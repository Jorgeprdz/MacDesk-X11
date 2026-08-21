# S25 Neo phone storage

S25 Neo presents Android shared storage as a first-class location named **Teléfono**.

## Data path

`Android /storage/emulated/0` → Termux `~/storage/shared` → PRoot `/sdcard` → stable alias `/mnt/s25` → Nautilus bookmarks.

No files are copied. `proot-distro` supplies the existing `/sdcard` bind and `scripts/s25-storage-prepare` creates only the stable `/mnt/s25` symbolic link. Private application data, `Android/data`, and `Android/obb` are intentionally outside the supported scope.

## Startup and health

`scripts/macdesk` runs `scripts/s25-storage-prepare` before Fedora's desktop session. Missing Termux storage permission does not prevent the desktop from starting; the log reports `S25_STORAGE_PERMISSION=REQUIRED` and `PHONE_STORAGE=UNAVAILABLE`. Grant access once with `termux-setup-storage`, then restart MacDesk.

The preparation script checks real Download, DCIM, Pictures, Documents, Movies and Music directories. It performs an isolated create/read/rename/delete test in Download and removes its own temporary file. Results are written to `state/storage.env`.

Nautilus bookmarks are managed in `/home/macdesk/.config/gtk-3.0/bookmarks` with friendly Spanish names. Linux Home remains separate.

## Rollback

Run `scripts/s25-storage-rollback`. It removes only the managed bookmark lines and removes `/mnt/s25` only when it is the managed link to `/sdcard`. It never removes phone content.

Termux:X11 fullscreen is likewise session-scoped: `macdesk` saves preferences and enables fullscreen; `macdesk-stop` restores the saved preferences before stopping X11.
