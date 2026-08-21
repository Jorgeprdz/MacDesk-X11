# Instalación reproducible

1. Instale Termux y Termux:X11 compatibles y conceda acceso al almacenamiento con `termux-setup-storage`.
2. Instale Fedora 44 mediante `proot-distro`. No actualice globalmente el contenedor.
3. Restaure `/opt/mesa-kgsl-git` y confirme que el ICD Turnip detecta Adreno 830.
4. Instale exactamente phoc 0.53.0 y wlroots0.19 0.19.3; aplique el parche wlroots del repo. Estos forman el rollback golden Phosh y no deben recompilarse durante la instalación del escritorio.
5. Instale Labwc 0.9.6 y las versiones fijadas en [VERSION-PINS.md](../VERSION-PINS.md). Use `install_weak_deps=False` y excluya `phoc`, `wlroots*` y `mesa*`.
6. Ejecute `scripts/install.sh`, después `scripts/golden-state-check.sh`.
7. Arranque con `scripts/macdesk`. El launcher limpia estado anterior, inicia Termux:X11/audio, abre Fedora, exige Vulkan/Turnip y verifica salud.
8. Ejecute `scripts/validate.sh`. Detenga con `scripts/macdesk-stop`.

Chromium se fija a Ozone X11, sin Vulkan/GBM/DRM/DRI3. Nautilus usa un bus mínimo sin autoactivación de servicios GNOME; HOME, Downloads y `/sdcard` permanecen disponibles.
