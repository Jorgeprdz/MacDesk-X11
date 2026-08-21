# Arquitectura

Android conserva control del hardware y expone KGSL. Termux aloja Termux:X11, PulseAudio y `proot-distro`. Fedora ve `/dev/kgsl-3d0` y el ICD de `/opt/mesa-kgsl-git`; Turnip renderiza para Adreno 830.

Labwc enlaza únicamente el wlroots 0.19 parcheado. El backend X11 de wlroots presenta en Termux:X11 mediante el camino XShm tolerante a la ausencia de DRI3/render node. Las advertencias DRI3 no significan fallback: el log debe contener `Vulkan device: 'Adreno (TM) 830v1'` y `turnip Mesa driver`.

Aplicaciones GTK como Nautilus usan Wayland. Plank y Chromium usan XWayland; Chromium no fuerza Vulkan propio. Yambar y swaybg son Wayland. PulseAudio usa TCP loopback. `/sdcard/Download` enlaza el almacenamiento compartido de Android.

El estado golden Phoc/Phosh permanece paralelo e intacto. `macdesk-stop` termina compositor, apps, buses mínimos y sockets sin afectar Android.
