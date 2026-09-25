# MacDesk Apps — Nautilus M0

Branch: `feature/macdesk-apps-nautilus-m0`

## Goal

Run the existing MacDesk Nautilus stack as the first standalone MacDesk app surface in DeX, with no XFCE desktop visible.

Success criteria for M0:

1. Nautilus launches through the existing `scripts/launch-nautilus` path.
2. No XFCE panel, wallpaper, Plank, or desktop shell is required for Nautilus.
3. Nautilus has its own Android/DeX task/window identity.
4. The Linux process remains on the shared X server so later Linux-to-Linux XDND drag & drop remains possible.
5. Closing the Nautilus Android task closes only the Nautilus presentation, not the shared X server/runtime.

## Existing runtime to preserve

The current `scripts/launch-nautilus` already contains the production fixes that must not regress:

- Nautilus 48 root-delay bypass.
- stable Cairo/GSK path.
- disabled inherited Mesa/virpipe variables for Nautilus.
- PRoot thumbnailer workaround.
- D-Bus private-session fallback.
- private Finder-style Nautilus build under `/opt/macdesk-nautilus-finderbar` with Debian fallback.

Do not rewrite those behaviors in the Android layer.

## Confirmed architectural gap

The current MacDesk repository stores the built standalone Termux:X11 APK and integration scripts, but not the Termux:X11 Android/native source tree.

Current Termux:X11 behavior is one Android activity/surface for one X display. That is not sufficient for MacDesk Apps.

M0 therefore requires a source-level Termux:X11-derived host that can map one selected top-level X11 window to one Android Surface/Activity/Task while the X server remains shared.

## M0 implementation direction

Use upstream `termux/termux-x11` as the renderer/server base.

Add a MacDesk app-window mode with a first hard-scoped target:

- WM_CLASS / app identity: Nautilus
- Linux launch command: `scripts/launch-nautilus`
- Android task label: Files
- resizable: true
- multi-window capable: true
- no forced portrait orientation
- independent task affinity/document task behavior

The first implementation must not fake independence by launching the normal Termux:X11 MainActivity. The Android task must display the Nautilus top-level X11 window itself.

## Explicit non-goals for M0

- Firefox
- Google Docs
- Android↔Linux drag and drop
- theming changes
- AVF/NPVM migration
- replacing PRoot
- multiple Linux windows in one Android task

Those come only after Nautilus is genuinely independent.

## M0 acceptance test

On the Galaxy S25 in DeX:

1. Launch Files.
2. One DeX window opens whose Android task is Files.
3. That window contains Nautilus only.
4. Alt+Tab shows Files independently from Termux/Termux:X11.
5. Resize/maximize/snap work.
6. Existing Nautilus thumbnails, Finder bar, Quick Look, shared Android storage and keyboard/mouse behavior still work.
7. Closing Files does not terminate the shared Linux/X11 runtime.

