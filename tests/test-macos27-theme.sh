#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "$0")/.." && pwd)"
tmp_root="$(mktemp -d)"
trap 'rm -rf "$tmp_root"' EXIT
root="$tmp_root/MacDesk"

mkdir -p "$root/assets/themes/GoldenGate-Dark/gtk-4.0" \
  "$root/assets/wallpapers" "$root/config/xfce" "$root/state" "$root/scripts" "$tmp_root/bin"
printf '%s\n' '/* macOS 27 dark profile */' > "$root/assets/themes/GoldenGate-Dark/gtk-4.0/gtk.css"
printf '%s\n' '<svg xmlns="http://www.w3.org/2000/svg"/>' > "$root/assets/wallpapers/macos27-dark.svg"
printf '%s\n' '<property name="ThemeName" type="string" value="Old"/>' \
  '<property name="IconThemeName" type="string" value="Old"/>' > "$root/config/xfce/xsettings.xml"
printf '%s\n' '<property name="theme" type="string" value="Old"/>' > "$root/config/xfce/xfwm4.xml"
printf '%s\n' '<property name="last-image" type="string" value="/old/Tahoe-5k-light.jpg"/>' \
  > "$root/config/xfce/xfce4-desktop.xml"
cat > "$root/scripts/macdesk-stop" <<'EOF'
#!/bin/sh
printf '%s\n' stop >> "$MACDESK_ROOT/state/actions.log"
EOF
cat > "$root/scripts/macdesk" <<'EOF'
#!/bin/sh
printf '%s\n' start >> "$MACDESK_ROOT/state/actions.log"
EOF
chmod +x "$root/scripts/macdesk-stop" "$root/scripts/macdesk"
cat > "$tmp_root/bin/proot-distro" <<'EOF'
#!/bin/sh
exit 0
EOF
chmod +x "$tmp_root/bin/proot-distro"

MACDESK_ROOT="$root" PATH="$tmp_root/bin:$PATH" \
  "$repo_root/scripts/macdesk-theme" macos27-dark

grep -q 'ACTIVE_THEME=macos27-dark' "$root/state/theme.env"
grep -q 'ThemeName.*GoldenGate-Dark' "$root/config/xfce/xsettings.xml"
grep -q 'IconThemeName.*WhiteSur-MacDesk-dark' "$root/config/xfce/xsettings.xml"
grep -q 'theme.*GoldenGate-Dark' "$root/config/xfce/xfwm4.xml"
grep -q 'macos27-dark.svg' "$root/config/xfce/xfce4-desktop.xml"
grep -q 'macOS 27 dark profile' "$root/config/gtk-4.0/gtk.css"
grep -q '^stop$' "$root/state/actions.log"
grep -q '^start$' "$root/state/actions.log"
echo MACOS27_DARK_THEME=PASS
