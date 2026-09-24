#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LAUNCH="$ROOT/scripts/launch-nautilus-app"
STOP="$ROOT/scripts/stop-nautilus-app"
MANIFEST="$ROOT/android/macdesk-apps-shell/AndroidManifest.xml"
ACTIVITY="$ROOT/android/macdesk-apps-shell/src/com/macdesk/shell/NautilusActivity.java"

fail() { echo "FAIL: $*" >&2; exit 1; }

[ -x "$LAUNCH" ] || fail "launch-nautilus-app is not executable"
[ -x "$STOP" ] || fail "stop-nautilus-app is not executable"

grep -q 'MACDESK_APPS_DISPLAY:-:3' "$LAUNCH" || fail "dedicated :3 display missing"
grep -q 'dbus-run-session' "$LAUNCH" || fail "private D-Bus missing"
grep -q 'launch-nautilus' "$LAUNCH" || fail "canonical Nautilus launcher not reused"

if grep -Eq 'startxfce4|xfce4-session|plank|virgl_test_server_android' "$LAUNCH"; then
  fail "desktop/GPU stack leaked into Nautilus app launcher"
fi

grep -q 'android:resizeableActivity="true"' "$MANIFEST" || fail "DeX resize support missing"
grep -q 'android:taskAffinity="com.macdesk.shell.nautilus"' "$MANIFEST" || fail "Nautilus task affinity missing"
grep -q 'SurfaceView' "$ACTIVITY" || fail "Android surface host missing"
grep -q 'launch-nautilus-app' "$ACTIVITY" || fail "runtime launcher wiring missing"

if grep -q 'com.termux.x11/.MainActivity' "$ACTIVITY"; then
  fail "Nautilus task must not open the Termux:X11 desktop Activity"
fi

echo "NAUTILUS_APP_M0_CONTRACT=PASS"
