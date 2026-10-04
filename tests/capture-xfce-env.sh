#!/usr/bin/env bash
set -u

vars=(
  DISPLAY HOME USER LOGNAME PATH TMPDIR XDG_RUNTIME_DIR XDG_CONFIG_HOME
  XDG_CACHE_HOME DBUS_SESSION_BUS_ADDRESS PULSE_SERVER GALLIUM_DRIVER
  MESA_LOADER_DRIVER_OVERRIDE LIBGL_DRIVERS_PATH VK_ICD_FILENAMES
  VK_DRIVER_FILES MESA_VK_WSI_PRESENT_MODE ZINK_DESCRIPTORS
  MESA_GL_VERSION_OVERRIDE MACDESK_MESA_PREFIX VTEST_SOCKET_NAME
)

for name in "${vars[@]}"; do
  if [[ -v $name ]]; then value=${!name}; else value='<UNSET>'; fi
  printf '%s=%s\n' "$name" "$value"
done

for name in XDG_RUNTIME_DIR XDG_CONFIG_HOME XDG_CACHE_HOME LIBGL_DRIVERS_PATH \
  VK_ICD_FILENAMES VK_DRIVER_FILES MACDESK_MESA_PREFIX VTEST_SOCKET_NAME; do
  [[ -v $name ]] || continue
  value=${!name}
  [[ -n $value ]] || continue
  case $name in
    XDG_RUNTIME_DIR|XDG_CONFIG_HOME|XDG_CACHE_HOME|MACDESK_MESA_PREFIX|VTEST_SOCKET_NAME)
      if [[ -e $value ]]; then printf 'PATH_CHECK %s EXISTS %s\n' "$name" "$value"
      else printf 'PATH_CHECK %s MISSING %s\n' "$name" "$value"; fi
      ;;
    LIBGL_DRIVERS_PATH)
      if [[ -d $value ]]; then printf 'PATH_CHECK %s EXISTS %s\n' "$name" "$value"
      else printf 'PATH_CHECK %s MISSING %s\n' "$name" "$value"; fi
      ;;
    VK_ICD_FILENAMES|VK_DRIVER_FILES)
      if [[ -f $value ]]; then printf 'PATH_CHECK %s EXISTS %s\n' "$name" "$value"
      else printf 'PATH_CHECK %s MISSING %s\n' "$name" "$value"; fi
      ;;
  esac
done
