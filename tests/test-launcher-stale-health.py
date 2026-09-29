"""An old PASS must not turn a failed new launch into a successful start."""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
ROOT = Path(__file__).resolve().parents[1]

class LauncherHealthTests(unittest.TestCase):
    def test_failed_new_guest_does_not_reuse_previous_pass(self):
        source = (ROOT / 'scripts/macdesk').read_text()
        function = source[source.index('healthy_session() {'):source.index('\nif [ -f "$STATE/guest.pid" ]')]
        launch = source[source.index('# SAFE_FALLBACK does not start'):]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'bin').mkdir()
            command = root / 'bin/proot-distro'
            command.write_text('#!/bin/sh\nexit 1\n')
            command.chmod(0o755)
            (root / 'session-check.env').write_text('\n'.join(
                f'{key}=PASS' for key in ('X11_SERVER', 'DBUS_SESSION', 'XFCONF', 'XFCE_SESSION', 'XFWM', 'XFCE_PANEL')) + '\n')
            result = subprocess.run(['bash', '-c',
                'set -eu\nSTATE="$1"; LOGS="$1"; GUEST_ROOT=/root/MacDesk-V6; DISPLAY_NUM=:2\n'
                'focus_x11_activity() { :; }\n' + function + '\n' + launch, 'test', tmp],
                env={**os.environ, 'PATH': str(root / 'bin') + ':' + os.environ['PATH']},
                capture_output=True, text=True, timeout=8)
            self.assertNotEqual(result.returncode, 0, result.stdout)
            self.assertNotIn('MACDESK_V6=RUNNING', result.stdout)

if __name__ == '__main__': unittest.main()
