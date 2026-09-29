#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "$0")/.." && pwd)"
termux_home="/data/data/com.termux/files/home/MacDesk-V6"

guest_files=(
  scripts/session-start
  scripts/session-health-supervisor
  scripts/plank-geometry-guard
  config/xfce/xfce4-desktop.xml
  config/xfce/xfce4-panel.xml
)

for relative in "${guest_files[@]}"; do
  if grep -Fq "$termux_home" "$repo_root/$relative"; then
    echo "Guest config uses inaccessible Termux-private path: $relative" >&2
    exit 1
  fi
done

# Dynamic launcher/root initialization is checked by test-xfce-startup-contract.sh.
# This test rejects host-private paths in guest configuration.
echo GUEST_REPO_PATHS=PASS
