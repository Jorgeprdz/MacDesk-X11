#!/usr/bin/env bash
set -euo pipefail

archive="${MACDESK_RESTORE_ARCHIVE:-/sdcard/emulated/0/MacDesk-V6.tar.gz}"
current_root="$HOME/MacDesk-V6"
log_dir="$HOME/.local/state/macdesk"
mkdir -p "$log_dir"
log="$log_dir/archive-restore.log"
exec > >(tee -a "$log") 2>&1

fail() { printf 'RESTORE_ERROR: %s\n' "$*" >&2; exit 1; }
[[ -r "$archive" ]] || fail "archive is not readable: $archive"
command -v tar >/dev/null 2>&1 || fail 'tar is unavailable'
command -v proot-distro >/dev/null 2>&1 || fail 'proot-distro is unavailable'

members=$(tar -tzf "$archive") || fail 'archive is corrupt or incomplete'
while IFS= read -r member; do
  [[ "$member" != /* ]] || fail "absolute archive path rejected: $member"
  [[ ! "$member" =~ (^|/)\.\.(/|$) ]] || fail "parent traversal rejected: $member"
done <<<"$members"
for required in 'MacDesk-V6/.git/HEAD' 'MacDesk-V6/scripts/macdesk' \
  'MacDesk-V6/scripts/macdesk-xfce-session' 'MacDesk-V6/scripts/session-start'; do
  grep -Fxq "$required" <<<"$members" || fail "archive is missing $required"
done

stage="$HOME/.macdesk-restore-stage-$$"
backup="$HOME/MacDesk-V6.pre-recovery.$(date +%Y%m%d-%H%M%S)"
[[ ! -e "$stage" ]] || fail "staging path already exists: $stage"
mkdir -m 700 "$stage"
if ! tar -xzf "$archive" -C "$stage"; then
  printf 'Extraction failed; staged files remain at %s\n' "$stage" >&2
  exit 1
fi
new_root="$stage/MacDesk-V6"
[[ -d "$new_root/.git" && -x "$new_root/scripts/macdesk" ]] || \
  fail 'extracted checkout failed validation'

# Stop only the invalid PRoot session recorded by this checkout. First try its
# leader, then validate that the whole process group contains only MacDesk
# session infrastructure before signaling that group.
pid_file="$current_root/state/guest.pid"
if [[ -r "$pid_file" ]]; then
  old_pid=$(cat "$pid_file")
  if [[ "$old_pid" =~ ^[0-9]+$ ]] && kill -0 "$old_pid" 2>/dev/null; then
    if [[ -r "$current_root/state/session-check.env" ]] \
      && grep -qx 'DBUS_SESSION=PASS' "$current_root/state/session-check.env" \
      && grep -qx 'XFCONF=PASS' "$current_root/state/session-check.env" \
      && grep -qx 'XFWM=PASS' "$current_root/state/session-check.env" \
      && grep -qx 'XFCE_PANEL=PASS' "$current_root/state/session-check.env"; then
      fail 'current MacDesk session reports healthy; it was left untouched'
    fi
    old_cmd=$(tr '\0' ' ' <"/proc/$old_pid/cmdline" 2>/dev/null || true)
    guest_root="/root/$(basename "$current_root")"
    if [[ "$old_cmd" != *'--kill-on-exit'* ]] || \
      { [[ "$old_cmd" != *"$current_root"* ]] \
        && [[ "$old_cmd" != *"$guest_root/scripts/"* ]] \
        && [[ "$old_cmd" != *"$guest_root/config/gpu/env.sh"* ]]; }; then
      fail "recorded PID $old_pid is not the MacDesk PRoot session; left it untouched"
    fi
    read -r _ _ _ _ old_pgrp <"/proc/$old_pid/stat"
    [[ "$old_pgrp" == "$old_pid" ]] || fail "PID $old_pid is not its own session process-group leader"
    self_pgrp=$(awk '{print $5}' "/proc/$$/stat")
    [[ "$self_pgrp" != "$old_pgrp" ]] || fail 'run this restore command from Termux, not inside the MacDesk Debian session'

    printf 'Stopping invalid MacDesk PRoot session PID=%s (graceful signal)...\n' "$old_pid"
    kill -TERM "$old_pid"
    stopped=false
    for second in 1 2 3; do
      if ! kill -0 "$old_pid" 2>/dev/null; then stopped=true; break; fi
      printf 'Waiting for MacDesk session to stop (%s/3 s)...\n' "$second"
      sleep 1
    done

    if [[ "$stopped" != true ]] && kill -0 "$old_pid" 2>/dev/null; then
      printf 'PRoot did not exit; checking its process group before cleanup...\n'
      unknown=''
      for stat_file in /proc/[0-9]*/stat; do
        [[ -r "$stat_file" ]] || continue
        read -r proc_pid _ proc_state _ proc_group <"$stat_file" || continue
        [[ "$proc_group" == "$old_pgrp" && "$proc_state" != Z ]] || continue
        proc_pid="${stat_file#/proc/}"; proc_pid="${proc_pid%/stat}"
        proc_cmd=$(tr '\0' ' ' <"/proc/$proc_pid/cmdline" 2>/dev/null || true)
        case "$proc_cmd" in
          *'proot --kill-on-exit'*|*'proot --shm-helper'*|*'dbus-run-session'*|*'dbus-daemon --nofork'*|*'xfce4-session'*|*'xfwm4'*|*'xfce4-panel'*|*'xfsettingsd'*|*'xfdesktop'*|*'xfconfd'*|*'plank'*|*'gvfsd'*|*'dconf-service'*|*'bamfdaemon'*|*'session-health-supervisor'*|*'input-guard'*|*'plank-geometry-guard'*|*'xfconf-query'*|*'gsettings'*|*'setxkbmap'*|*'dbus-launch'*|*'sleep '*|*'tr '*|*'mv '*|*'sh /root/MacDesk-V6/scripts/'*|*'/bin/bash -c /usr/bin/bash -lc'* ) ;;
          *) unknown+=" PID=$proc_pid:$proc_cmd" ;;
        esac
      done
      [[ -z "$unknown" ]] || fail "unrelated/user processes share the MacDesk group; left them untouched:$unknown"
      printf 'Validated MacDesk-only process group %s; sending graceful group signal...\n' "$old_pgrp"
      kill -TERM -- "-$old_pgrp"
      stopped=false
      for second in 1 2 3 4 5; do
        if ! kill -0 "$old_pid" 2>/dev/null; then stopped=true; break; fi
        printf 'Waiting for MacDesk process group to stop (%s/5 s)...\n' "$second"
        sleep 1
      done
    fi
    [[ "$stopped" == true ]] || fail "MacDesk session PID $old_pid did not stop; checkout was not replaced"
  fi
fi

if [[ -e "$current_root" ]]; then
  mv "$current_root" "$backup"
fi
if ! mv "$new_root" "$current_root"; then
  [[ ! -e "$backup" ]] || mv "$backup" "$current_root"
  fail 'could not install restored checkout; previous repo was restored'
fi
rmdir "$stage" 2>/dev/null || true
printf 'Repository restored to %s\nBackup: %s\n' "$current_root" "$backup"
printf 'Starting the normal MacDesk launcher...\n'
exec bash "$current_root/scripts/macdesk"
