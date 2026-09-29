#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd -- "$(dirname -- "$0")/.." && pwd)
RESTORE="$ROOT/scripts/restore-macdesk-from-archive.sh"
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
fail() { printf 'FAIL: %s\n' "$*" >&2; exit 1; }

home="$tmp/home"
mkdir -p "$home/MacDesk-V6/scripts" "$tmp/archive-root/MacDesk-V6/scripts" \
  "$tmp/archive-root/MacDesk-V6/.git"
printf 'previous installation\n' >"$home/MacDesk-V6/KEEP-ME"
printf 'ref: refs/heads/test\n' >"$tmp/archive-root/MacDesk-V6/.git/HEAD"
cat >"$tmp/archive-root/MacDesk-V6/scripts/macdesk" <<'LAUNCHER'
printf 'LAUNCHER_STARTED\n' >>"$MACDESK_TEST_MARKER"
LAUNCHER
printf '#!/bin/sh\nexit 0\n' >"$tmp/archive-root/MacDesk-V6/scripts/session-start"
cat >"$tmp/archive-root/MacDesk-V6/scripts/macdesk-xfce-session" <<'SESSION'
#!/usr/bin/env bash
exit 0
SESSION
archive="$tmp/MacDesk-V6.tar.gz"
chmod +x "$tmp/archive-root/MacDesk-V6/scripts/macdesk"
tar -czf "$archive" -C "$tmp/archive-root" MacDesk-V6
marker="$tmp/launcher-started"
mkdir -p "$tmp/bin"
printf '#!/bin/sh\nexit 0\n' >"$tmp/bin/proot-distro"
chmod +x "$tmp/bin/proot-distro"

[[ -x $RESTORE ]] || fail "restore script missing or not executable"
PATH="$tmp/bin:$PATH" HOME="$home" MACDESK_RESTORE_ARCHIVE="$archive" MACDESK_TEST_MARKER="$marker" \
  bash "$RESTORE" || fail "restore operation failed"
[[ -f "$home/MacDesk-V6/.git/HEAD" ]] || fail "repository was not restored"
find "$home" -maxdepth 2 -name KEEP-ME -print -quit | grep -q . || fail "old repository was not backed up"
[[ -f $marker ]] || fail "normal launcher was not invoked"

bad="$tmp/not-a-tar.gz"
printf 'invalid archive' >"$bad"
PATH="$tmp/bin:$PATH" HOME="$home" MACDESK_RESTORE_ARCHIVE="$bad" MACDESK_TEST_MARKER="$marker" \
  bash "$RESTORE" >/dev/null 2>&1 && fail "invalid archive was accepted"
[[ -f "$home/MacDesk-V6/.git/HEAD" ]] || fail "invalid archive damaged restored repository"
printf 'RESTORE_MACDESK_ARCHIVE=PASS\n'
