# MacDesk V6

Reproducible Galaxy S25 DeX desktop based on Debian, Termux:X11, XFCE, and Adreno/Turnip acceleration.

Gate order is strict: GPU -> stable desktop -> applications -> Android storage -> performance -> visuals -> physical input -> regression.

## Recovery status (2026-09-29)

Android's phantom-process trimming was confirmed as the cause of repeated
Codex and desktop SIGKILL events. The device now has
`settings_enable_monitor_phantom_procs=false`. Normal XFCE startup, an owned
stop/restart, and a real X11 test window pass in `SAFE_FALLBACK` software graphics.
Shutdown validates process ownership; new launches require fresh health results.

This is a recovery baseline, **not a new full-product acceptance**. External DeX,
physical input, application coverage, and the six smart-desktop additions still
need their current-device acceptance. D-Bus clients in a separate PRoot session
remain unable to authenticate to the desktop bus; in-session checks pass.

See [Android process recovery](docs/ANDROID-PROCESS-RECOVERY.md) and
[remaining smart-desktop scope](docs/SMART-DESKTOP-SCOPE.md). The older hardware,
UID, rendering and resolution claims below are historical, not current evidence.

## Historical acceptance (2026-08-21)

Recorded status: **daily-computer and bug-resolution PASS**.
Debian, XFCE/XFWM, host VirGL, the DeX keyboard contract, dynamic display
recovery, Chromium app keyboard bridges, Plank geometry recovery, and the
in-session health monitor are installed and survived a full phone reboot.

Firefox ESR is the primary browser. It uses the verified Adreno 830 -> Turnip
-> Zink path with WebRender/EGL and the Linux/XFCE port of Liquid Fox. Zen was
removed after repeated GTK/X11 freezes; its last profile backup is retained in
shared storage under `Download/MacDesk-Backups`.

Termux:X11 standalone `1.03.01-f68cd36-21.08.26` is installed with Android UID
10423, isolated from Termux UID 10602. The old shared-UID force-stop hazard no
longer applies. `scripts/restart-termux-x11-safe` remains the supported restart
path.

The final resolution is native 1920x1080 at 100% scale. The rejected 75%
experiment was completely rolled back because it produced visible pixelation;
no monitor-connect scaling automation remains.

Operational commands:

- `macdesk`: start or focus V6.
- `macdesk-resume`: detect the current DeX display, focus X11, and recover V6
  only when X11/XFWM are not healthy.
- `scripts/check-dex-keyboard.sh`: keyboard/accessibility regression gate.
- `scripts/measure-stability`: RSS, swap, process and Android exit history.
- `scripts/migrate-termux-x11-external.sh`: host-side standalone migration;
  retained for provenance/recovery and never run from Termux.
- `scripts/launch-whatsapp`: isolated Chromium WhatsApp window with its scoped
  physical-keyboard bridge.
- `scripts/launch-chatgpt`: isolated Chromium ChatGPT window with its scoped
  physical-keyboard bridge.
- `scripts/launch-firefox`: primary Firefox launcher with Adreno acceleration,
  Liquid Fox, single-instance focus, and safe URL/tab routing.
- `scripts/plank-geometry-guard`: realigns Plank after DeX/XRandR resizing.

Final evidence and the signed-off defect matrix are recorded in
`docs/MACDESK-V6-BUG-RESOLUTION-CERTIFICATE.md`.
