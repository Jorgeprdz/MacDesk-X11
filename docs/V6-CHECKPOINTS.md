# MacDesk V6 checkpoints

> Registro cronológico. El checkpoint final inmediatamente siguiente es el
> estado vigente; las palabras `pending`, `deferred` o referencias a shared UID
> en secciones posteriores describen el estado histórico de ese momento.

## Final stabilization and bug-resolution checkpoint (2026-08-21)

- The standalone Termux:X11 `1.03.01-f68cd36-21.08.26` package is installed as
  UID 10423, isolated from Termux UID 10602. The migration and post-reboot
  validation are complete.
- The accepted physical keyboard contract passes Ctrl+T, Ctrl+C, Ctrl+V and
  native DeX Alt+Tab. The X11 accessibility KeyInterceptor is disabled, no
  keyboard filter owns DeX Display 6, and the input guard prevents a latched
  modifier.
- WhatsApp runs in a dedicated Chromium profile on the stable software-rendered
  path. A localhost-only DevTools bridge forwards physical X11 keyboard input
  only while the WhatsApp page has focus. The owner physically confirmed text
  entry and shortcuts.
- ChatGPT has an equivalent standalone Chromium launcher, separate profile and
  local keyboard bridge. It is persisted in the Plank launcher order and was
  physically accepted.
- `plank-geometry-guard` debounces root-window changes and restarts only Plank
  when its dock window no longer matches the root width or bottom edge. A live
  1920x1080 check measured the dock at `0,904`, size `1920x176`, ending exactly
  at Y=1080. The owner also passed the resize test.
- A full phone reboot returned Termux:X11, VirGL, XFCE, XFWM, D-Bus, Zen,
  terminal, WhatsApp and the persisted ChatGPT launcher. Keyboard shortcuts
  remained functional after reboot.
- The requested 75% external-monitor scale was tested and rejected because it
  rendered visibly pixelated. It was fully rolled back: resolution mode is
  `native`, scale is 100, fullscreen is true, the root is 1920x1080, separate
  secondary-display preferences are disabled, and no scale-on-connect
  automation remains in the source tree.
- Final certificate: `docs/MACDESK-V6-BUG-RESOLUTION-CERTIFICATE.md`.

## Persisted recovery baseline

- `PREBUILD_AUDIT=PASS`
- `VISUAL_TARGET=macOS Golden Gate`
- `DOCK=Plank`
- V5 and Fedora are retained until the functional golden state and salvage manifest pass.
- Post-reboot recovery is active; direct Turnip Vulkan has reconfirmed Adreno 830.
- The recovered runtime's EGL probe hung, so it is not accepted as evidence and will be retested after a clean owned-PID restart.

## GPU post-reboot recovery

- `GPU_DRIVER=TURNIP`, `VULKAN=PASS`, `EGL=PASS`, `GLES=PASS`, `OPENGL=PASS`.
- `SOFTWARE_RENDERER=NO`; renderer is `virgl (Adreno (TM) 830)`.
- Virgl now uses multi-client mode so XFCE and health checks can coexist.

## Deferred final gate: stuck Super modifier

- Physical observation indicates Super/Mod4 remains active after release.
- Application, storage, Cairo-Dock, and visual work proceed in the safe non-latching state; final physical keyboard acceptance remains deferred.
- Read-only cross-layer instrumentation is active; no Termux:X11 preference has been changed.

### Diagnostic checkpoint: FAIL

- Baseline raw press was Super keycode 133 but raw release was Alt keycode 64,
  leaving XKB Mod4 at `0x40` for subsequent normal keys.
- The tested static preference matrix either removed Super entirely, left
  Control stuck, or translated physical Super as Control.
- First proven failing layer: Samsung DeX / Termux:X11 Lorie key translation.
- Safe interim state prevents a stuck modifier but does not expose Super, so the
  Super sub-gate remains open. See `docs/STUCK-SUPER-TRACE.md`.

## Split-track decision

- Track A continues all functional gates that do not require Super.
- Track B independently repairs Samsung DeX / Termux:X11 Super translation.
- The safe non-latching preference state is frozen until Track B has a proven
  replacement; no preference combination that latches Mod4 may be restored.
- Visual work remains forbidden until the functional golden-state decision is
  revisited after both tracks have evidence.

### Split-track checkpoint

- Track A: all physical mouse, click, scroll, focus, drag, and edge/corner
  resize tests pass. Letters, numbers, and Shift pass. Accents/specials and
  Ctrl/Alt shortcuts do not yet pass; Mod4 also recreated after focus/modifier
  testing, so application acceptance remains unsafe.
- Track B: exact Java-to-JNI translation path identified in current upstream.
  A narrow Samsung Meta-release canonicalization patch is prepared but not
  built or installed. See `docs/SUPER-SOURCE-REPAIR.md`.

## Application/storage checkpoint (2026-08-20)

- Official Zen Browser `1.21.15b` Linux ARM64 archive was checksum-verified and installed. A real 875x526 X11 browser window rendered; Zen is the default browser.
- Chromium `151.0.7922.169` launches and renders an X11 window, but its GPU subprocess repeatedly exits with status 1 and Chromium falls back to `--use-gl=disabled`; `CHROMIUM_GPU=FAIL` remains open without changing the global GPU path.
- LibreOffice `25.2.3.2` Writer, Calc, and Impress each rendered 1920x920 windows. LibreOffice created a valid ODT in Android Documents and reopened it in Writer.
- Nautilus `48.3` rendered an X11 window and is configured as the XFCE/default directory handler. Legacy Thunar failsafe autostart is removed from the V6 user session definition.
- `/mnt/s25 -> /sdcard` exists. Read, write, create, rename, and delete mutations passed in Android Documents; GTK bookmarks cover Teléfono, Descargas, Cámara, Fotos, and Documentos.

## Cairo-Dock functional checkpoint (2026-08-20)

Historical checkpoint, superseded by the Plank migration below.

- `CAIRO_DOCK_LAUNCH=PASS`: Cairo-Dock 3.5.1 autostarts as a real 1920x106 X11 dock using direct OpenGL 4.3 on virgl/Adreno 830.
- An owned stop/start preserved the adopted Termux:X11 process, recreated virgl, and restored XFCE, XFWM compositing, panel, Cairo-Dock, and the fully accelerated global GPU path.
- The pinned Mactahoe-dark source (`899df8526dbf2980e0feef8a10630a3aaa5005e6`, GPL-3.0) supplies curated dock geometry, background, and indicators. Its unrelated launchers and heavyweight plug-ins were excluded.
- V6 launchers for Nautilus, Zen, Chromium, Terminal, and LibreOffice returned after restart; Applications and Trash remain the only enabled applets. Early idle samples were approximately 1.3% Cairo, 1.3% panel, 1.9% XFWM, and 1.4% xfdesktop.
- `CAIRO_DOCK_CLICK`, `CAIRO_DOCK_HOVER`, and fullscreen behavior still require physical interaction validation, so the component result is `PARTIAL` rather than final PASS.

## Plank migration checkpoint (2026-08-21)

- Plank `0.11.89` replaces Cairo-Dock in the live session and in XFCE autostart; no Cairo-Dock process or autostart entry remains active.
- The existing GoldenGate-Light and GoldenGate-Dark Plank themes are installed from the V6 assets. The active `current-light` profile selects `GoldenGate-Light`.
- Applications, Show Desktop, Nautilus, Zen, WhatsApp, Chromium, Terminal, LibreOffice, App Store, and Trash persist as the curated dock order.
- The Applications, Show Desktop, and Trash entries use Plank's required `docklet://` launcher URI; this prevents the three empty-launcher gear icons produced by the invalid `Docklet=` form.
- App Store launches Synaptic instead of GNOME Software. GNOME Software cannot initialize its PackageKit plugins without a system D-Bus in PRoot; Synaptic opened a real X11 package-manager window and manages Debian APT directly.
- XFWM compositing is enabled and owns `_NET_WM_CM_S0`; Plank zoom is disabled to avoid the prior disappearing-icon animation artifact.
- On the Galaxy S25/DeX path, XFWM uses `vblank=off`: `auto` produced a physical black screen, while `off` preserves compositing and restores visible XFCE output.
- Turnip, EGL, GLES, OpenGL, Vulkan, XFCE, XFWM, panel, D-Bus, Termux:X11, and VirGL checks pass after the owned session restart. Software rendering remains absent.
- Physical acceptance: the owner confirmed that XFCE starts and is visible with Plank and the compositor enabled.
- All 29 historical evidence captures under `logs/` were reviewed and intentionally removed at the owner's request; no PNG/JPG evidence capture remains there.

## Golden Gate visual checkpoint (2026-08-21)

- Tahoe-Dark GTK3 and generated GTK4 styling, Cupertino-Sonoma icons, MacTahoe XFWM traffic-light controls, Golden Gate wallpaper, dark menu bar, and curated Mactahoe Cairo-Dock persist across owned restarts.
- The visual captures used for this checkpoint were reviewed and later removed at the owner's request.
- Zen and LibreOffice rendered real themed windows; Android Documents remained writable. Nautilus/storage had already passed the application gate and its process still launches, but final physical interaction remains pending.
- Idle sample: XFWM 1.4%, xfdesktop 1.0%, Cairo-Dock 0.8%, panel 0.6% CPU.
- Final `REAL_MAC_FEEL` remains pending physical visual and dock interaction acceptance.

### Nautilus/XFWM regression correction

- Nautilus 48.3 source contains an unconditional `sleep(7)` for UID 0; measured cold and warm baselines were both about 7.2 seconds. A Nautilus-only shim skips exactly that intentional seven-second delay while retaining the root session's working D-Bus/GVFS/storage path.
- Real-window timing after correction: cold 1.29 seconds, warm 0.99 seconds. Android Documents remained writable.
- The initially selected MacTahoe `hdpi` XFWM assets produced a 42px title bar. Standard-density assets reduce it to 28px with 24px controls; terminal capture confirms compact geometry and optical title centering.

### Physical acceptance (2026-08-21)

- User confirmed: `KEYBOARD=PASS`, `MOUSE=PASS`, `VISUAL=PASS`, `NAUTILUS=PASS`, and `ZEN=PASS` on the real DeX display.

### Alt+Tab and shared-UID crash correction (2026-08-21)

- User physically confirmed `ALT_TAB=PASS` after restoring the known-good
  Termux:X11 keyboard preferences and keeping its Accessibility KeyInterceptor
  disabled.
- `WRITE_SECURE_SETTINGS` is revoked from `com.termux.x11`, preventing silent
  KeyInterceptor reactivation. Other enabled accessibility services were
  preserved.
- Android reports no accessibility `KeyboardInterceptor` on DeX Display 8.
  Key Mapper and Essentials request key filtering on the phone display only;
  DeX Corners, SwiftSlate, and Smartspacer do not request key filtering.
- Termux and Termux:X11 share Android UID 10602. The prior interruptions were
  caused by an X11 package update and `am force-stop com.termux.x11`, both of
  which stop the shared Termux process. V6 now uses an in-process preference
  receiver and process-level X11 restart; a controlled restart preserved the
  Termux PID and returned X11, VirGL, XFCE, and XFWM to PASS.
- The global HappyMac `macdesk` entry point now targets V6; no V5 process
  remains after startup.

## Selectable theme profiles (2026-08-21)

- MacTahoe `3c5551dcce983961cb5893212f8497ce991b5495`: isolated `GoldenGate-Light` and `GoldenGate-Dark` GTK3/GTK4/XFWM profiles with 28px decorations.
- GNOME-macOS-Tahoe `6735e7bffa49d4450c799e3c5a5dfbf2331b8760`: optional `Tahoe-Alt-Light` and `Tahoe-Alt-Dark` GTK profiles; GNOME Shell excluded and compact GoldenGate XFWM retained.
- Commands: `macdesk-theme current-light`, `current-dark`, `tahoe-light`, `tahoe-dark`, or `rollback`. Only V6-owned desktop processes restart; Termux:X11 is preserved.
- Four-profile rollback/XFCE/dock/storage checks pass. The temporary screenshots were removed after review. Physical four-profile acceptance remains pending.

### XFWM traffic-light recovery (2026-08-21)

- Root cause: XFWM searched `/usr/share/themes`, while the installed GoldenGate profiles were only reachable under `/usr/local/share/themes`; XFWM therefore fell back to `Default` and hid the traffic-light pixmaps.
- Fix: `scripts/session-start` now creates owned `/usr/share/themes/{GoldenGate-Light,GoldenGate-Dark,Tahoe-Alt-Light,Tahoe-Alt-Dark,MacDesk-GoldenGate}` symlinks to the V6 theme assets.
- Verified after `macdesk-theme current-dark`: runtime `theme=GoldenGate-Dark`, `button_layout=CHM|`, compact 28px title bar, visible red/yellow/green controls, and centered title; DBus/XFCE/XFWM/panel checks PASS. The temporary capture was removed after review.

### WhiteSur icon profile (2026-08-21)

- WhiteSur icon source pinned at `f6a78df1c9ea8c5f804b6c72d03408ca3db3521b` (GPLv3, `COPYING`), installed as `WhiteSur`, `WhiteSur-light`, and `WhiteSur-dark`.
- `macdesk-theme current-dark` now selects `WhiteSur-dark`; the prior Cupertino-Sonoma source and installed link remain untouched.
- Runtime verification: XFCE reports `IconThemeName=WhiteSur-dark`, GoldenGate-Dark/XFWM traffic lights remain active, and session checks pass. The temporary capture was removed after review.
- `macdesk-theme rollback` restores Cupertino-Sonoma without deleting WhiteSur.

### Wallpaper persistence (2026-08-21)

- `scripts/session-start` no longer overwrites the live `/root/.config/xfce4/.../xfce4-desktop.xml` on restart. The repository wallpaper remains a first-boot default only; a user-selected wallpaper is preserved across owned MacDesk restarts.

### Nautilus WhiteSur icon visibility (2026-08-21)

- Nautilus and the desktop session now inherit `/usr/local/share:/usr/share` through `XDG_DATA_DIRS`, and the session applies the configured GTK icon theme through GSettings. This makes WhiteSur discoverable to GTK4/Nautilus while leaving Cupertino-Sonoma installed.
- User screenshot then showed Nautilus using a pixelated low-resolution fallback. WhiteSur `places` now explicitly includes 48px and 64px directories (copied from the scalable assets), icon caches were regenerated, and each GTK4 profile has `settings.ini` with `gtk-icon-theme-name=WhiteSur[-dark]`.
- A second runtime check identified the effective fallback as Debian Adwaita. WhiteSur folder SVGs are now overlaid only at `/usr/share/icons/Adwaita/scalable/places/`, with originals backed up at `/usr/local/share/icons/Adwaita.macdesk-v6-backup`; Cupertino-Sonoma remains untouched and rollback is reversible.
- The reported white glyphs were also present in WhiteSur's own symbolic folder set. For the dark profile, `places/symbolic/folder*-symbolic.svg` now uses the colored scalable WhiteSur artwork; originals are backed up at `/usr/local/share/icons/WhiteSur-dark.macdesk-v6-symbolic-backup`.
