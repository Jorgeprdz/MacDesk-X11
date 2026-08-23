#!/data/data/com.termux/files/usr/bin/bash
set -eu

BASE="$HOME/MacDesk-V6"
TURNIP=/opt/macdesk-v6/turnip
MESA=/opt/macdesk-v6/mesa
ICD="$TURNIP/share/vulkan/icd.d/freedreno_icd.aarch64.json"

vulkan="$(timeout 30 proot-distro login debian -- sh -lc \
  "VK_DRIVER_FILES=$ICD LD_LIBRARY_PATH=$TURNIP/lib/aarch64-linux-gnu vulkaninfo --summary 2>&1")"
printf '%s\n' "$vulkan" | grep -F "deviceName         = Adreno (TM) 830"
printf '%s\n' "$vulkan" | grep -F 'driverName         = turnip Mesa driver'
if printf '%s\n' "$vulkan" | grep -qiE 'llvmpipe|software rasterizer'; then
  echo SOFTWARE_RENDERER=YES
  exit 1
fi

gpu_env="DISPLAY=${DISPLAY:-:2} XDG_RUNTIME_DIR=/tmp LD_LIBRARY_PATH=$MESA/lib/aarch64-linux-gnu LIBGL_DRIVERS_PATH=$MESA/lib/aarch64-linux-gnu/dri MESA_LOADER_DRIVER_OVERRIDE=zink GALLIUM_DRIVER=zink ZINK_DESCRIPTORS=lazy VTEST_SOCKET_NAME=/tmp/.virgl_test VK_DRIVER_FILES=$ICD MESA_GL_VERSION_OVERRIDE=4.3"
gles="$(timeout 30 proot-distro login debian --shared-tmp -- sh -lc \
  "$gpu_env eglinfo -p x11 -a gles -B 2>&1")"
opengl="$(timeout 30 proot-distro login debian --shared-tmp -- sh -lc \
  "$gpu_env eglinfo -p x11 -a glcore -B 2>&1")"
printf '%s\n' "$gles" | grep -F 'EGL API version: 1.5'
printf '%s\n' "$gles" | grep -F "OpenGL ES profile renderer: zink Vulkan"
printf '%s\n' "$opengl" | grep -F "OpenGL core profile renderer: zink Vulkan"

echo GPU_DRIVER=TURNIP
echo EGL=PASS
echo GLES=PASS
echo OPENGL=PASS
echo VULKAN=PASS
echo SOFTWARE_RENDERER=NO
echo GPU_ACCELERATION=PASS
