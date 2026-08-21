#!/data/data/com.termux/files/usr/bin/bash
set -u
BASE="${MACDESK_BASE:-$HOME/MacDesk-V5}"
fail=0
need() { "$@" || { echo "FAIL $*"; fail=1; }; }
need "$BASE/scripts/golden-state-check.sh"
need pgrep -f 'termux-x11.*:0'
need pgrep -x labwc
need grep -q "Vulkan device: 'Adreno (TM) 830v1'" "$BASE/logs/labwc.log"
need grep -q 'Driver name: turnip Mesa driver' "$BASE/logs/labwc.log"
need "$BASE/scripts/s25-storage-prepare"
need grep -q '^TERMUX_STORAGE=PASS$' "$BASE/state/storage.env"
need grep -q '^PHONE_STORAGE_BIND=PASS$' "$BASE/state/storage.env"
need grep -q '^PHONE_STORAGE_READ=PASS$' "$BASE/state/storage.env"
need grep -q '^PHONE_STORAGE_WRITE=PASS$' "$BASE/state/storage.env"
need grep -q '^NAUTILUS_PHONE_BOOKMARK=PASS$' "$BASE/state/storage.env"
proot-distro login fedora --shared-tmp -e MACDESK_BASE="$BASE" -- bash -lc '
  pgrep -x yambar >/dev/null && pgrep -x plank >/dev/null &&
  test "$(runuser -u macdesk -- xdg-mime query default inode/directory)" = s25-nautilus.desktop &&
  rpm -q --quiet chromium nautilus libreoffice-core plank labwc
' || fail=1
[ "$fail" -eq 0 ] && echo S25_NEO_VALIDATION=PASS || { echo S25_NEO_VALIDATION=BLOCKED; exit 1; }
