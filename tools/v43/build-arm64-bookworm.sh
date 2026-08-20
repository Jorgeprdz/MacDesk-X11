#!/usr/bin/env bash
set -Eeuo pipefail
export DEBIAN_FRONTEND=noninteractive

ROOT="$(pwd)"
WORK="/tmp/macdesk-v43-build"
PREFIX_OUT="/opt/macdesk-v43"
DIST="$ROOT/dist/v43"
LOGDIR="$ROOT/build-logs/v43"
MESA_REF="e24dc5bd1e7fe6101bdc866fb16a15a8fcae1aae"
WLR_REF="0.19"
LABWC_REF="0.9.7"
WAYLAND_REF="1.23.1"
WAYLAND_PROTOCOLS_REF="1.39"
GLSLANG_REF="15.1.0"
PATCH_REPO_REF="35519672cf2e252e87e78a77afd2c3284c8200d4"

mkdir -p "$WORK" "$DIST" "$LOGDIR"
stage="bootstrap"
trap 'rc=$?; echo "V43_BUILD_ERROR stage=$stage line=$LINENO rc=$rc command=$BASH_COMMAND" >&2; exit "$rc"' ERR
log() { printf '[%s] %s\n' "$(date '+%F %T')" "$*"; }

stage="apt"
log "Bookworm build environment"
printf '%s\n' \
  'deb http://deb.debian.org/debian bookworm main' \
  'deb http://deb.debian.org/debian bookworm-updates main' \
  'deb http://deb.debian.org/debian-security bookworm-security main' \
  'deb http://deb.debian.org/debian bookworm-backports main' \
  > /etc/apt/sources.list
rm -f /etc/apt/sources.list.d/debian.sources
apt-get update
apt-get install -y --no-install-recommends \
  ca-certificates git curl xz-utils zstd file jq patch pkg-config \
  build-essential python3 python3-pip python3-setuptools python3-wheel \
  ninja-build meson cmake glslang-tools spirv-tools gettext \
  libffi-dev libexpat1-dev zlib1g-dev libzstd-dev \
  libdrm-dev libx11-dev libx11-xcb-dev \
  libxcb1-dev libxcb-render0-dev libxcb-shm0-dev libxcb-xfixes0-dev \
  libxcb-randr0-dev libxcb-image0-dev libxcb-render-util0-dev \
  libxcb-icccm4-dev libxcb-ewmh-dev libxcb-composite0-dev \
  libxcb-dri3-dev libxcb-present-dev libxcb-sync-dev libxcb-xinput-dev \
  libxcb-cursor-dev libxshmfence-dev \
  libxkbcommon-dev libpixman-1-dev libvulkan-dev \
  libdisplay-info-dev libliftoff-dev libseat-dev hwdata \
  libxml2-dev libcairo2-dev libpango1.0-dev librsvg2-dev libpng-dev \
  libglib2.0-dev libjpeg-dev libinput-dev xwayland
# xcb-errors is only in Bookworm backports.
apt-get install -y -t bookworm-backports libxcb-errors-dev libdisplay-info-dev || true
python3 -m pip install --break-system-packages --no-cache-dir \
  'meson>=1.5,<2' 'ninja>=1.11' 'cmake>=3.27,<4' mako pyyaml packaging

hash -r
CMAKE_VERSION_OUT="$(cmake --version | head -1)"
printf '%s\n' "$CMAKE_VERSION_OUT" | tee "$LOGDIR/cmake-version.txt"
python3 - "$CMAKE_VERSION_OUT" <<'PYCMAKE'
import re, sys
s=sys.argv[1]
m=re.search(r'(\d+)\.(\d+)\.(\d+)', s)
if not m:
    raise SystemExit('CMAKE_GATE=FAIL unable to parse version')
v=tuple(map(int,m.groups()))
if v < (3,27,0):
    raise SystemExit(f'CMAKE_GATE=FAIL version={v}')
print('CMAKE_GATE=PASS version=' + '.'.join(map(str,v)))
PYCMAKE

export PATH="$PREFIX_OUT/bin:$PATH"
export PKG_CONFIG_PATH="$PREFIX_OUT/lib/aarch64-linux-gnu/pkgconfig:$PREFIX_OUT/lib/pkgconfig:$PREFIX_OUT/share/pkgconfig:${PKG_CONFIG_PATH:-}"
export LD_LIBRARY_PATH="$PREFIX_OUT/lib/aarch64-linux-gnu:$PREFIX_OUT/lib:${LD_LIBRARY_PATH:-}"

stage="wayland"
log "Build Wayland $WAYLAND_REF"
rm -rf "$WORK/wayland"
git clone --depth 1 --branch "$WAYLAND_REF" https://gitlab.freedesktop.org/wayland/wayland.git "$WORK/wayland"
meson setup "$WORK/wayland/build" "$WORK/wayland" \
  --prefix="$PREFIX_OUT" --buildtype=release \
  -Ddocumentation=false -Dtests=false
ninja -C "$WORK/wayland/build" -j"$(nproc)"
ninja -C "$WORK/wayland/build" install

stage="wayland-protocols"
log "Build wayland-protocols $WAYLAND_PROTOCOLS_REF"
rm -rf "$WORK/wayland-protocols"
git clone --depth 1 --branch "$WAYLAND_PROTOCOLS_REF" \
  https://gitlab.freedesktop.org/wayland/wayland-protocols.git "$WORK/wayland-protocols"
meson setup "$WORK/wayland-protocols/build" "$WORK/wayland-protocols" \
  --prefix="$PREFIX_OUT" --buildtype=release -Dtests=false
ninja -C "$WORK/wayland-protocols/build" -j"$(nproc)"
ninja -C "$WORK/wayland-protocols/build" install

stage="glslang"
log "Build glslang $GLSLANG_REF from source (Bookworm package is too old for Mesa)"
rm -rf "$WORK/glslang"
git clone --depth 1 --branch "$GLSLANG_REF" \
  https://github.com/KhronosGroup/glslang.git "$WORK/glslang"
cmake -S "$WORK/glslang" -B "$WORK/glslang/build" -G Ninja \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_INSTALL_PREFIX="$PREFIX_OUT" \
  -DBUILD_EXTERNAL=OFF \
  -DENABLE_OPT=OFF \
  -DENABLE_SPVREMAPPER=OFF \
  -DGLSLANG_TESTS=OFF \
  -DGLSLANG_ENABLE_INSTALL=ON \
  -DENABLE_GLSLANG_BINARIES=ON
cmake --build "$WORK/glslang/build" --parallel "$(nproc)"
cmake --install "$WORK/glslang/build"
hash -r
GLSLANG_BIN="$(command -v glslangValidator || true)"
[ -n "$GLSLANG_BIN" ] || { echo "GLSLANG_GATE=FAIL no glslangValidator"; exit 21; }
GLSLANG_VERSION_OUT="$(glslangValidator --version 2>&1 | head -5)"
printf '%s\n' "$GLSLANG_VERSION_OUT" | tee "$LOGDIR/glslang-version.txt"
python3 - "$GLSLANG_VERSION_OUT" <<'PYV'
import re, sys
s=sys.argv[1]
m=re.search(r'Glslang Version:\s*(?:\d+:)?(\d+)\.(\d+)\.(\d+)', s, re.I)
if not m:
    m=re.search(r'GLSLANG[^0-9]*(\d+)\.(\d+)(?:\.(\d+))?', s, re.I)
if not m:
    raise SystemExit('GLSLANG_GATE=FAIL unable to parse version')
v=tuple(int(x or 0) for x in m.groups())
print('GLSLANG_VERSION_PARSED=%d.%d.%d' % v)
if v < (12,2,0):
    raise SystemExit('GLSLANG_GATE=FAIL need >=12.2')
print('GLSLANG_GATE=PASS')
PYV
case "$GLSLANG_BIN" in
  "$PREFIX_OUT"/*) : ;;
  *) echo "GLSLANG_GATE=FAIL expected $PREFIX_OUT binary, got $GLSLANG_BIN"; exit 22 ;;
esac

stage="patch-source"
log "Fetch S25 KGSL patch source $PATCH_REPO_REF"
rm -rf "$WORK/phosh-termux-gpu"
git clone --filter=blob:none https://github.com/Azkali/phosh-termux-gpu.git "$WORK/phosh-termux-gpu"
git -C "$WORK/phosh-termux-gpu" checkout "$PATCH_REPO_REF"

stage="mesa-source"
log "Fetch Mesa $MESA_REF"
rm -rf "$WORK/mesa"
git init "$WORK/mesa"
git -C "$WORK/mesa" remote add origin https://github.com/mirror/mesa.git
git -C "$WORK/mesa" fetch --depth 1 origin "$MESA_REF"
git -C "$WORK/mesa" checkout --detach FETCH_HEAD

stage="mesa-patch"
python3 - "$WORK/mesa" <<'PY'
import os,sys
f=os.path.join(sys.argv[1],'src/freedreno/vulkan/tu_knl_kgsl.cc')
if not os.path.exists(f): raise SystemExit('missing tu_knl_kgsl.cc')
s=open(f,encoding='utf-8').read()
old=("   if (instance->vk.enabled_extensions.KHR_display) {\n"
     "      return vk_errorf(instance, VK_ERROR_INITIALIZATION_FAILED,\n"
     "                       \"I can't KHR_display\");\n   }")
if old in s:
    s=s.replace(old,'   /* MacDesk KGSL: ignore KHR_display. */',1)
    open(f,'w',encoding='utf-8').write(s)
    print('PATCH_KHR_DISPLAY=APPLIED')
else:
    print('PATCH_KHR_DISPLAY=NOT_NEEDED')
PY

stage="mesa-configure"
log "Configure Mesa Turnip KGSL"
meson setup "$WORK/mesa/builddir" "$WORK/mesa" \
  --prefix="$PREFIX_OUT" --buildtype=release \
  -Dvulkan-drivers=freedreno -Dgallium-drivers= \
  -Dfreedreno-kmds=kgsl,msm -Dplatforms=x11,wayland \
  -Dglx=disabled -Degl=disabled -Dgbm=disabled \
  -Dopengl=false -Dllvm=disabled -Dvideo-codecs= -Dvulkan-layers=

stage="mesa-build"
log "Build/install Turnip"
ninja -C "$WORK/mesa/builddir" -j"$(nproc)"
ninja -C "$WORK/mesa/builddir" install

stage="wlroots-source"
log "Fetch wlroots $WLR_REF"
rm -rf /root/wlroots
git clone --depth 1 --branch "$WLR_REF" \
  https://gitlab.freedesktop.org/wlroots/wlroots.git /root/wlroots

stage="wlroots-patch"
log "Apply Vulkan->SHM KGSL patches"
python3 "$WORK/phosh-termux-gpu/fedora/apply_wlr_patches.py" \
  | tee "$LOGDIR/wlroots-patches.log"

stage="wlroots-configure"
log "Configure wlroots: nested X11 + Vulkan + XWayland"
meson setup /root/wlroots/build /root/wlroots \
  --prefix="$PREFIX_OUT" --buildtype=release \
  -Dbackends=x11 -Drenderers=vulkan -Dxwayland=enabled \
  -Dexamples=false -Dwerror=false

stage="wlroots-build"
ninja -C /root/wlroots/build -j"$(nproc)"
ninja -C /root/wlroots/build install

stage="labwc-source"
log "Fetch Labwc $LABWC_REF"
rm -rf "$WORK/labwc"
git clone --depth 1 --branch "$LABWC_REF" \
  https://github.com/labwc/labwc.git "$WORK/labwc"

stage="labwc-configure"
log "Configure Labwc against patched wlroots"
meson setup "$WORK/labwc/build" "$WORK/labwc" \
  --prefix="$PREFIX_OUT" --buildtype=release \
  -Dicon=disabled -Dnls=disabled -Dman-pages=disabled \
  -Dtest=disabled -Dxwayland=enabled

stage="labwc-build"
ninja -C "$WORK/labwc/build" -j"$(nproc)"
ninja -C "$WORK/labwc/build" install

stage="manifest"
mkdir -p "$PREFIX_OUT/share/macdesk-v43"
MESA_SHA="$(git -C "$WORK/mesa" rev-parse HEAD)"
WLR_SHA="$(git -C /root/wlroots rev-parse HEAD)"
LABWC_SHA="$(git -C "$WORK/labwc" rev-parse HEAD)"
cat > "$PREFIX_OUT/share/macdesk-v43/build-manifest.json" <<EOF
{
  "target":"debian-bookworm-arm64",
  "arch":"$(dpkg --print-architecture)",
  "mesa":"$MESA_SHA",
  "wlroots":"$WLR_SHA",
  "labwc":"$LABWC_SHA",
  "wayland":"$WAYLAND_REF",
  "wayland_protocols":"$WAYLAND_PROTOCOLS_REF",
  "glslang":"$GLSLANG_REF",
  "patch_repo":"$PATCH_REPO_REF",
  "built_at":"$(date -u '+%FT%TZ')"
}
EOF

stage="validate"
log "Static validation"
ICD="$(find "$PREFIX_OUT" -type f \( -name 'freedreno_icd.aarch64.json' -o -name 'freedreno_icd.*.json' \) | head -1)"
WLR_SO="$(find "$PREFIX_OUT" -type f -name 'libwlroots-0.19.so*' | head -1)"
LABWC_BIN="$PREFIX_OUT/bin/labwc"
[ -n "$ICD" ] && [ -f "$ICD" ]
[ -n "$WLR_SO" ] && [ -f "$WLR_SO" ]
[ -x "$LABWC_BIN" ]
file "$WLR_SO" "$LABWC_BIN" | tee "$LOGDIR/file-validation.log"
file "$LABWC_BIN" | grep -qiE 'ARM aarch64|ARM64'
LD_LIBRARY_PATH="$PREFIX_OUT/lib/aarch64-linux-gnu:$PREFIX_OUT/lib" \
  ldd "$LABWC_BIN" | tee "$LOGDIR/labwc-ldd.txt"
! grep -q 'not found' "$LOGDIR/labwc-ldd.txt"

stage="package"
log "Package artifact"
rm -f "$DIST/macdesk-v43-arm64-bookworm.tar.zst" "$DIST/SHA256SUMS"
tar -C /opt --zstd -cf "$DIST/macdesk-v43-arm64-bookworm.tar.zst" macdesk-v43
sha256sum "$DIST/macdesk-v43-arm64-bookworm.tar.zst" | tee "$DIST/SHA256SUMS"
cp "$PREFIX_OUT/share/macdesk-v43/build-manifest.json" "$DIST/build-manifest.json"

log "V43_BUILD=PASS"
