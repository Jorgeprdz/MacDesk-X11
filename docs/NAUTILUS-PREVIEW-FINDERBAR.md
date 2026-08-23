# MacDesk V6 — Nautilus preview, thumbnails and Finder bar

Date: 2026-08-22

## Platform

- Debian: 13 (trixie), arm64
- Nautilus package: 48.3-2
- GTK 4: 4.18.6
- GLib: 2.84.4
- GNOME Sushi: 46.0-2
- MacDesk X display: `:2`

## Quick Look

Nautilus 48 already binds unmodified Space to the
`view.preview-selection` action. GNOME Sushi remains D-Bus activated and runs
through `scripts/launch-sushi-previewer`, which selects Cairo/llvmpipe because
Zink fails to create a Vulkan instance for this GTK previewer under Android.

A long-lived Debian PRoot can leave XFCE and X11 healthy while its original
D-Bus socket closes new client connections. `scripts/launch-nautilus` tests
that socket. It keeps the normal XFCE bus when healthy; otherwise it runs only
Nautilus in one `dbus-run-session`. This is not a second desktop, file manager,
X server or XFCE session. Sushi then uses its normal upstream D-Bus API.

Physical validation: selecting a PNG and pressing Space repeatedly opened and
closed the GNOME Sushi preview successfully.

## Thumbnail pipeline

Nautilus is configured only through keys that exist in
`org.gnome.nautilus.preferences`:

- `show-image-thumbnails='always'`
- `thumbnail-limit=uint64 256` MiB

The existing JPEG/PNG, SVG, PDF, video and WebP thumbnailers were retained.
HEIF support adds `heif-thumbnailer` and `heif-gdk-pixbuf`; the GdkPixbuf cache
tool adds `libgdk-pixbuf2.0-bin`.

libgnome-desktop 44 normally nests every thumbnailer inside bubblewrap.
PRoot's virtual `/tmp` is not a kernel-visible bind source, so bubblewrap
recorded valid generators as failed. `scripts/launch-nautilus` sets
`SNAP_NAME=macdesk-proot` for Nautilus only, selecting libgnome-desktop's
upstream no-nested-sandbox path. Debian itself remains contained by Android
and PRoot; no global library or thumbnailer definition is modified.

Actual sample generation passed for JPEG, PNG, SVG, WebP, PDF, MP4 and HEIC.
The Nautilus integration test generated eight files in
`~/.cache/thumbnails/large` and zero entries in `fail`.

## Native Finder-style bar

The versioned patch inserts one native `GtkCenterBox` into every
`NautilusFilesView`. It uses:

- `NautilusViewModel` item and selection signals;
- Nautilus file metadata for asynchronous selection sizes;
- `nautilus_file_get_volume_free_space()` for the active filesystem;
- `NautilusListBase` native zoom levels and `notify::icon-size`.

There is no external window, overlay, polling loop, `df` loop, CSS zoom or
second settings store. Grid has its five native levels and list has its three
native levels. The bar uses GTK `.toolbar` and `.dim-label` styles, so it
inherits light/dark theme colors and typography without hardcoded colors.

Observed tests passed for an empty directory, a populated directory, live item
creation, one/multiple selections with combined size, free space, minus/plus,
minimum/medium/maximum zoom, grid/list view, and both directions of zoom sync.

## Rebuild and rollback

Version metadata:

```text
UPSTREAM_NAUTILUS_VERSION=48.3-2
PATCH_VERSION=2
PATCH_FILE=patches/nautilus/nautilus-48.3-finderbar-v2.patch
```

Build prerequisites are temporary and are not part of the runtime image:

```sh
apt-get install --no-install-recommends build-essential meson ninja-build gettext \
  libadwaita-1-dev libglib2.0-dev libgnome-autoar-0-dev \
  libgnome-desktop-4-dev libgtk-4-dev libportal-gtk4-dev \
  libtracker-sparql-3.0-dev
```

Then run `scripts/build-nautilus-finderbar`. The checked-in payload is installed
without replacing `/usr/bin/nautilus`:

```sh
scripts/macdesk-nautilus-finderbar install
scripts/macdesk-nautilus-finderbar status
scripts/macdesk-nautilus-finderbar remove
```

`remove` deletes only `/opt/macdesk-nautilus-finderbar`; the launcher
automatically falls back to Debian Nautilus. The remove/fallback/install cycle
was tested successfully.

Primary backup:

`backups/preview-thumbnails-20260822-194608/`

