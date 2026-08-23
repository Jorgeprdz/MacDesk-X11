#!/data/data/com.termux/files/usr/bin/bash
set -u

. "$HOME/MacDesk-V6/scripts/lib/android-x11.sh"
component=com.termux.x11/com.termux.x11.utils.KeyInterceptor
status=0
prefs_xml="$(x11_read_preferences || true)"

pref_value() {
  local key="$1"
  printf '%s\n' "$prefs_xml" \
    | sed -n "s/.*<boolean name=\"$key\" value=\"\([^\"]*\)\".*/\1/p" \
    | tail -1
}

report_pref() {
  local label="$1" key="$2" expected="$3" value
  value="$(pref_value "$key")"
  if [ "$value" = "$expected" ]; then
    printf '%s: %s\n' "$label" "$(printf '%s' "$value" | tr '[:lower:]' '[:upper:]')"
  else
    printf '%s: %s (EXPECTED %s)\n' "$label" "${value:-UNKNOWN}" "$expected"
    status=1
  fi
}

echo 'MACDESK DEX KEYBOARD'
echo

if ! x11_adb_ready; then
  echo 'KeyInterceptor: UNKNOWN (ADB unavailable)'
  adb_ready=false
  status=1
else
  adb_ready=true
  services="$($ADB shell settings get secure enabled_accessibility_services 2>/dev/null | tr -d '\r')"
  case ":$services:" in
    *":$component:"*) echo 'KeyInterceptor: ENABLED'; status=1 ;;
    *) echo 'KeyInterceptor: DISABLED' ;;
  esac
  # Samsung may assign a new external-display id after a DeX reconnect (this
  # device has used both 8 and 9).  Display 0 is the phone; inspect the active
  # non-zero accessibility display instead of hard-coding a stale DeX id.
  dex_filter="$($ADB shell dumpsys accessibility 2>/dev/null \
    | grep 'Enabled features of Display' \
    | grep -v 'Display \[0\]' \
    | head -1 || true)"
  dex_display="$(printf '%s\n' "$dex_filter" | sed -n 's/.*Display \[\([0-9][0-9]*\)\].*/\1/p')"
  case "$dex_filter" in
    *KeyboardInterceptor*) echo "Android DeX keyboard filter: ACTIVE (Display ${dex_display:-UNKNOWN})"; status=1 ;;
    *'Enabled features of Display'*) echo "Android DeX keyboard filter: NONE (Display $dex_display)" ;;
    *) echo 'Android DeX keyboard filter: UNKNOWN'; status=1 ;;
  esac
fi

report_pref 'Auto Accessibility' enableAccessibilityServiceAutomatically false
report_pref 'DeX Meta Capture' dexMetaKeyCapture false
report_pref 'Pointer Capture' pointerCapture false
report_pref 'Prefer Scancodes' preferScancodes true
report_pref 'Hardware Keyboard Workaround' hardwareKbdScancodesWorkaround true
report_pref 'Pause Intercepting With Esc' pauseKeyInterceptingWithEsc true
report_pref 'Character Based Input' enforceCharBasedInput false
report_pref 'Clipboard' clipboardEnable true

if [ "$adb_ready" = true ]; then
  if "$ADB" shell dumpsys package com.termux.x11 2>/dev/null | grep -q 'android.permission.WRITE_SECURE_SETTINGS: granted=true'; then
    echo 'WRITE_SECURE_SETTINGS: GRANTED'
    status=1
  else
    echo 'WRITE_SECURE_SETTINGS: NOT GRANTED'
  fi
else
  echo 'WRITE_SECURE_SETTINGS: UNKNOWN'
fi

if [ "$status" -eq 0 ]; then
  echo
  echo 'ALT-TAB CONFIG: PASS'
else
  echo
  echo 'ALT-TAB CONFIG: FAIL'
fi

exit "$status"
