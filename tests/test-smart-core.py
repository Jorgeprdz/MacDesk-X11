import json
import os
from pathlib import Path
import signal
import socket
import subprocess
import sys
import tempfile
import time
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts/lib'))


class CoreIntegration(unittest.TestCase):
    def test_socket_auth_override_and_user_process_survives_trim(self):
        with tempfile.TemporaryDirectory() as tmp:
            env = dict(os.environ, XDG_CONFIG_HOME=tmp+'/config', XDG_STATE_HOME=tmp+'/state',
                       XDG_CACHE_HOME=tmp+'/cache', MACDESK_RUNTIME=tmp+'/runtime', DISPLAY=':987')
            config = Path(tmp)/'config/macdesk'
            config.mkdir(parents=True)
            (config/'features.json').write_text(json.dumps(dict(desktop_mode=False, window_snap=False, dex_binding=False)))
            core = subprocess.Popen([sys.executable, str(ROOT/'scripts/macdesk-smart'), 'core'], env=env,
                                    stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
            user = subprocess.Popen(['sleep', '30'])
            try:
                for _ in range(100):
                    if (Path(tmp)/'runtime/token.json').exists():
                        break
                    if core.poll() is not None:
                        self.fail(core.stderr.read().decode())
                    time.sleep(.05)
                def send(payload):
                    with socket.socket(socket.AF_UNIX) as sock:
                        sock.settimeout(20)
                        sock.connect(tmp+'/runtime/core.sock')
                        sock.sendall(json.dumps(payload).encode()+b'\n')
                        result=b''
                        while b'\n' not in result:
                            result += sock.recv(65536)
                        return json.loads(result)
                self.assertFalse(send({'action': 'stop'})['ok'])
                token = json.loads((Path(tmp)/'runtime/token.json').read_text())
                self.assertTrue(send(dict(action='mode', mode='tablet', token=token))['ok'])
                self.assertTrue(send(dict(action='remote', enabled=True, token=token))['ok'])
                status = send(dict(action='status', token=token))['result']
                self.assertEqual(status['mode'], 'tablet')
                self.assertEqual(status['override'], 'tablet')
                self.assertTrue(send(dict(action='trim', token=token))['ok'])
                self.assertIsNone(user.poll())
                self.assertTrue(send(dict(action='stop', token=token))['ok'])
                self.assertEqual(core.wait(timeout=15), 0)
                self.assertFalse((Path(tmp)/'runtime/core.sock').exists())
            finally:
                if core.poll() is None:
                    core.terminate()
                core.wait(timeout=15)
                core.stderr.close()
                user.terminate()
                user.wait()

    def test_preview_group_cancellation_preserves_unrelated_process(self):
        from macdesk.core import Core
        with tempfile.TemporaryDirectory() as tmp:
            child = subprocess.Popen(['sh', '-c', 'sleep 30 & echo $! > "$1"; wait', 'sh', tmp+'/child'], start_new_session=True)
            other = subprocess.Popen(['sleep', '30'])
            try:
                for _ in range(100):
                    if Path(tmp+'/child').exists():
                        break
                    time.sleep(.01)
                descendant = int(Path(tmp+'/child').read_text())
                Core.stop_child(child)
                child.wait(timeout=5)
                time.sleep(.1)
                try:
                    data = Path(f'/proc/{descendant}/stat').read_text()
                    self.assertEqual(data[data.rfind(')')+2:].split()[0], 'Z')
                except FileNotFoundError:
                    pass
                self.assertIsNone(other.poll())
            finally:
                Core.stop_child(child)
                other.terminate()
                other.wait()


if __name__ == '__main__':
    unittest.main()
