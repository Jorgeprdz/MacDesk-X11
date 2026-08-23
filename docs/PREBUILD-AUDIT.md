# MacDesk V6 prebuild audit

Status: PASS. No V5 or Fedora content was deleted.

## Regression inventory

| Generation | Retain | Reject or retest |
|---|---|---|
| V3 | Direct Termux:X11 + XFCE/XFWM architecture; simple session ownership; explicit Zink wrapper | Forced wallpaper; broad process killing; software desktop default; Thunar fallback; browser keyboard and restart regressions |
| V4 | Debian as the leaner guest; verified virpipe -> host Zink -> Turnip path; minimal XFCE components | Process-running acceptance; black desktop states; GLX/XShm failures; unproven persistent physical input |
| V5 | Host Turnip and KGSL knowledge; pinned Mesa revision; storage bridge; bookmarks; health checks; static Termux:X11 preference rule | Fedora paths; Labwc/wlroots; runtime preference broadcasts; GTK resource overlays; Nautilus internals/FIFO hacks; Tahoe CSS surgery |

Known browser/input regressions remain hard gates: three cold restart cycles, full Mexican Spanish input, physical mouse, Zen, and Chromium.

## Salvage manifest (planned and verified facts)

- GPU: Mesa commit `6dd2f2919e74a1e038485b1dd08eb062c4230ebb`, KGSL Turnip build knowledge, host `mesa-vulkan-icd-freedreno`, and virgl/Zink bridge.
- Storage: Termux shared storage mounted through `--shared-tmp`, stable `/mnt/s25 -> /sdcard`, direct mutation checks, and GTK bookmarks for Teléfono/Descargas/Cámara/Fotos/Documentos.
- Lifecycle: Termux:X11 preferences are static/offline. Startup and shutdown never write pointerCapture, fullscreen, or touchMode.

## Storage

- The superseded MacDesk V5 tree occupied approximately 191 MiB and was
  removed by the V6 legacy wipe on 2026-08-21. V6 has no runtime dependency on
  that tree.
- Fedora proot: approximately 6.0 GiB.
- Curated reusable payload: approximately 25–35 MiB (visual assets are deferred).
- Expected later reclaim: approximately 6.15 GiB.

Deletion is forbidden until V6 GPU, input, applications, storage, restart gates, and the final salvage manifest pass.
