# Limitaciones conocidas

- Chromium usa Ozone X11/XWayland y rasterización no Vulkan; el compositor sí usa Turnip.
- La papelera funciona en HOME. Android no permite crear `/sdcard/.Trash-UID`, por lo que borrar en almacenamiento compartido puede ser permanente.
- Nautilus no ofrece red/GVFS, Tracker ni integración Mutter; se omiten deliberadamente para una sesión mínima.
- La automatización X11 no siempre puede enfocar ventanas rootless XWayland; la validación visual/física es autoritativa para input.
- Las advertencias DRI3 y ausencia de DRM render node son esperadas en XShm.
