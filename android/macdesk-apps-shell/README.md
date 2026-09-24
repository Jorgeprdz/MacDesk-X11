# MacDesk Apps Shell — Nautilus M0

This is the first ChromeOS-style MacDesk application host.

## M0 contract

- Android/DeX owns the task and window.
- The launcher starts a dedicated MacDesk Apps X display on `:3`.
- No XFCE, Plank, desktop shell, compositor, or VirGL is started.
- Nautilus gets a private D-Bus session, so the existing V6 Nautilus on `:2`
  cannot absorb the request.
- `NautilusActivity` owns a dedicated Android `SurfaceView` and task identity
  ("Files").
- The Android task never opens or focuses the Termux:X11 desktop Activity.

## Current boundary

The X11 client is launched and isolated, and the Android task/surface exists,
but the top-level Nautilus X window is not yet attached to that Android
`SurfaceView`. That X11-window-to-Surface bridge is M1 and is the only missing
piece before Nautilus can actually render inside the independent DeX task.

The bootstrap still uses Termux RUN_COMMAND intentionally. The final MacDesk APK
will internalize the Linux runtime after the window bridge is proven.
