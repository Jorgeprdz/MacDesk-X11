#!/usr/bin/env bash
set -u
for socket in /tmp/dbus-*; do
  [[ -S $socket ]] || continue
  printf '\nBUS=%s\n' "$socket"
  timeout 1 /usr/bin/dbus-send --address="unix:path=$socket" \
    --type=method_call --print-reply --dest=org.freedesktop.DBus \
    / org.freedesktop.DBus.ListNames 2>&1 | head -n 8
done
