#!/usr/bin/env bash
# MacDesk all-in-one bootstrap. Run in Termux, never inside Debian/PRoot.
set -euo pipefail

REPOSITORY=https://github.com/Jorgeprdz/MacDesk-X11.git
REF=feature/wps-desktop-integration
APK_URL=https://github.com/termux/termux-x11/releases/download/nightly/termux-x11-universal-debug.apk
HOST_PACKAGES=(git curl proot-distro pulseaudio python rclone x11-repo termux-x11-nightly)
GUEST_PACKAGES=(ca-certificates coreutils util-linux procps psmisc python3
  xfce4 xfce4-terminal dbus-x11 x11-utils x11-xserver-utils xinput xdotool wmctrl
  plank nautilus gnome-sushi gjs librsvg2-common libglib2.0-bin libgl1-mesa-dri
  fonts-dejavu-core fonts-liberation2 fonts-noto-core firefox-esr)
mode=install
open_apk=true
usage() {
  cat <<'EOF'
MacDesk all-in-one installer (Android ARM64 + Termux)
  bash install.sh             Install missing dependencies; preserve existing repo
  bash install.sh --check     Read-only environment/dependency check
  bash install.sh --plan      Show packages and actions without modifying anything
  bash install.sh --no-apk-open  Download missing Android APK without opening it
  bash install.sh --help

No root, force-stop, session restart, automatic git reset or user config replacement.
Android requires you to approve the Termux:X11 APK installation yourself.
Re-running the installer preserves the current checkout; it is not a git updater.
EOF
}
fail() { printf 'MacDesk installer: %s\n' "$*" >&2; exit 1; }
install_launcher() {
  local destination="$1" entrypoint="$2" interpreter="$3"
  if [[ ! -e "$destination" && ! -L "$destination" ]]; then
    # Repository scripts derive BASE from their invocation path. A wrapper
    # preserves that path; a symlink in PREFIX/bin would make BASE incorrect.
    printf '#!%s\nexec %q "$@"\n' "$interpreter" "$entrypoint" > "$destination"
    chmod 0755 "$destination"
  else
    printf 'Existing launcher preserved: %s\n' "$destination"
  fi
}

main() {
for arg in "$@"; do
  case "$arg" in
    --help|-h) usage; exit 0 ;;
    --check) mode=check ;;
    --plan) mode=plan ;;
    --no-apk-open) open_apk=false ;;
    *) fail "Unknown option: $arg" ;;
  esac
done
if [[ "$mode" == plan ]]; then
  printf 'Termux packages: %s\n' "${HOST_PACKAGES[*]}"
  printf 'Debian packages: %s\n' "${GUEST_PACKAGES[*]}"
  printf 'Checkout: ~/MacDesk-V6 (existing checkout preserved)\nDebian: existing container reused; otherwise installed\n'
  printf 'Android APK: %s (user approval required)\n' "$APK_URL"
  printf 'No automatic launch, restart, GPU rebuild, browser daemon or VNC exposure.\n'
  exit 0
fi

[[ "${PREFIX:-}" == /data/data/com.termux/files/usr ]] || fail 'Run this command in Termux, outside Debian/PRoot.'
[[ "${HOME:-}" == /data/data/com.termux/files/home ]] || fail 'Termux HOME is required; do not run from a guest shell.'
[[ "$(uname -m)" == aarch64 ]] || fail 'This MacDesk build includes ARM64 binaries and requires aarch64.'
command -v pkg >/dev/null || fail 'Termux package manager not found.'
target="$HOME/MacDesk-V6"
[[ ! -L "$target" ]] || fail 'Refusing a symlink at ~/MacDesk-V6.'
if [[ -e "$target" ]]; then
  [[ -d "$target/.git" && -f "$target/scripts/macdesk-xfce-session" ]] || fail 'Existing ~/MacDesk-V6 is not a recognized checkout; left untouched.'
fi

installed() { [[ "$(dpkg-query -W -f='${Status}' "$1" 2>/dev/null || true)" == 'install ok installed' ]]; }
if [[ "$mode" == check ]]; then
  missing=0
  for package in "${HOST_PACKAGES[@]}"; do
    if installed "$package"; then printf 'HOST %s OK\n' "$package"
    else printf 'HOST %s MISSING\n' "$package"; missing=1; fi
  done
  if command -v proot-distro >/dev/null && proot-distro login debian -- /bin/true >/dev/null 2>&1; then
    printf 'DEBIAN OK\n'
    proot-distro login debian -- /bin/sh -c '
      missing=0
      for package do
        if [ "$(dpkg-query -W -f="\${Status}" "$package" 2>/dev/null)" = "install ok installed" ]; then
          printf "GUEST %s OK\n" "$package"
        else printf "GUEST %s MISSING\n" "$package"; missing=1; fi
      done
      exit "$missing"
    ' sh "${GUEST_PACKAGES[@]}" || missing=1
  else printf 'DEBIAN MISSING OR UNAVAILABLE\n'; missing=1; fi
  printf 'CHECK_ONLY: no changes made\n'
  exit "$missing"
fi

# Installation while an existing session is alive could race packages/config.
# Do not stop it: the user may have documents open.
if [[ -r "$target/state/guest.pid" ]]; then
  read -r session_pid < "$target/state/guest.pid" || true
  if [[ "${session_pid:-}" =~ ^[0-9]+$ ]] && kill -0 "$session_pid" 2>/dev/null; then
    printf 'MacDesk session is running; preserved without changes.\nUse --check now, or rerun after closing the desktop normally.\n'
    exit 0
  fi
fi

stage=''
cleanup() { [[ -z "$stage" ]] || rm -rf -- "$stage"; }
trap cleanup EXIT
for package in "${HOST_PACKAGES[@]}"; do
  installed "$package" || pkg install -y "$package"
done

if [[ ! -d "$target" ]]; then
  stage=$(mktemp -d "$HOME/.macdesk-install.XXXXXX")
  git clone --depth 1 --single-branch --branch "$REF" "$REPOSITORY" "$stage/repo"
  [[ -x "$stage/repo/scripts/macdesk" && -f "$stage/repo/scripts/session-start" ]] || fail 'Downloaded checkout is incomplete.'
  mv -- "$stage/repo" "$target"
else
  printf 'Preserving existing checkout and all local changes: %s\n' "$target"
fi

if ! proot-distro login debian -- /bin/true >/dev/null 2>&1; then
  # proot-distro itself refuses to overwrite an existing container. A broken
  # existing guest therefore stops installation rather than being reset.
  proot-distro install debian
fi
proot-distro login debian --shared-home --shared-tmp -- /bin/bash -s -- "${GUEST_PACKAGES[@]}" <<'GUEST'
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive
missing=()
for package do
  [[ "$(dpkg-query -W -f='${Status}' "$package" 2>/dev/null || true)" == 'install ok installed' ]] || missing+=("$package")
done
if ((${#missing[@]})); then
  apt-get update
  apt-get install -y --no-install-recommends --no-upgrade "${missing[@]}"
fi
root=/root/MacDesk-V6
mkdir -p /root/.local/share/themes /root/.local/share/icons /root/.local/share/applications
for theme in GoldenGate-Light GoldenGate-Dark; do
  link="/root/.local/share/themes/$theme"
  if [[ ! -e "$link" && ! -L "$link" ]]; then ln -s "$root/assets/themes/$theme" "$link"; fi
done
for icon in WhiteSur-MacDesk WhiteSur-MacDesk-dark WhiteSur-MacDesk-light; do
  link="/root/.local/share/icons/$icon"
  if [[ ! -e "$link" && ! -L "$link" ]]; then ln -s "$root/assets/icons-clean/$icon" "$link"; fi
done
for entry in "$root"/config/applications/*.desktop; do
  destination="/root/.local/share/applications/$(basename "$entry")"
  [[ -e "$destination" ]] || install -m 0644 "$entry" "$destination"
done
# SAFE_FALLBACK is the normal session's default. The installer does not copy
# device-specific Vulkan binaries, enable GPU experiments or overwrite XFCE.
printf 'DEBIAN_DESKTOP=INSTALLED\n'
GUEST

for command in macdesk macdesk-stop macdesk-resume macdesk-smart-host macdesk-gdrive; do
  link="$PREFIX/bin/$command"
  install_launcher "$link" "$target/scripts/$command" "$PREFIX/bin/bash"
done

apk_path=$(timeout 5 /system/bin/pm path com.termux.x11 2>/dev/null || true)
if [[ "$apk_path" != package:* ]]; then
  cache="$HOME/.cache/macdesk/install"
  mkdir -p "$cache"
  chmod 700 "$cache"
  curl --fail --location --retry 2 --connect-timeout 15 --max-time 180 \
    "$APK_URL" -o "$cache/termux-x11.apk.part"
  mv -- "$cache/termux-x11.apk.part" "$cache/termux-x11.apk"
  printf 'Termux:X11 APK: %s\nApprove installation in Android; do not uninstall an existing differently-signed build.\n' "$cache/termux-x11.apk"
  if [[ "$open_apk" == true ]] && command -v termux-open >/dev/null; then
    termux-open --view --content-type application/vnd.android.package-archive "$cache/termux-x11.apk" || true
  fi
fi
printf '\nMacDesk desktop files and dependencies prepared.\n'
printf 'For shared storage and WPS desktop integration, run: bash %s/scripts/setup-wps-desktop\n' "$target"
printf 'Google Drive can be linked afterward with: macdesk-gdrive setup\n'
printf 'After the Android APK is installed, start with: macdesk\n'
printf 'Features and hardware limitations: %s/docs/SMART-DESKTOP.md\n' "$target"
}

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then main "$@"; fi
