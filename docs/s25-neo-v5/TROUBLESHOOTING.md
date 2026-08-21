# Solución de problemas

- **Phoc 0.56 / wlroots 0.20:** mezclar esa ABI con wlroots 0.19 causa crash o pantalla negra. Restaure phoc 0.53 y las versiones fijadas; no use `dnf upgrade`.
- **Pantalla negra con cursor:** compruebe ABI, `/tmp/runtime-root/wayland-0`, Labwc vivo y evidencia Turnip en `logs/labwc.log`.
- **DRI3 o render node ausente:** son advertencias esperadas en el backend X11/XShm si después aparece el dispositivo Vulkan Adreno.
- **ICD ausente:** verifique `/opt/mesa-kgsl-git/share/vulkan/icd.d/freedreno_icd.aarch64.json`; no reconstruya Mesa sin evidencia concreta.
- **Socket Wayland stale:** ejecute `scripts/macdesk-stop`; el siguiente arranque elimina socket y lock.
- **Termux:X11 stale:** el launcher limpia la instancia anterior antes de iniciar una nueva.
- **Lifecycle Phoc/Phosh:** use los launchers golden, que fijan su ABI y sesión D-Bus.
- **“Desktop manager is not active”:** procedía de `pcmanfm --desktop-pref`, expuesto por su archivo desktop. Las entradas PCManFM están ocultas; Nautilus es el gestor predeterminado. No instale un desktop manager.
- **Chromium:** se espera WebGL blocklisted/software. No fuerce Vulkan, GBM, DRM o DRI3; Labwc debe seguir en Turnip.
