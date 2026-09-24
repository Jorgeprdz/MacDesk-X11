#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

BASE="$(cd "$(dirname "$0")" && pwd)"
BUILD="$BASE/build"
SDK="$BASE/sdk/android.jar"
KEYSTORE="$BASE/signing/macdesk-apps.keystore"
UNSIGNED="$BUILD/MacDesk-Files-M0-unsigned.apk"
ALIGNED="$BUILD/MacDesk-Files-M0-aligned.apk"
OUTPUT="$BUILD/MacDesk-Files-M0.apk"

[ -f "$SDK" ] || { echo 'ANDROID_JAR=FAIL'; exit 1; }

rm -rf "$BUILD/classes" "$BUILD/dex" "$BUILD/gen"
mkdir -p "$BUILD/classes" "$BUILD/dex" "$BUILD/gen" "$BASE/signing"

aapt package -f -m \
  -J "$BUILD/gen" \
  -M "$BASE/AndroidManifest.xml" \
  -S "$BASE/res" \
  -I "$SDK" \
  -F "$BUILD/resources.ap_"

javac --release 8 -encoding UTF-8 \
  -classpath "$SDK" \
  -d "$BUILD/classes" \
  "$BUILD/gen/com/macdesk/shell/R.java" \
  "$BASE/src/com/macdesk/shell/NautilusActivity.java"

mapfile -t classes < <(find "$BUILD/classes" -type f -name '*.class' -print)
d8 --min-api 26 --lib "$SDK" --output "$BUILD/dex" "${classes[@]}"

cp "$BUILD/resources.ap_" "$UNSIGNED"
zip -qj "$UNSIGNED" "$BUILD/dex/classes.dex"
zipalign -f 4 "$UNSIGNED" "$ALIGNED"

if [ ! -f "$KEYSTORE" ]; then
  keytool -genkeypair -noprompt \
    -keystore "$KEYSTORE" \
    -storepass android \
    -keypass android \
    -alias macdesk-apps \
    -keyalg RSA -keysize 2048 -validity 10000 \
    -dname 'CN=MacDesk Apps, OU=Local, O=MacDesk, C=MX' >/dev/null
  chmod 600 "$KEYSTORE"
fi

apksigner sign \
  --ks "$KEYSTORE" \
  --ks-key-alias macdesk-apps \
  --ks-pass pass:android \
  --key-pass pass:android \
  --out "$OUTPUT" \
  "$ALIGNED"

apksigner verify --verbose "$OUTPUT" >/dev/null
echo 'MACDESK_FILES_M0_APK=PASS'
echo "APK=$OUTPUT"
