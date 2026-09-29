#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd -- "$(dirname -- "$0")/.." && pwd)
launcher="$ROOT/scripts/macdesk-xfce-session"
session_start="$ROOT/scripts/session-start"
safe_graphics="$ROOT/config/gpu/profiles/safe-graphics.sh"
fail() { printf 'FAIL: %s\n' "$*" >&2; exit 1; }

[[ -x $launcher ]] || fail "missing executable session environment launcher"
[[ -f $safe_graphics ]] || fail "missing SAFE_GRAPHICS profile"
for name in HOME USER LOGNAME TMPDIR XDG_RUNTIME_DIR XDG_CONFIG_HOME XDG_CACHE_HOME XDG_DATA_HOME DISPLAY MACDESK_ROOT PATH; do
  grep -Eq "export[[:space:]]+$name=" "$launcher" || fail "$name is not explicitly exported"
done
runtime_line=$(grep -n 'XDG_RUNTIME_DIR=' "$launcher" | head -1 | cut -d: -f1)
mkdir_line=$(grep -n 'mkdir -p.*XDG_CONFIG_HOME' "$launcher" | head -1 | cut -d: -f1)
chmod_line=$(grep -n 'chmod 700.*XDG_RUNTIME_DIR' "$launcher" | head -1 | cut -d: -f1)
dbus_line=$(grep -n 'exec /usr/bin/dbus-run-session' "$launcher" | head -1 | cut -d: -f1)
[[ -n $runtime_line && -n $mkdir_line && -n $chmod_line && -n $dbus_line ]] || fail "runtime setup or D-Bus creation missing"
(( runtime_line < mkdir_line && mkdir_line < chmod_line && chmod_line < dbus_line )) || fail "runtime must exist with 0700 permissions before D-Bus"
[[ $(grep -c 'exec /usr/bin/dbus-run-session' "$launcher") -eq 1 ]] || fail "launcher must create exactly one session bus"
! grep -Eq '(^|[[:space:]])dbus-run-session([[:space:]]|$)' "$session_start" || fail "session-start must reuse launcher bus"
! grep -Eq '(^|[[:space:]])dbus-run-session([[:space:]]|$)' "$ROOT/scripts/plank-geometry-guard" || fail "Plank guard must reuse XFCE session bus"
! grep -Eq '^[[:space:]]*(\.|source)[[:space:]]+.*config/gpu/env.sh' "$ROOT/scripts/macdesk" || fail "normal launcher must not source legacy GPU profile"
! grep -q 'GALLIUM_DRIVER=zink\|MESA_LOADER_DRIVER_OVERRIDE=zink\|VK_DRIVER_FILES=' "$ROOT/scripts/macdesk" || fail "normal launcher must not force Zink/Vulkan"
grep -q 'MACDESK_GPU_PROFILE=SAFE_FALLBACK' "$safe_graphics" || fail "SAFE_GRAPHICS state is not recorded"
! grep -q '/root/MacDesk-V6' "$launcher" "$session_start" "$ROOT/scripts/plank-geometry-guard" "$ROOT/scripts/session-health-supervisor" || fail "session scripts must derive MACDESK_ROOT"
for state in X11_SERVER DBUS_SESSION XFCONF XFCE_SESSION XFWM XFCE_PANEL XFSETTINGS XFDESKTOP GPU_PROFILE MACDESK_ROOT PATHS; do
  grep -q "${state}=" "$session_start" || fail "session health check omits $state"
done
printf 'XFCE_STARTUP_CONTRACT=PASS\n'
