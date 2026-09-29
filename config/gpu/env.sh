#!/bin/sh
# MacDesk V6 guest GPU environment. Sourced inside Debian.
export DISPLAY="${DISPLAY:-:2}"
if [ "${MACDESK_GPU_PROFILE:-}" = SAFE_FALLBACK ] || \
   [ ! -f /opt/macdesk-v6/turnip/share/vulkan/icd.d/freedreno_icd.aarch64.json ] || \
   [ ! -d /opt/macdesk-v6/mesa/lib/aarch64-linux-gnu/dri ]; then
  # Fresh installations do not ship device-specific GPU drivers. Apps must
  # honor the same working renderer as the session instead of forcing Zink.
  unset GALLIUM_DRIVER MESA_LOADER_DRIVER_OVERRIDE LIBGL_DRIVERS_PATH
  unset VK_ICD_FILENAMES VK_DRIVER_FILES MESA_VK_WSI_PRESENT_MODE
  unset ZINK_DESCRIPTORS MESA_GL_VERSION_OVERRIDE MACDESK_MESA_PREFIX
  unset VTEST_SOCKET_NAME LD_LIBRARY_PATH
  export LIBGL_ALWAYS_SOFTWARE=1 MACDESK_GPU_PROFILE=SAFE_FALLBACK
  return 0
fi
export XDG_RUNTIME_DIR="${XDG_RUNTIME_DIR:-/tmp/runtime-macdesk-v6}"
export VTEST_SOCKET_NAME="${VTEST_SOCKET_NAME:-/tmp/.virgl_test}"
export MESA_LOADER_DRIVER_OVERRIDE=zink
export GALLIUM_DRIVER=zink
export ZINK_DESCRIPTORS=lazy
export VK_DRIVER_FILES=/opt/macdesk-v6/turnip/share/vulkan/icd.d/freedreno_icd.aarch64.json
export MESA_GL_VERSION_OVERRIDE=4.3
export MACDESK_MESA_PREFIX=/opt/macdesk-v6/mesa
export LD_LIBRARY_PATH="$MACDESK_MESA_PREFIX/lib/aarch64-linux-gnu${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
export LIBGL_DRIVERS_PATH="$MACDESK_MESA_PREFIX/lib/aarch64-linux-gnu/dri"
