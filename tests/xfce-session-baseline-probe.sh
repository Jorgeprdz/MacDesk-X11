#!/usr/bin/env bash
set -u

ROOT=/root/MacDesk-V6
if [[ ${1-} == inner ]]; then
  profile=$2
  gpu=$3
  log="$ROOT/logs/xfce-session-${profile}-${gpu}.log"
  config_home="${XDG_CONFIG_HOME:-$HOME/.config}"
  {
    printf 'PROFILE=%s GPU=%s\n' "$profile" "$gpu"
    for name in DISPLAY HOME USER LOGNAME PATH TMPDIR XDG_RUNTIME_DIR \
      XDG_CONFIG_HOME XDG_CACHE_HOME DBUS_SESSION_BUS_ADDRESS PULSE_SERVER \
      GALLIUM_DRIVER MESA_LOADER_DRIVER_OVERRIDE LIBGL_DRIVERS_PATH \
      VK_ICD_FILENAMES VK_DRIVER_FILES MESA_VK_WSI_PRESENT_MODE ZINK_DESCRIPTORS; do
      if [[ -v $name ]]; then printf 'ENV %s=%s\n' "$name" "${!name}"
      else printf 'ENV %s=<UNSET>\n' "$name"; fi
    done
    printf '\n--- saved session/config files ---\n'
    /usr/bin/find "$HOME/.cache/sessions" "$config_home/xfce4" \
      "$HOME/.config/xfce4" -maxdepth 4 -type f -print 2>&1 || true
    printf '\n--- process baseline ---\n'
    /usr/bin/ps -eo pid,ppid,stat,comm,args
  } >"$log" 2>&1

  baseline=""
  for name in xfce4-session xfwm4 xfce4-panel xfsettingsd xfdesktop xfconfd; do
    pids="$(/usr/bin/pgrep -x "$name" 2>/dev/null || true)"
    baseline+=" $pids"
  done
  exec 3>>"$log"
  /usr/bin/startxfce4 >>"$log" 2>&1 &
  launcher=$!
  sleep 5
  printf '\n--- startup status ---\n' >&3
  printf 'STARTXFCE4_PID=%s ALIVE=' "$launcher" >&3
  if kill -0 "$launcher" 2>/dev/null; then printf 'YES\n' >&3
  else wait "$launcher"; printf 'NO EXIT_CODE=%s\n' "$?" >&3; fi
  for name in xfce4-session xfwm4 xfce4-panel xfsettingsd xfdesktop xfconfd; do
    pids="$(/usr/bin/pgrep -x "$name" 2>/dev/null || true)"
    printf '%s_PIDS=%s\n' "$name" "${pids//$'\n'/,}" >&3
  done
  printf '\n--- relevant process tree ---\n' >&3
  /usr/bin/ps -eo pid,ppid,stat,comm,args | \
    /usr/bin/grep -E 'xfce4-session|xfwm4|xfce4-panel|xfsettingsd|xfdesktop|xfconfd|startxfce4|dbus-daemon' >&3 || true
  printf '\n--- WM check ---\n' >&3
  /usr/bin/wmctrl -m >>"$log" 2>&1; printf 'WMCTRL_EXIT=%s\n' "$?" >&3
  /usr/bin/xprop -root _NET_SUPPORTING_WM_CHECK >>"$log" 2>&1
  printf 'XPROP_EXIT=%s\n' "$?" >&3
  /usr/bin/xwininfo -root -tree >>"$log" 2>&1
  printf 'XWININFO_EXIT=%s\n' "$?" >&3

  if kill -0 "$launcher" 2>/dev/null; then kill -TERM "$launcher" 2>/dev/null || true; fi
  for name in xfce4-session xfwm4 xfce4-panel xfsettingsd xfdesktop xfconfd; do
    for pid in $(/usr/bin/pgrep -x "$name" 2>/dev/null || true); do
      case " $baseline " in *" $pid "*) continue;; esac
      kill -TERM "$pid" 2>/dev/null || true
    done
  done
  sleep 1
  for name in xfce4-session xfwm4 xfce4-panel xfsettingsd xfdesktop xfconfd; do
    for pid in $(/usr/bin/pgrep -x "$name" 2>/dev/null || true); do
      case " $baseline " in *" $pid "*) continue;; esac
      kill -KILL "$pid" 2>/dev/null || true
    done
  done
  wait "$launcher" 2>/dev/null || true
  exit 0
fi

profile=${1:?profile must be current or clean}
gpu=${2:?gpu must be on or off}
runtime="/tmp/runtime-macdesk-probe-${profile}-${gpu}"
mkdir -p "$runtime"
chmod 700 "$runtime"
export DISPLAY=:2 XDG_RUNTIME_DIR="$runtime" LANG=es_MX.UTF-8
export USER=root LOGNAME=root

if [[ $profile == clean ]]; then
  export HOME="/tmp/macdesk-xfce-clean-${gpu}/home"
  export XDG_CONFIG_HOME="/tmp/macdesk-xfce-clean-${gpu}/config"
  export XDG_CACHE_HOME="/tmp/macdesk-xfce-clean-${gpu}/cache"
  mkdir -p "$HOME" "$XDG_CONFIG_HOME" "$XDG_CACHE_HOME"
else
  export HOME=/root
  unset XDG_CONFIG_HOME XDG_CACHE_HOME
fi

if [[ $gpu == on ]]; then
  . "$ROOT/config/gpu/env.sh"
else
  unset GALLIUM_DRIVER MESA_LOADER_DRIVER_OVERRIDE LIBGL_DRIVERS_PATH
  unset VK_ICD_FILENAMES VK_DRIVER_FILES MESA_VK_WSI_PRESENT_MODE
  unset ZINK_DESCRIPTORS MESA_GL_VERSION_OVERRIDE MACDESK_MESA_PREFIX
  unset LD_LIBRARY_PATH LIBGL_ALWAYS_SOFTWARE VTEST_SOCKET_NAME
  export LIBGL_ALWAYS_SOFTWARE=1
fi

exec /usr/bin/dbus-run-session -- /usr/bin/bash "$0" inner "$profile" "$gpu"
