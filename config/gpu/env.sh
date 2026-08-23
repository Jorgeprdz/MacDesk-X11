#!/bin/sh
# MacDesk V6 guest GPU environment. Sourced inside Debian.
export DISPLAY="${DISPLAY:-:2}"
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
