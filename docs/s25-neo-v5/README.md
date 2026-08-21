# MacDesk V5 — S25 Neo

S25 Neo convierte un Galaxy S25 en un escritorio Fedora ligero sobre Android, conservando Android como sistema principal. Termux:X11 presenta un escritorio Labwc 1920×1080; wlroots compone con Turnip/KGSL en Adreno 830. Chromium usa XWayland deliberadamente sin Vulkan propio, mientras el compositor continúa acelerado.

## Hardware objetivo y estado

- Samsung Galaxy S25, Snapdragon 8 Elite, Adreno 830
- Android 16 / One UI, Termux y Termux:X11
- Monitor externo 1920×1080, teclado y mouse físicos
- Estado validado: Labwc, Yambar, Plank, Chromium, Nautilus y LibreOffice

## Quick start

```sh
$HOME/MacDesk-V5/scripts/golden-state-check.sh
$HOME/MacDesk-V5/scripts/macdesk
```

Para cerrar: `$HOME/MacDesk-V5/scripts/macdesk-stop`. No ejecute `dnf upgrade`: consulte [VERSION-PINS.md](../VERSION-PINS.md).

## Arquitectura

Android → Termux → Fedora PRoot → Turnip/KGSL → wlroots 0.19 parcheado → Labwc → Termux:X11. Las aplicaciones Wayland y XWayland comparten el escritorio; PulseAudio cruza por loopback. Consulte [ARCHITECTURE.md](ARCHITECTURE.md).

## Screenshots

Pendiente: vista 1920×1080 del escritorio, Chromium y Nautilus.
