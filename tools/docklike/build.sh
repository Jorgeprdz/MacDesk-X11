#!/bin/bash
# Rebuild in Debian on aarch64. Install build dependencies separately.
set -euo pipefail
root="$(cd -- "$(dirname -- "$0")/../.." && pwd)"
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
git clone --depth 1 --branch xfce4-docklike-plugin-0.4.3 https://github.com/xfce-mirror/xfce4-docklike-plugin.git "$work/source"
cd "$work/source"
patch -p1 < "$root/tools/docklike/macdesk.patch"
sh autogen.sh --prefix=/usr --libdir=/usr/lib/aarch64-linux-gnu --disable-wayland
make -j2
strip -o "$root/tools/docklike/libdocklike-aarch64.so" src/.libs/libdocklike.so
