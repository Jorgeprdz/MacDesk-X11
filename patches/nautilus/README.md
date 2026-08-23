# Nautilus 48.3 Finder-style bottom bar

UPSTREAM_NAUTILUS_VERSION=48.3-2

PATCH_VERSION=2

PATCH_FILE=patches/nautilus/nautilus-48.3-finderbar-v2.patch

This patch adds a native GTK bottom bar to every `NautilusFilesView`. It uses
the existing `NautilusViewModel` for item counts, the existing selection model
for selection count and size, `nautilus_file_get_volume_free_space()` for the
asynchronous filesystem-aware free-space value, and `NautilusListBase`'s real
zoom levels and `notify::icon-size` signal for bidirectional synchronization.

There is no external window, overlay process, shell polling loop, `df` loop, or
second preference store. Grid view exposes its five native levels. List view
exposes its three native levels. Views with no zoom range disable the slider.

Patch version 2 retains Nautilus's native Space shortcut. The MacDesk launcher
first verifies the XFCE session bus and, only when that stale PRoot socket no
longer accepts clients, starts Nautilus on one private `dbus-run-session`.
GNOME Sushi then uses its normal upstream D-Bus integration; no global shortcut
or second desktop session is introduced.

The Debian `/usr/bin/nautilus` is never replaced. The private binary is shipped
under `assets/nautilus-finderbar/48.3/` and installed under
`/opt/macdesk-nautilus-finderbar`. `scripts/launch-nautilus` automatically
falls back to Debian Nautilus whenever the private installation marker is
absent.

Commands from the MacDesk project path inside Debian:

```sh
/data/data/com.termux/files/home/MacDesk-V6/scripts/macdesk-nautilus-finderbar install
/data/data/com.termux/files/home/MacDesk-V6/scripts/macdesk-nautilus-finderbar status
/data/data/com.termux/files/home/MacDesk-V6/scripts/macdesk-nautilus-finderbar remove
```

`remove` deletes only the private prefix. It does not touch user files,
bookmarks, settings, thumbnail caches, GNOME Sushi, or the Debian package.

To rebuild, install the development packages documented in
`docs/NAUTILUS-PREVIEW-FINDERBAR.md`, then run
`scripts/build-nautilus-finderbar` inside Debian. The build script uses the
project-local `deb-src` definition and applies the exact versioned patch.
