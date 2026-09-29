#!/usr/bin/env bash
set -u
ROOT=/root/MacDesk-V6
export DISPLAY=:2
export XDG_RUNTIME_DIR=/tmp/runtime-macdesk-v6
export LANG=es_MX.UTF-8
. "$ROOT/config/gpu/env.sh"
exec /usr/bin/dbus-run-session -- /usr/bin/bash "$ROOT/tests/capture-xfce-env.sh" \
  >"$ROOT/logs/xfce-environment-audit.log" 2>&1
