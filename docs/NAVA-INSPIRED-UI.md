# MacDesk — Nava-inspired interface, optional proof of concept

This is an independently authored visual interpretation of the Nava OS
public design previews. It contains no official Nava OS code, imagery or
logos. **Not tested on the physical Galaxy S25 or DeX.**

## What works in principle

The existing Debian + XFCE/XFWM + Termux:X11 + Plank desktop is retained.
Two original Plank backgrounds imitate the cool, floating glass palette
without requiring a second compositor. XFCE's top-panel background and GTK
theme are adjusted while preserving the existing GoldenGate window engine.
The small keyboard-first launcher delegates to XFCE App Finder.

This is **not** the true Liquid Glass refractive/blur compositor and does not
implement a Nava OS Control Center. XFWM transparency is just compositing.

## Activate (inside the Debian/XFCE graphical terminal)

    cd /root/MacDesk-V6
    sh scripts/macdesk-nava-style plan
    sh scripts/macdesk-nava-style apply-dark
    # alternatively: sh scripts/macdesk-nava-style apply-light
    sh scripts/macdesk-nava-command

Check and undo:

    sh scripts/macdesk-nava-style status
    sh scripts/macdesk-nava-style rollback

The first apply snapshots the existing Plank, GTK, XFWM and XFCE panel
settings under ~/.local/state/macdesk-nava/. Further light/dark changes do
not replace this snapshot. Rollback restores the original values.

Run in Debian/XFCE, not the host Termux environment, so commands can access
the active X11 display and user D-Bus session. No global Super shortcut is
registered because MacDesk has an unresolved DeX/Super keyboard conflict.

## Gates before calling it delivered

- Static shell and theme format checks.
- Actual activation and rollback on Galaxy S25, DeX 1920x1080.
- Dock restarts and geometry changes, XFCE panel rgba handling.
- SAFE_FALLBACK and Turnip/Zink stability, RSS/CPU checks.
- Persistence after restart: current MacDesk session code may reset the Plank
  theme to GoldenGate on next session; reapply in the graphical session.
- Regression: keyboard, focus, Nautilus, Firefox, recovery, stable themes.
- No merge until physical validation and user approval.
