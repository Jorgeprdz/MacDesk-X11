#!/usr/bin/env bash
# Restore Debian 13 / XFCE 4.20 artwork without installing system packages.
set -euo pipefail
for tool in curl dpkg-deb sha256sum; do
  command -v "$tool" >/dev/null || { echo "Falta $tool (Termux: pkg install curl dpkg coreutils)" >&2; exit 1; }
done
case "$(cd "$HOME" && pwd -P)" in
  /sdcard*|/storage/*|/mnt/media_rw/*) echo 'HOME debe estar en almacenamiento privado.' >&2; exit 1;;
esac
cache="$HOME/.cache/macdesk"
backgrounds="$HOME/.local/share/backgrounds/xfce"
icons="$HOME/.local/share/icons"
cursor="$icons/MacDesk-Adwaita"
mkdir -p "$cache" "$backgrounds" "$icons"
touch "$cache/.nomedia" "$backgrounds/.nomedia" "$icons/.nomedia"
if [ -e "$cursor" ] && [ ! -f "$cursor/.macdesk-restored" ]; then
  echo "Ya existe $cursor; no se sobrescribira." >&2
  exit 1
fi
stage=$(mktemp -d "$cache/.xfce-assets.XXXXXX")
trap 'rm -rf -- "$stage"' EXIT
touch "$stage/.nomedia"
fetch() {
  curl --proto '=https' --proto-redir '=https' -fL --retry 2 --connect-timeout 15 --max-time 180 "$1" -o "$stage/$2"
  printf '%s  %s\n' "$3" "$stage/$2" | sha256sum -c -
  dpkg-deb -x "$stage/$2" "$stage/extracted"
}
fetch https://deb.debian.org/debian/pool/main/x/xfdesktop4/xfdesktop4-data_4.20.1-1_all.deb xfdesktop.deb 4d49e514d55a78ebc7a12b0f1dd1ee737dbc4c0bd8d1ea82f410eb79db918ae1
fetch https://deb.debian.org/debian/pool/main/a/adwaita-icon-theme/adwaita-icon-theme_48.1-1_all.deb adwaita.deb f60b0577aee314d43d6908ca7f0b8f07dc48e2bb766e7e25035330817e0e827c
# Preserve existing pictures; only fill missing official filenames.
for file in "$stage/extracted/usr/share/backgrounds/xfce/"*; do
  [ -e "$backgrounds/${file##*/}" ] || cp -p -- "$file" "$backgrounds/"
done
cp "$stage/extracted/usr/share/doc/xfdesktop4-data/copyright" "$backgrounds/COPYRIGHT"
mkdir -p "$cursor"
touch "$cursor/.nomedia" "$cursor/.macdesk-restored"
cp -a "$stage/extracted/usr/share/icons/Adwaita/cursors" "$cursor/"
cp "$stage/extracted/usr/share/doc/adwaita-icon-theme/copyright" "$cursor/COPYRIGHT"
printf '[Icon Theme]\nName=MacDesk Adwaita\nComment=Restored Adwaita cursors\nInherits=Adwaita\n' > "$cursor/index.theme"
# Classic Xcursor consumers also search ~/.icons (relative link survives PRoot).
mkdir -p "$HOME/.icons"
touch "$HOME/.icons/.nomedia"
if [ ! -e "$HOME/.icons/MacDesk-Adwaita" ] && [ ! -L "$HOME/.icons/MacDesk-Adwaita" ]; then
  ln -s ../.local/share/icons/MacDesk-Adwaita "$HOME/.icons/MacDesk-Adwaita"
fi
mkdir -p "$HOME/.config/autostart"
cat > "$HOME/.config/autostart/macdesk-restored-cursor.desktop" <<'EOF'
[Desktop Entry]
Type=Application
Name=MacDesk restored cursor
Exec=sh -c "xfconf-query -c xsettings -p /Gtk/CursorThemeName -s MacDesk-Adwaita || xfconf-query -c xsettings -p /Gtk/CursorThemeName -n -t string -s MacDesk-Adwaita"
OnlyShowIn=XFCE;
StartupNotify=false
Terminal=false
EOF
printf 'Fondos: %s\nCursores: %s\n' "$backgrounds" "$cursor"
echo 'En Configuracion del escritorio > Fondo > Otra carpeta, abre la ruta de fondos.'
echo 'El cursor se aplicara en la proxima sesion; tambien puedes elegir MacDesk Adwaita en Raton y panel tactil > Tema.'
