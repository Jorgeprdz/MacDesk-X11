#!/data/data/com.termux/files/usr/bin/bash

# Shared Android/Termux:X11 helpers.  Every function is safe with the current
# sharedUid APK and automatically switches to sandbox-safe interfaces after
# the standalone APK is installed.

ADB=${ADB:-adb}
X11_PACKAGE=com.termux.x11
TERMUX_PACKAGE=com.termux
X11_PREFS=/data/data/com.termux.x11/shared_prefs/com.termux.x11_preferences.xml

x11_adb_ready() {
  command -v "$ADB" >/dev/null 2>&1 && "$ADB" get-state >/dev/null 2>&1
}

x11_package_uid() {
  local package="$1"
  x11_adb_ready || return 1
  "$ADB" shell pm list packages -U "$package" 2>/dev/null \
    | tr -d '\r' \
    | awk -v name="package:$package" \
      '$1 == name { sub(/^uid:/, "", $2); print $2; exit }'
}

x11_uids_are_isolated() {
  local termux_uid x11_uid
  termux_uid="$(x11_package_uid "$TERMUX_PACKAGE" || true)"
  x11_uid="$(x11_package_uid "$X11_PACKAGE" || true)"
  [ -n "$termux_uid" ] && [ -n "$x11_uid" ] && [ "$termux_uid" != "$x11_uid" ]
}

x11_read_preferences() {
  if [ -r "$X11_PREFS" ]; then
    cat "$X11_PREFS"
  elif x11_adb_ready; then
    "$ADB" shell "run-as $X11_PACKAGE cat shared_prefs/com.termux.x11_preferences.xml" \
      2>/dev/null | tr -d '\r'
  else
    return 1
  fi
}

x11_apply_keyboard_preferences() {
  local receiver_output
  if [ -r "$X11_PREFS" ]; then
    # The sharedUid build has previously raced and killed Termux when the
    # app_process preference helper was used.  Keep its proven direct intent.
    receiver_output="$(/system/bin/am broadcast --user 0 --receiver-foreground \
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
      --es clipboardEnable true 2>&1)" || {
        printf '%s\n' "$receiver_output" >&2
        return 1
      }
  else
    # Standalone has a different sandbox.  The companion's official helper
    # crosses that boundary without direct access to X11 private files.
    termux-x11-preference \
      dexMetaKeyCapture:false \
      enableAccessibilityServiceAutomatically:false \
      pointerCapture:false \
      preferScancodes:true \
      hardwareKbdScancodesWorkaround:true \
      filterOutWinkey:false \
      pauseKeyInterceptingWithEsc:true \
      enforceCharBasedInput:false \
      clipboardEnable:true >/dev/null
  fi
}

x11_detect_dex_display() {
  local display
  if [ -n "${DEX_DISPLAY_ID:-}" ]; then
    printf '%s\n' "$DEX_DISPLAY_ID"
    return 0
  fi
  x11_adb_ready || return 1
  display="$("$ADB" shell dumpsys accessibility 2>/dev/null \
    | sed -n 's/.*Enabled features of Display \[\([1-9][0-9]*\)\].*/\1/p' \
    | head -1 | tr -d '\r')"
  [ -n "$display" ] || return 1
  printf '%s\n' "$display"
}

x11_focus_activity() {
  local display
  display="$(x11_detect_dex_display || true)"
  if [ -n "$display" ] && x11_adb_ready; then
    "$ADB" shell am start --user 0 --display "$display" \
      -n "$X11_PACKAGE/.MainActivity" >/dev/null 2>&1
  else
    /system/bin/am start --user 0 -n "$X11_PACKAGE/.MainActivity" >/dev/null 2>&1
  fi
}

x11_android_pid() {
  local package="$1"
  x11_adb_ready || return 1
  "$ADB" shell pidof "$package" 2>/dev/null | tr -d '\r'
}
