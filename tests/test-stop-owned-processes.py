"""A stale PID file must never terminate an unrelated live process."""
import os
from pathlib import Path
import subprocess
import tempfile
import sys
import time
import unittest

ROOT = Path(__file__).resolve().parents[1]

class OwnedStopTests(unittest.TestCase):
    def test_unrelated_live_pid_is_refused(self):
        with tempfile.TemporaryDirectory() as home:
            state = Path(home) / 'MacDesk-V6/state'
            state.mkdir(parents=True)
            child = subprocess.Popen(['sleep', '60'])
            try:
                pidfile = state / 'input-guard.pid'
                pidfile.write_text(str(child.pid))
                # Load the real stop function, without running the global shutdown.
                definitions = (ROOT / 'scripts/macdesk-stop').read_text().split(
                    '# Stop the owned session.', 1)[0]
                result = subprocess.run(['bash', '-c', definitions + '\nstop_pid_file "$1"',
                                         'stop-test', str(pidfile)],
                                        env={**os.environ, 'HOME': home},
                                        capture_output=True, text=True, timeout=10)
                self.assertIsNone(child.poll(), 'shutdown killed an unrelated process from a stale PID file')
                self.assertNotEqual(result.returncode, 0, 'must report refusal')
                self.assertTrue(pidfile.exists(), 'preserve refused state for diagnosis')
            finally:
                if child.poll() is None:
                    child.terminate()
                child.wait()

    def test_unrelated_process_with_guard_path_argument_is_refused(self):
        with tempfile.TemporaryDirectory() as home:
            base = Path(home) / 'MacDesk-V6'
            (base / 'state').mkdir(parents=True)
            child = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(60)',
                                      str(base / 'scripts/input-guard')])
            try:
                time.sleep(.1)
                pidfile = base / 'state/input-guard.pid'
                pidfile.write_text(str(child.pid))
                definitions = (ROOT / 'scripts/macdesk-stop').read_text().split(
                    '# Stop the owned session.', 1)[0]
                result = subprocess.run(['bash', '-c', definitions + '\nstop_pid_file "$1"',
                                         'stop-test', str(pidfile)],
                                        env={**os.environ, 'HOME': home},
                                        capture_output=True, text=True, timeout=10)
                self.assertIsNone(child.poll(), 'script path in data arguments is not ownership')
                self.assertNotEqual(result.returncode, 0)
            finally:
                if child.poll() is None:
                    child.terminate()
                child.wait()

    def test_owned_guard_stops_and_removes_pid_file(self):
        with tempfile.TemporaryDirectory() as home:
            base = Path(home) / 'MacDesk-V6'
            (base / 'scripts').mkdir(parents=True)
            (base / 'state').mkdir()
            script = base / 'scripts/input-guard'
            script.write_text("#!/bin/bash\ntrap 'exit 0' TERM\nwhile :; do sleep .1; done\n")
            child = subprocess.Popen(['bash', str(script)])
            try:
                time.sleep(.1)
                pidfile = base / 'state/input-guard.pid'
                pidfile.write_text(str(child.pid))
                definitions = (ROOT / 'scripts/macdesk-stop').read_text().split(
                    '# Stop the owned session.', 1)[0]
                result = subprocess.run(['bash', '-c', definitions + '\nstop_pid_file "$1"',
                                         'stop-test', str(pidfile)],
                                        env={**os.environ, 'HOME': home},
                                        capture_output=True, text=True, timeout=10)
                self.assertEqual(result.returncode, 0, result.stderr)
                child.wait(timeout=2)
                self.assertFalse(pidfile.exists())
            finally:
                if child.poll() is None:
                    child.terminate()
                child.wait()

if __name__ == '__main__':
    unittest.main()
