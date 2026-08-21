#!/data/data/com.termux/files/usr/bin/bash
set -u
BASE="${MACDESK_BASE:-$HOME/MacDesk-V5}"
"$BASE/scripts/golden-state-check.sh" || true
printf 'TERMUX_X11=%s\n' "$(pgrep -f 'termux-x11.*:0' >/dev/null && echo UP || echo DOWN)"
proot-distro login fedora --shared-tmp -e MACDESK_BASE="$BASE" -- bash -lc '
  for p in labwc yambar plank nautilus; do printf "%s=%s\n" "${p^^}" "$(pgrep -x "$p" >/dev/null && echo UP || echo DOWN)"; done
  grep -E "Vulkan device:|Driver name:|X11-1" "$MACDESK_BASE/logs/labwc.log" | tail -8
  rpm -q chromium nautilus libreoffice-core plank labwc
'
