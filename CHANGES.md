# MacDesk V6 changes

## 2026-08-22 — Nautilus Quick Look, thumbnails and Finder bar

- Installed the minimal missing HEIF/GdkPixbuf runtime support while retaining
  GNOME Sushi 46 and all existing thumbnailers.
- Configured verified Nautilus 48 keys for always-on previews and a 256 MiB
  limit; backed up and reset only the regenerable thumbnail cache.
- Added a stable software-rendered Sushi D-Bus wrapper and a Nautilus-only
  private-bus fallback for stale long-running PRoot session buses.
- Fixed nested bubblewrap thumbnail generation under PRoot using the upstream
  already-containerized path, scoped only to Nautilus.
- Added a reproducible Nautilus 48.3 patch and private `/opt` payload with a
  native Finder-style bottom bar: live item/selection counts, selection size,
  filesystem free space and real bidirectional zoom controls.
- Kept Debian `/usr/bin/nautilus` unchanged and tested install/remove/status,
  system fallback, patch dry-run and restoration of the original package set.
- Physical Space Quick Look and actual JPEG/PNG/SVG/WebP/PDF/video/HEIC
  thumbnail generation passed.

Documentation: `docs/NAUTILUS-PREVIEW-FINDERBAR.md`.

## 2026-08-22 — Firefox primary browser and Liquid Fox Linux port

- Replaced Zen with Firefox ESR 140 as the XFCE, XDG, MIME, and Plank default.
- Added `scripts/launch-firefox` with the existing Adreno 830 / Turnip / Zink
  environment, stable software page composition, integrated title bar, and
  idempotent routing to the existing primary Firefox window.
- Vendored Liquid Fox commit `3dfcc8d4f1b3a392eef8b065f34287d7135d4e1d`.
  The upstream CSS is unchanged in `liquid-fox.css`; `userChrome.css` supplies
  the Linux/XFCE ARGB fallback for macOS-only vibrancy.
- Enabled Firefox's native vertical tabs on the left; the sidebar remains
  collapsible between icons-only and titled-tab layouts.
- Keeps 16 px Liquid Fox rounding for internal panels. Native outer-window
  rounding was rejected: Firefox/X11 stayed rectangular and transparent
  clipping flashed during resize. The Linux port uses an opaque top-level
  surface for stable repainting.
- Preserved standalone Firefox/Chromium app profiles and excluded them from
  primary-browser start/stop/health matching.
- Replaced the Zen Plank item with the WhiteSur Firefox item while preserving
  the bottom-geometry guard.
- Validated the GPU path with Adreno/Turnip/Zink EGL, GLES, OpenGL, Vulkan, and
  a live WebGL/resize smoke test: 936 frames, five resize cycles, zero stalls.
- Firefox presentation uses GLX rather than EGL: EGL-on-X11 produced visible
  WebRender surface corruption during live use. WebGL still uses Adreno through
  the same Turnip/Zink Mesa stack.
- Hardware WebRender was subsequently disabled because GLX still reproduced
  the corruption. Stable software page composition is used; WebGL remains
  forced on and resolves through the Adreno Mesa stack.
- Kept `MOZ_GTK_TITLEBAR_DECORATION=client`. The `system` and `none` modes were
  rejected because XFWM added a second 28 px title bar. This leaves the outer
  X11 surface square, while preserving Liquid Fox rounding inside the window.
- Removed Liquid Fox's inner card highlight and Firefox 140's revamp
  `#tabbrowser-tabbox` outline; GoldenGate rendered those perimeters as a hard
  cyan frame. Interactive focus indicators such as the URL field are retained.
- Backed up the Zen profile to shared storage before uninstalling it.

Rollback:

- Project files: `backups/firefox-primary-migration-20260822-183741/`.
- Firefox profile/session: `backups/firefox-theme-pre-restart-20260822-185141/`.
- Zen profile archive:
  `/sdcard/Download/MacDesk-Backups/Zen-profile-pre-uninstall-20260822-183741.tar.gz`.
