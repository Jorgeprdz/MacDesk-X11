#!/usr/bin/env bash
set -euo pipefail

# Run this file on an external computer with Android platform-tools installed.
# It intentionally cannot run from Termux: uninstalling the last sharedUid X11
# build may terminate every process using the old UID.

EXPECTED_SHA256=cc16c4f4108604aa3cb6ea5768871146aadcc1908bed46a7b5cc3d3449b179db
EXPECTED_VERSION=1.03.01-f68cd36-21.08.26
SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
APK="${1:-$SCRIPT_DIR/termux-x11-universal-debug.apk}"

fail() { printf 'MIGRATION=FAIL\nREASON=%s\n' "$*" >&2; exit 1; }

command -v adb >/dev/null 2>&1 || fail 'adb is not installed on the external computer'
[ -f "$APK" ] || fail "standalone APK not found: $APK"
[ "$(adb get-state 2>/dev/null || true)" = device ] || fail 'no authorized external ADB device'

if command -v sha256sum >/dev/null 2>&1; then
  apk_sha="$(sha256sum "$APK" | awk '{print $1}')"
elif command -v shasum >/dev/null 2>&1; then
  apk_sha="$(shasum -a 256 "$APK" | awk '{print $1}')"
else
  fail 'sha256sum or shasum is required'
fi
[ "$apk_sha" = "$EXPECTED_SHA256" ] || fail "APK SHA-256 mismatch: $apk_sha"

package_uid() {
  local package="$1"
  adb shell pm list packages -U "$package" 2>/dev/null \
    | tr -d '\r' \
    | awk -v name="package:$package" \
      '$1 == name { sub(/^uid:/, "", $2); print $2; exit }'
}

termux_uid_before="$(package_uid com.termux)"
x11_uid_before="$(package_uid com.termux.x11)"
[ -n "$termux_uid_before" ] || fail 'Termux is not installed'
[ -n "$x11_uid_before" ] || fail 'Termux:X11 is not installed'
[ "$termux_uid_before" = "$x11_uid_before" ] || fail 'preflight is no longer the expected sharedUid state'

adb shell "run-as com.termux test -d files/home/MacDesk-V6" \
  || fail 'MacDesk V6 is not readable before migration'
adb shell "run-as com.termux test -d files/usr/var/lib/proot-distro/containers/debian/rootfs" \
  || fail 'Debian PRoot is not readable before migration'

printf 'TERMUX_UID_BEFORE=%s\nTERMUX_X11_UID_BEFORE=%s\n' \
  "$termux_uid_before" "$x11_uid_before"
printf 'APK_SHA256=%s\n' "$apk_sha"

# No -k: private data created under the shared UID must not cross into the new
# sandbox.  This is the one operation expected to terminate the old Termux
# process; execution continues because this script is external.
adb uninstall com.termux.x11 | grep -q Success || fail 'adb uninstall com.termux.x11 failed'
adb install "$APK" | grep -q Success || fail 'standalone APK installation failed'

termux_uid_after="$(package_uid com.termux)"
x11_uid_after="$(package_uid com.termux.x11)"
[ "$termux_uid_after" = "$termux_uid_before" ] || fail 'Termux UID changed unexpectedly'
[ -n "$x11_uid_after" ] || fail 'standalone X11 has no UID'
[ "$termux_uid_after" != "$x11_uid_after" ] || fail 'X11 still shares the Termux UID'

installed_version="$(adb shell dumpsys package com.termux.x11 \
  | sed -n 's/^[[:space:]]*versionName=//p' | head -1 | tr -d '\r')"
[ "$installed_version" = "$EXPECTED_VERSION" ] \
  || fail "installed version mismatch: $installed_version"
adb shell "run-as com.termux test -d files/home/MacDesk-V6" \
  || fail 'MacDesk V6 was not preserved'
adb shell "run-as com.termux test -d files/usr/var/lib/proot-distro/containers/debian/rootfs" \
  || fail 'Debian PRoot was not preserved'

dex_display="$(adb shell dumpsys accessibility \
  | sed -n 's/.*Enabled features of Display \[\([1-9][0-9]*\)\].*/\1/p' \
  | head -1 | tr -d '\r')"
[ -n "$dex_display" ] || fail 'active Samsung DeX display not found'
adb shell am start --user 0 --display "$dex_display" \
  -n com.termux.x11/.MainActivity >/dev/null
sleep 2

adb shell am broadcast --user 0 --receiver-foreground \
  -a com.termux.x11.CHANGE_PREFERENCE \
  -n 'com.termux.x11/.LoriePreferences$Receiver' \
  --es dexMetaKeyCapture false \
  --es enableAccessibilityServiceAutomatically false \
  --es pointerCapture false \
  --es preferScancodes true \
  --es hardwareKbdScancodesWorkaround true \
  --es filterOutWinkey false \
  --es pauseKeyInterceptingWithEsc true \
  --es enforceCharBasedInput false \
  --es clipboardEnable true >/dev/null

# Remove only Termux:X11's interceptor, preserving every other service.
services="$(adb shell settings get secure enabled_accessibility_services | tr -d '\r')"
case "$services" in null) services='' ;; esac
filtered="$(printf '%s' "$services" | tr ':' '\n' \
  | grep -v -E '^com\.termux\.x11/(com\.termux\.x11)?\.utils\.KeyInterceptor$' \
  | awk 'NF { if (out) out=out ":" $0; else out=$0 } END { print out }')"
if [ "$filtered" != "$services" ]; then
  if [ -n "$filtered" ]; then
    adb shell settings put secure enabled_accessibility_services "$filtered"
  else
    adb shell settings delete secure enabled_accessibility_services >/dev/null
  fi
fi
adb shell pm revoke com.termux.x11 android.permission.WRITE_SECURE_SETTINGS \
  >/dev/null 2>&1 || true
adb shell cmd deviceidle whitelist +com.termux >/dev/null
adb shell cmd deviceidle whitelist +com.termux.x11 >/dev/null
adb shell cmd appops set com.termux RUN_ANY_IN_BACKGROUND allow
adb shell cmd appops set com.termux.x11 RUN_ANY_IN_BACKGROUND allow
adb shell cmd appops set com.termux RUN_IN_BACKGROUND allow
adb shell cmd appops set com.termux.x11 RUN_IN_BACKGROUND allow

services_after="$(adb shell settings get secure enabled_accessibility_services | tr -d '\r')"
case ":$services_after:" in
  *:com.termux.x11/.utils.KeyInterceptor:*|*:com.termux.x11/com.termux.x11.utils.KeyInterceptor:*)
    fail 'KeyInterceptor is still enabled' ;;
esac
if adb shell dumpsys package com.termux.x11 \
  | grep -q 'android.permission.WRITE_SECURE_SETTINGS: granted=true'; then
  fail 'WRITE_SECURE_SETTINGS is still granted'
fi

# Prove package isolation: stopping X11 must leave the Termux process intact.
adb shell am start --user 0 -n com.termux/.app.TermuxActivity >/dev/null
sleep 2
termux_pid_before_stop="$(adb shell pidof com.termux | tr -d '\r')"
[ -n "$termux_pid_before_stop" ] || fail 'Termux did not start for isolation test'
adb shell am force-stop --user 0 com.termux.x11
sleep 1
termux_pid_after_stop="$(adb shell pidof com.termux | tr -d '\r')"
[ "$termux_pid_after_stop" = "$termux_pid_before_stop" ] \
  || fail 'Termux did not survive X11 force-stop'
adb shell am start --user 0 --display "$dex_display" \
  -n com.termux.x11/.MainActivity >/dev/null

printf 'TERMUX_UID_AFTER=%s\nTERMUX_X11_UID_AFTER=%s\n' \
  "$termux_uid_after" "$x11_uid_after"
printf 'UID_ISOLATION=PASS\nTERMUX_DATA_PRESERVED=PASS\nDEBIAN_PRESERVED=PASS\n'
printf 'TERMUX_SURVIVES_X11_FORCE_STOP=PASS\nKEYINTERCEPTOR=DISABLED\n'
printf 'WRITE_SECURE_SETTINGS=NOT_GRANTED\nDEX_DISPLAY=%s\nMIGRATION=PASS\n' "$dex_display"
