#!/data/data/com.termux/files/usr/bin/bash
set -eu

probe="$(proot-distro login debian --shared-tmp -- sh -lc '
  DISPLAY=:2 xinput list
  printf "%s\n" "---XKB---"
  DISPLAY=:2 setxkbmap -query
  printf "%s\n" "---WM---"
  DISPLAY=:2 xprop -root _NET_SUPPORTING_WM_CHECK
')"
printf '%s\n' "$probe"
printf '%s\n' "$probe" | grep -F 'Virtual core pointer' >/dev/null
printf '%s\n' "$probe" | grep -F 'Virtual core keyboard' >/dev/null
printf '%s\n' "$probe" | grep -F 'layout:     latam' >/dev/null
printf '%s\n' "$probe" | grep -F '_NET_SUPPORTING_WM_CHECK' >/dev/null

echo INPUT_DEVICES_PRESENT=PASS
echo XKB_LAYOUT_LATAM=PASS
echo WINDOW_MANAGER_PRESENT=PASS
echo PHYSICAL_INPUT=MANUAL_VALIDATION_REQUIRED
