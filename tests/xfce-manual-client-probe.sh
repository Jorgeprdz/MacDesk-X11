#!/usr/bin/env bash
set -u

ROOT=/root/MacDesk-V6
client=${1:?client required}
mode=${2:?mode must be gpu-on or gpu-off}
log="$ROOT/logs/${client}-manual${mode/gpu-on/}.log"
[[ $mode == gpu-off ]] && log="$ROOT/logs/${client}-manual-gpu-off.log"
mkdir -p "$ROOT/logs" /tmp/runtime-macdesk-v6
chmod 700 /tmp/runtime-macdesk-v6
export DISPLAY=:2 HOME=/root USER=root XDG_RUNTIME_DIR=/tmp/runtime-macdesk-v6
export PULSE_SERVER=127.0.0.1:4713

if [[ $mode == gpu-on ]]; then
  . "$ROOT/config/gpu/env.sh"
else
  unset GALLIUM_DRIVER MESA_LOADER_DRIVER_OVERRIDE LIBGL_DRIVERS_PATH
  unset VK_ICD_FILENAMES VK_DRIVER_FILES MESA_VK_WSI_PRESENT_MODE
  unset ZINK_DESCRIPTORS MESA_GL_VERSION_OVERRIDE MACDESK_MESA_PREFIX
  unset LD_LIBRARY_PATH LIBGL_ALWAYS_SOFTWARE VTEST_SOCKET_NAME
  export LIBGL_ALWAYS_SOFTWARE=1
fi

{
  printf 'TEST=%s MODE=%s\n' "$client" "$mode"
  for name in DISPLAY HOME USER LOGNAME PATH TMPDIR XDG_RUNTIME_DIR \
    XDG_CONFIG_HOME XDG_CACHE_HOME DBUS_SESSION_BUS_ADDRESS PULSE_SERVER \
    GALLIUM_DRIVER MESA_LOADER_DRIVER_OVERRIDE LIBGL_DRIVERS_PATH \
    VK_ICD_FILENAMES VK_DRIVER_FILES MESA_VK_WSI_PRESENT_MODE ZINK_DESCRIPTORS; do
    if [[ -v $name ]]; then printf 'ENV %s=%s\n' "$name" "${!name}"
    else printf 'ENV %s=<UNSET>\n' "$name"; fi
  done
  printf '\n--- executable and linked libraries ---\n'
  command -v "$client" || true
  ldd "$(command -v "$client")" 2>&1 || true
  printf '\n--- start ---\n'
} >"$log" 2>&1

exec 3>>"$log"
if [[ $client == xfwm4 ]]; then
  "$client" --replace >>"$log" 2>&1 &
else
  "$client" >>"$log" 2>&1 &
fi
pid=$!
sleep 2
if kill -0 "$pid" 2>/dev/null; then
  printf 'OBSERVED=ALIVE PID=%s\n' "$pid" >&3
else
  wait "$pid"; rc=$?
  printf 'OBSERVED=EXITED EXIT_CODE=%s\n' "$rc" >&3
  exit "$rc"
fi

if [[ $client == xfwm4 ]]; then
  /usr/bin/wmctrl -m >>"$log" 2>&1; printf 'WMCTRL_EXIT=%s\n' "$?" >&3
  /usr/bin/xprop -root _NET_SUPPORTING_WM_CHECK >>"$log" 2>&1
  printf 'XPROP_EXIT=%s\n' "$?" >&3
else
  /usr/bin/xwininfo -root -tree >>"$log" 2>&1
  printf 'XWININFO_EXIT=%s\n' "$?" >&3
fi

kill -TERM "$pid" 2>/dev/null || true
wait "$pid"; rc=$?
printf 'EXIT_AFTER_TEST_SIGNAL=%s\n' "$rc" >&3
