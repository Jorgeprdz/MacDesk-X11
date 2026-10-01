#!/usr/bin/env bash
set -euo pipefail
root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"

bash -n "$root/scripts/setup-onlyoffice"
bash -n "$root/scripts/apply-office-storage-repair"
sh -n "$root/scripts/launch-nautilus"
sh -n "$root/scripts/launch-onlyoffice"
sh -n "$root/scripts/session-start"

grep -q "launch-onlyoffice" "$root/scripts/session-start"
grep -q "30-onlyoffice.dockitem" "$root/scripts/session-start"
grep -q "exec /usr/bin/nautilus" "$root/scripts/launch-nautilus"
grep -q "NoDisplay=true" "$root/config/plank/applications/macdesk-nautilus.desktop"
grep -q "NoDisplay=true" "$root/config/plank/applications/macdesk-onlyoffice.desktop"
grep -q "macdesk-nautilus.desktop" "$root/config/plank/launchers/10-nautilus.dockitem"
grep -q "macdesk-onlyoffice.desktop" "$root/config/plank/launchers/30-onlyoffice.dockitem"
grep -q "file:/// Sistema" "$root/config/storage/gtk-bookmarks"
grep -q "file:///mnt/s25 Teléfono" "$root/config/storage/gtk-bookmarks"

test ! -e "$root/config/plank/applications/org.gnome.Nautilus.desktop"
test ! -e "$root/config/plank/applications/onlyoffice-desktopeditors.desktop"

echo "OFFICE_STORAGE_CONTRACT=PASS"
