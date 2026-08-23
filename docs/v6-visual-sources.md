# V6 macOS Golden Gate visual sources

Visual installation is intentionally blocked until the functional golden state passes.

The definitive target is the macOS Golden Gate visual language on XFCE/XFWM.
No source theme is itself the acceptance target: each is only infrastructure or
reference material to adapt after the functional gate passes. The production dock
is Cairo-Dock; Plank is forbidden.

| Priority | Repository | Pinned commit | Intended use | License | Destination | Rollback |
|---|---|---|---|---|---|---|
| 1 | Local reference screenshots in `/sdcard/Download` | local acceptance oracle | Visual comparison only | user-provided | not copied yet | remove generated comparison artifacts |
| 2 | https://github.com/vinceliuice/WhiteSur-gtk-theme | PENDING CLONE | GTK/XFCE technical source to adapt toward Golden Gate | PENDING INSPECTION | `assets/themes/WhiteSur-gtk-theme` | remove installed theme and restore XFCE/GTK config snapshot |
| 3 | https://github.com/vinceliuice/MacTahoe-gtk-theme | `3c5551dcce983961cb5893212f8497ce991b5495` | Active selectable GoldenGate Light/Dark GTK3, GTK4 and compact XFWM profiles | MIT; local one-line no-sudo robustness modification | `vendor/visual-sources/MacTahoe-gtk-theme`, `assets/themes/GoldenGate-*`, `/usr/local/share/themes/GoldenGate-*` | `macdesk-theme rollback`; snapshots under `state/backups/mactahoe-trial-20260821` and `state/backups/tahoe-alt-20260821` |
| 4 | https://github.com/kayozxo/GNOME-macOS-Tahoe | `6735e7bffa49d4450c799e3c5a5dfbf2331b8760` | Optional Tahoe-Alt Light/Dark GTK3/GTK4 only; no GNOME Shell components adopted | MIT | `assets/themes/Tahoe-Alt-*` and `/usr/local/share/themes/Tahoe-Alt-*` | `macdesk-theme rollback` or `macdesk-theme current-dark`; current profiles remain intact |
| 5 | https://github.com/lassekongo83/adw-gtk3 | PENDING CLONE | Optional GTK3/GTK4 compatibility; must not redefine Golden Gate | PENDING INSPECTION | `assets/themes/adw-gtk3` | restore GTK settings and remove installed theme |
| 6 | https://github.com/vinceliuice/WhiteSur-icon-theme | `f6a78df1c9ea8c5f804b6c72d03408ca3db3521b` | Selectable WhiteSur default/light/dark icon profiles; Cupertino-Sonoma retained | GPL-3.0-or-later (COPYING) | `vendor/visual-sources/WhiteSur-icon-theme`, `assets/icons/WhiteSur*`, `/usr/local/share/icons/WhiteSur*` | `macdesk-theme rollback` restores Cupertino-Sonoma; WhiteSur assets remain installed |
| 7 | https://github.com/vinceliuice/WhiteSur-cursors | PENDING CLONE | Cursor source/reference | PENDING INSPECTION | `assets/themes/WhiteSur-cursors` | restore cursor setting and remove installed cursors |
| 8 | https://github.com/vinceliuice/WhiteSur-wallpapers | PENDING CLONE | Optional wallpaper source/reference | PENDING INSPECTION | `assets/themes/WhiteSur-wallpapers` | restore wallpaper setting and remove installed wallpapers |
| 9 | https://github.com/jereate/Cairo-dock-theme-Mactahoe-dark | `899df8526dbf2980e0feef8a10630a3aaa5005e6` | Primary Cairo-Dock geometry, background, indicators and selected icons; bundled unrelated launchers/plugins will not be adopted | GPL-3.0 | `vendor/visual-sources/Cairo-dock-theme-Mactahoe-dark`; curated runtime copy under `config/cairo-dock/` | restore the pre-theme runtime snapshot and reinstall V6-owned `config/cairo-dock/launchers` |
| 10 | https://github.com/USBA/Cupertino-Sonoma-iCons | `0c6afe6d2d25327e759b5be7f2e5e3ade265da54` | Active system/application icon theme; inherited Adwaita/hicolor coverage retained | Custom personal-use-only notice in `index.theme`; no standalone license file | pinned source plus `/usr/local/share/icons/Cupertino-Sonoma` symlink; selected by `config/xfce/xsettings.xml` | restore XFCE `IconThemeName` and remove the local icon symlink |

Exact commits, licenses, reused components, modifications, and install paths must
replace every PENDING value immediately after deferred read-only inspection.

The Cupertino source is not treated as an open-source redistributable dependency:
its own metadata says personal/fun use only and prohibits commercial use. V6 may
use a local personal installation, but must not relicense or publish those assets.

Visual acceptance requires `MAC_LOOK=PASS`, `MAC_FEEL=PASS`,
`VISUAL_COHERENCE=PASS`, and `MACOS_SHELL_LANGUAGE=PASS` against all available
local screenshots under `/sdcard/Download`. Package installation or theme loading
alone is never a visual pass.
