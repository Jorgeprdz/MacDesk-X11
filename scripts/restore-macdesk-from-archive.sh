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

# Stop only the PRoot session recorded by this checkout, and only when its
# command line proves it belongs to MacDesk. --kill-on-exit then ends that
# session's children without touching Termux:X11 or unrelated processes.
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
    printf 'Stopping invalid MacDesk PRoot session PID=%s\n' "$old_pid"
    kill -TERM "$old_pid"
    stopped=false
    for _ in $(seq 1 100); do
      if ! kill -0 "$old_pid" 2>/dev/null; then stopped=true; break; fi
      sleep .1
    done
    [[ "$stopped" == true ]] || fail "MacDesk session PID $old_pid did not stop cleanly"
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
