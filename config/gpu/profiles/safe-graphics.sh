#!/usr/bin/env bash
# Baseline renderer: do not inherit the legacy Zink/Turnip profile until its
# libraries and ICD are installed and verified in this Debian rootfs.
unset GALLIUM_DRIVER
unset MESA_LOADER_DRIVER_OVERRIDE
unset LIBGL_DRIVERS_PATH
unset VK_ICD_FILENAMES VK_DRIVER_FILES MESA_VK_WSI_PRESENT_MODE
unset ZINK_DESCRIPTORS MESA_GL_VERSION_OVERRIDE
unset MACDESK_MESA_PREFIX VTEST_SOCKET_NAME LD_LIBRARY_PATH
export LIBGL_ALWAYS_SOFTWARE=1
export MACDESK_GPU_PROFILE=SAFE_FALLBACK
