#!/usr/bin/env bash
set -euo pipefail
root=$(cd -- "$(dirname -- "$0")/.." && pwd)
test -f "$root/install.sh" || { echo 'FAIL: all-in-one installer missing'; exit 1; }
bash -n "$root/install.sh"
bash "$root/install.sh" --help | grep -q -- '--check'
# These paths must be safe outside Termux and must not run package managers.
bash "$root/install.sh" --plan | grep -q 'xfce4'
if bash "$root/install.sh" --definitely-invalid >/dev/null 2>&1; then
  echo 'FAIL: invalid option accepted'; exit 1
fi
if env PREFIX=/tmp/not-termux bash "$root/install.sh" --check >/dev/null 2>&1; then
  echo 'FAIL: accepted non-Termux environment'; exit 1
fi
env MACDESK_GPU_PROFILE=SAFE_FALLBACK GALLIUM_DRIVER=zink LIBGL_DRIVERS_PATH=/missing \
  sh -c '. "$1/config/gpu/env.sh"; test "${LIBGL_ALWAYS_SOFTWARE:-}" = 1; test -z "${GALLIUM_DRIVER:-}"; test -z "${LIBGL_DRIVERS_PATH:-}"' sh "$root"
source "$root/install.sh"
test_dir=$(mktemp -d)
trap 'rm -rf -- "$test_dir"' EXIT
mkdir -p "$test_dir/repo with spaces/scripts" "$test_dir/bin"
cat > "$test_dir/repo with spaces/scripts/macdesk" <<'APP'
#!/usr/bin/env bash
printf '%s\n%s\n' "$(dirname -- "${BASH_SOURCE[0]}")" "$1"
APP
chmod +x "$test_dir/repo with spaces/scripts/macdesk"
install_launcher "$test_dir/bin/macdesk" "$test_dir/repo with spaces/scripts/macdesk" "$BASH"
output=$("$test_dir/bin/macdesk" 'space ü ; literal')
[[ "$output" == "$test_dir/repo with spaces/scripts"$'\n''space ü ; literal' ]]
before=$(cat "$test_dir/bin/macdesk")
install_launcher "$test_dir/bin/macdesk" /wrong/path "$BASH" >/dev/null
[[ "$(cat "$test_dir/bin/macdesk")" == "$before" ]]
printf 'ALL_IN_ONE_INSTALLER=PASS\n'
