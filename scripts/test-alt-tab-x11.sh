#!/data/data/com.termux/files/usr/bin/bash
set -u

BASE="$HOME/MacDesk-V6"
capture="$(mktemp "$BASE/logs/alt-tab-live.XXXXXX")" || exit 1
trap 'rm -f "$capture"' EXIT

echo 'Pulsa Alt+Tab una vez en los próximos 10 segundos.'
proot-distro login debian --shared-tmp -- sh -lc \
  'DISPLAY=:2 timeout 10s stdbuf -oL xinput test-xi2 --root' \
  >"$capture" 2>&1 || true

awk '
  /EVENT type 13 \(RawKeyPress\)/  { event="press"; next }
  /EVENT type 14 \(RawKeyRelease\)/ { event="release"; next }
  event != "" && /detail:/ {
    sequence++
    if ($2 == 64 && event == "press" && !alt_press) alt_press=sequence
    if ($2 == 23 && event == "press" && !tab_press) tab_press=sequence
    if ($2 == 23 && event == "release" && !tab_release) tab_release=sequence
    if ($2 == 64 && event == "release" && !alt_release) alt_release=sequence
    event=""
  }
  END {
    print "X11 Alt_L: " (alt_press && alt_release ? "PASS" : "FAIL")
    print "X11 Tab: " (tab_press && tab_release ? "PASS" : "FAIL")
    if (alt_press && tab_press && tab_release && alt_release &&
        alt_press < tab_press && tab_press < tab_release && tab_release < alt_release)
      print "Alt+Tab event sequence: PASS"
    else
      print "Alt+Tab event sequence: FAIL"
  }
' "$capture"

echo 'XFWM window switch: confirma visualmente que cambió de ventana.'
