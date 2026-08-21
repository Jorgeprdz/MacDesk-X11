#!/data/data/com.termux/files/usr/bin/bash
set -u
BASE="${MACDESK_BASE:-$HOME/MacDesk-V5}"
fail=0
check() { if "$@"; then printf 'PASS %s\n' "$*"; else printf 'FAIL %s\n' "$*"; fail=1; fi; }
check test -x "$BASE/scripts/macdesk-v5-golden-diagnostic"
"$BASE/scripts/macdesk-v5-golden-diagnostic" || fail=1
proot-distro login fedora -- bash -lc '
  rpm -q --quiet phoc-0.53.0-1.fc44 wlroots0.19-0.19.3-1.fc44 labwc-0.9.6-1.fc44 &&
  test -r /opt/mesa-kgsl-git/share/vulkan/icd.d/freedreno_icd.aarch64.json &&
  test "$(sha256sum /root/wlroots/build/libwlroots-0.19.so | cut -d" " -f1)" = ad7dcf5c762ead62551362e6bfb66c6c52080a00b595734b57a14a4b4861df83
' || fail=1
[ "$fail" -eq 0 ] && echo GOLDEN_STATE=PASS || { echo GOLDEN_STATE=BLOCKED; exit 1; }
