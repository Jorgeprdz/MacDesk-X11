#!/usr/bin/env bash
set -euo pipefail
root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
grep -q "launch-onlyoffice" "$root/scripts/session-start"
grep -q "30-onlyoffice.dockitem" "$root/scripts/session-start"
grep -q "GoldenGate-Light" "$root/scripts/launch-nautilus"
grep -q "file:/// Sistema" "$root/config/storage/gtk-bookmarks"
grep -q "file:///mnt/s25 Teléfono" "$root/config/storage/gtk-bookmarks"
test -f "$root/config/plank/applications/org.gnome.Nautilus.desktop"
test -f "$root/config/plank/applications/onlyoffice-desktopeditors.desktop"
test -f "$root/config/plank/launchers/10-nautilus.dockitem"
test -f "$root/config/plank/launchers/30-onlyoffice.dockitem"
echo "OFFICE_STORAGE_CONTRACT=PASS"
