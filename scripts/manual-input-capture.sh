#!/bin/sh
set -eu

out=/data/data/com.termux/files/home/MacDesk-V6/logs/manual-keyboard-input.txt
tmp="${out}.tmp.$$"

printf '\033[2J\033[H'
echo 'MacDesk V6 — physical es-MX input gate (Super excluded)'
echo
echo 'Type each requested line exactly, then press Enter.'
echo
printf '1/3 accents: á é í ó ú ñ Ñ\n> '
IFS= read -r accents
printf '2/3 punctuation: ¿ ? ¡ ! @ # $ %% & / ( ) = + - _\n> '
IFS= read -r punctuation
printf '3/3 letters/numbers/Shift: abc XYZ 0123456789\n> '
IFS= read -r basic

{
  printf 'ACCENTS=%s\n' "$accents"
  printf 'PUNCTUATION=%s\n' "$punctuation"
  printf 'BASIC=%s\n' "$basic"
} > "$tmp"
mv "$tmp" "$out"

echo
echo 'CAPTURED. Leave this window open for Ctrl/Alt/focus/resize tests.'
echo 'Press Enter only after those tests are complete.'
IFS= read -r _done
