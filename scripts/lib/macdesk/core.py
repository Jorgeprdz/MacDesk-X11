"""One optional event loop. Never stops XFCE, X11, or user applications."""
import fcntl
import json
import logging
from logging.handlers import RotatingFileHandler
import os
from pathlib import Path
import selectors
import secrets
import signal
import socket
import struct
import subprocess
import sys
import time

from .common import CONFIG, ROOT, RUNTIME, STATE, flags, private_dir, read_json, write_json
from .context import Android, Governor, MODES, choose_mode, preferred_display
from .profiles import Profiles


class Core:
    def __init__(self):
        self.features = flags()
        self.context = dict(android_available=False, foreground=None, remote=False)
        self.governor = Governor()
        self.profiles = Profiles()
        self.children = {}  # only subprocess.Popen objects created here
        self.stop = False
        self.last_target = None
        self.pending_refresh = None
        self.pending_android = None
        self.android = Android()
        self.override = read_json(CONFIG / 'display-mode', 'auto')
        if self.override not in MODES:
            self.override = 'auto'
        self.log = logging.getLogger('macdesk-core')
        private_dir(STATE)
        handler = RotatingFileHandler(STATE / 'core.log', maxBytes=128*1024, backupCount=2)
        handler.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
        self.log.addHandler(handler)
        self.log.setLevel(logging.INFO)
        self.last_mode = None

    @staticmethod
    def stop_child(child):
        if child.poll() is None:
            try:
                # Every helper is born in its own session. This group contains
                # only its decoder/UI descendants, never XFCE or user apps.
                os.killpg(child.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass

    def trim(self, critical=False):
        from .preview import prune_cache
        from .memory import measure
        before = measure(os.getpid(), self.children)
        for pid, child in list(self.children.items()):
            if child.poll() is not None:
                del self.children[pid]
            elif self.governor.state in ('BACKGROUND', 'SUSPENDED') or critical:
                # Popen owns this child until reaped: no untrusted PID registry.
                self.stop_child(child)
        prune_cache(limit=0)
        self.log.info('memory trim state=%s helpers_before_kib=%s', self.governor.state, before['helpers_kib'])
        return dict(before=before, after=measure(os.getpid(), self.children))

    def refresh(self, android=False):
        from .snap import monitors
        if android:
            snapshot = self.android.snapshot()
            # Replace stale Android state instead of retaining disconnected DeX.
            for key in ('external', 'dex_active', 'display_id', 'visibility', 'diagonal_inches', 'touch', 'mouse', 'keyboard'):
                self.context.pop(key, None)
            self.context.update(snapshot)
            target = preferred_display(snapshot.get('displays', []))
            fingerprint = tuple(target.get(k) for k in ('id', 'name', 'width', 'height')) if target else None
            if self.features['dex_binding'] and fingerprint != self.last_target:
                # Initial phone-only startup should not steal focus. A real
                # external->phone transition may move the existing Activity.
                if target and (target['role'] in ('DEX', 'EXTERNAL') or self.last_target):
                    if self.android.bind(target):
                        self.last_target = fingerprint
                        self.log.info('display bind role=%s id=%s', target['role'], target['id'])
                elif not target:
                    self.last_target = None
        geometry = monitors()
        if geometry:
            self.context['monitors'] = geometry
            self.context['width'], self.context['height'] = geometry[0][2:]
        mode = choose_mode(self.context, self.override)
        if self.features['desktop_mode'] and mode != self.last_mode:
            self.profiles.apply(mode, self.features['window_snap'])
            self.log.info('desktop-mode %s -> %s override=%s', self.last_mode, mode, self.override)
        elif not self.features['desktop_mode'] and self.features['window_snap'] and self.last_mode is None:
            self.profiles.deltas.apply({'xfwm4:/general/tile_on_move': 'true'})
            write_json(self.profiles.path, self.profiles.deltas.state)
        self.last_mode = mode
        self.context['mode'] = mode
        self.context['override'] = self.override
        self.context['governor'] = self.governor.state
        write_json(STATE / 'context.json', self.context)

    def preview(self, path):
        if not self.features['quicklook']:
            raise ValueError('Quick Look disabled')
        path = str(Path(path).expanduser().resolve(strict=True))
        if not Path(path).is_file():
            raise ValueError('Not a regular file')
        # At most one recreatable Quick Look UI. No application process lookup.
        for child in self.children.values():
            if child.poll() is None:
                self.stop_child(child)
        child = subprocess.Popen([sys.executable, str(ROOT / 'scripts/macdesk-smart'), '_preview', path],
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
        self.children[child.pid] = child
        return {'pid': child.pid, 'module': 'quicklook', 'purpose': 'file preview', 'recreatable': True}

    def dispatch(self, request):
        action = request.get('action')
        if action == 'status':
            return dict(self.context, governor=self.governor.state, features=self.features)
        if action == 'mode':
            mode = request.get('mode')
            if mode not in MODES:
                raise ValueError('Invalid mode')
            self.override = mode
            write_json(CONFIG / 'display-mode', mode)
            self.refresh()
            return self.context
        if action == 'refresh':
            self.pending_refresh = time.monotonic() + .5
            self.pending_android = time.monotonic() + .5
            return {'scheduled': True}
        if action == 'remote':
            if type(request.get('enabled')) is not bool:
                raise ValueError('Expected boolean')
            self.context['remote'] = request['enabled']
            self.refresh()
            return self.context
        if action == 'memory':
            from .memory import measure
            return dict(measure(os.getpid(), self.children), mode=self.governor.state)
        if action == 'memory-ui':
            import tempfile
            from .memory import measure
            snapshot = dict(measure(os.getpid(), self.children), mode=self.governor.state)
            fd, filename = tempfile.mkstemp(prefix='preview-', suffix='.json', dir=RUNTIME)
            with os.fdopen(fd, 'w') as stream:
                json.dump(dict(title='MacDesk Memory', text=json.dumps(snapshot, indent=2), image=None), stream)
            child = subprocess.Popen(['gjs', str(ROOT / 'scripts/quicklook-viewer.js'), filename],
                                     start_new_session=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self.children[child.pid] = child
            return {'pid': child.pid, 'refresh': 'snapshot on open; no background refresh'}
        if action == 'trim':
            return self.trim()
        if action == 'pressure':
            if request.get('level') not in ('low', 'critical'):
                raise ValueError('Invalid pressure level')
            return self.trim(critical=request['level'] == 'critical')
        if action == 'preview':
            return self.preview(request['path'])
        if action == 'stop':
            self.stop = True
            return {'stopping': True}
        raise ValueError('Unknown action')

    def serve(self):
        private_dir(RUNTIME)
        lock = (RUNTIME / 'core.lock').open('a')
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return 0
        path = RUNTIME / 'core.sock'
        path.unlink(missing_ok=True)
        server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        server.bind(str(path))
        path.chmod(0o600)
        # PRoot rewrites SO_PEERCRED differently for local and cross-PRoot
        # peers. A fresh capability in the same 0700 directory authenticates
        # clients without relying on virtual UIDs or protected /proc data.
        token = secrets.token_hex(32)
        write_json(RUNTIME / 'token.json', token)
        server.listen(4)
        selector = selectors.DefaultSelector()
        selector.register(server, selectors.EVENT_READ, 'client')
        # Signal wakeup pipe: terminate/reap with no periodic process scan.
        rfd, wfd = os.pipe2(os.O_NONBLOCK | os.O_CLOEXEC)
        signal.set_wakeup_fd(wfd)
        signal.signal(signal.SIGTERM, lambda *_: setattr(self, 'stop', True))
        signal.signal(signal.SIGINT, lambda *_: setattr(self, 'stop', True))
        signal.signal(signal.SIGCHLD, lambda *_: None)
        selector.register(rfd, selectors.EVENT_READ, 'signal')
        events = None
        try:
            from .xevents import XEvents
            events = XEvents()
            selector.register(events, selectors.EVENT_READ, 'x11')
        except (OSError, AttributeError):
            self.log.info('X11 event source unavailable; explicit hooks remain active')
        self.log.info('core started pid=%s', os.getpid())
        next_android = time.monotonic() + self.features['android_interval']
        self.refresh(android=True)
        try:
            while not self.stop:
                now = time.monotonic()
                state = 'REMOTE' if self.context.get('remote') else self.context.get('visibility', 'ACTIVE')
                if self.features['memory_governor'] and self.governor.update(state, now):
                    self.trim()
                deadlines = [next_android]
                if self.pending_refresh is not None:
                    deadlines.append(self.pending_refresh)
                if self.pending_android is not None:
                    deadlines.append(self.pending_android)
                if self.features['memory_governor'] and not self.governor.trimmed and state in ('BACKGROUND', 'SUSPENDED', 'IDLE'):
                    deadlines.append(self.governor.since + (60 if state == 'IDLE' else 10))
                for key, _ in selector.select(max(0, min(deadlines)-now)):
                    if key.data == 'signal':
                        os.read(rfd, 4096)
                        self.children = {p: c for p, c in self.children.items() if c.poll() is None}
                    elif key.data == 'x11':
                        if events.drain():
                            self.pending_refresh = time.monotonic() + .5
                            # X11 resize invalidates Android roles, debounced.
                            self.pending_android = time.monotonic() + 1
                    else:
                        conn, _ = server.accept()
                        with conn:
                            conn.settimeout(1)
                            try:
                                data = b''
                                while b'\n' not in data and len(data) <= 65536:
                                    block = conn.recv(4096)
                                    if not block:
                                        break
                                    data += block
                                if len(data) > 65536:
                                    raise ValueError('Request too large')
                                payload = json.loads(data)
                                if not isinstance(payload, dict) or not isinstance(payload.get('token'), str) or not secrets.compare_digest(payload['token'], token):
                                    raise ValueError('Unauthenticated request')
                                result = {'ok': True, 'result': self.dispatch(payload)}
                            except (ValueError, OSError, KeyError, TypeError) as error:
                                result = {'ok': False, 'error': str(error)}
                                self.log.warning('request rejected: %s', error)
                            try:
                                conn.sendall((json.dumps(result) + '\n').encode())
                            except OSError:
                                pass
                now = time.monotonic()
                android_due = now >= next_android or (self.pending_android is not None and now >= self.pending_android)
                if android_due or (self.pending_refresh is not None and now >= self.pending_refresh):
                    try:
                        self.refresh(android=android_due)
                    except (OSError, ValueError) as error:
                        self.log.warning('refresh failed: %s', error)
                    self.pending_refresh = None
                    if android_due:
                        self.pending_android = None
                        next_android = time.monotonic() + self.features['android_interval']
        finally:
            # No PID files accepted, no user apps killed, no X11 reset.
            for child in self.children.values():
                if child.poll() is None:
                    self.stop_child(child)
            self.profiles.restore()
            path.unlink(missing_ok=True)
            (RUNTIME / 'token.json').unlink(missing_ok=True)
            if events:
                events.close()
            selector.close()
            server.close()
            signal.set_wakeup_fd(-1)
            os.close(rfd)
            os.close(wfd)
            lock.close()
        return 0


def request(action, **kwargs):
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as conn:
        conn.settimeout(20)
        conn.connect(str(RUNTIME / 'core.sock'))
        token = read_json(RUNTIME / 'token.json', '')
        conn.sendall((json.dumps(dict(action=action, token=token, **kwargs)) + '\n').encode())
        output = b''
        while b'\n' not in output and len(output) < 1024*1024:
            block = conn.recv(65536)
            if not block:
                break
            output += block
        result = json.loads(output)
        if not result['ok']:
            raise ValueError(result['error'])
        return result['result']
