# Nautilus standalone app — M0

## Goal

Make Nautilus the first MacDesk app that is conceptually independent from a
Linux desktop. The user should ultimately open **Files** from DeX and receive a
normal Android task whose content is the real Nautilus process.

## Implemented in M0

1. A dedicated app runtime display, `:3`, separate from MacDesk V6 `:2`.
2. `scripts/launch-nautilus-app` starts only Termux:X11 server state and one
   Nautilus guest process.
3. No XFCE, XFWM, Plank, VirGL, desktop wallpaper, or desktop panel.
4. Nautilus runs on a private D-Bus session and reuses the existing canonical
   MacDesk Nautilus wrapper, preserving:
   - Finder-style bottom bar;
   - Quick Look/Sushi integration;
   - Android storage view;
   - GTK theme/customizations;
   - stable Cairo/software renderer path.
5. `com.macdesk.shell/.NautilusActivity` is a resizable DeX task named
   **Files** with its own Android `SurfaceView`.
6. The activity invokes only the Nautilus runtime launcher. It never opens the
   Termux:X11 desktop activity.
7. M0 has an explicit static contract test.

## M1 gate: X11 top-level window -> Android Surface

M0 intentionally does **not** claim seamless rendering is complete.

The missing bridge must:

- observe top-level X windows on the MacDesk Apps X server;
- match the Nautilus window by XID / WM_CLASS;
- bind that single window's buffers to the Surface owned by
  `NautilusActivity`;
- translate Android task size changes into X configure events;
- translate pointer, wheel and keyboard input into the matching X window;
- preserve X selections/XDND inside the shared MacDesk Apps server;
- keep the X server invisible as an Android desktop activity.

Success criteria for M1:

1. Tap **Files** in DeX.
2. One Android task named **Files** appears.
3. Nautilus renders inside that task.
4. No XFCE desktop and no Termux:X11 activity becomes visible.
5. Move/resize/maximize/minimize works using DeX controls.
6. Closing the task does not affect MacDesk V6 on `:2`.

## Why a dedicated display now

Using `:3` lets us develop the app/window bridge without destabilizing the
known-good daily MacDesk V6 desktop on `:2`. Once the bridge is stable,
Firefox and Chromium web-app windows can share the same Apps X server so Linux
clipboard and XDND drag-and-drop remain native between them.
