import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

from .common import ROOT, STATE, CONFIG, CACHE, flags, run, log_event


def preview_ui(path):
    if not shutil.which('gjs'):
        raise ValueError('GJS/GTK unavailable; bounded preview data is available with quicklook --describe')
    try:
        worker = subprocess.run([sys.executable, str(ROOT / 'scripts/macdesk-smart'),
                                 '_describe', path], capture_output=True, timeout=15, text=True)
        if worker.returncode:
            raise ValueError('File cannot be previewed within resource limits')
        data = json.loads(worker.stdout)
    except subprocess.TimeoutExpired:
        import signal
        if os.getpgrp() == os.getpid():
            os.killpg(os.getpgrp(), signal.SIGTERM)
        raise ValueError('Preview exceeded 15 second limit') from None
    # Replace the worker wrapper so the core owns the actual GTK UI PID.
    # JSON via a private temporary file; removed by the viewer immediately.
    import tempfile
    from .common import RUNTIME, private_dir
    private_dir(RUNTIME)
    fd, metadata = tempfile.mkstemp(prefix='preview-', suffix='.json', dir=RUNTIME)
    with os.fdopen(fd, 'w') as stream:
        json.dump(data, stream)
    os.execvp('gjs', ['gjs', str(ROOT / 'scripts/quicklook-viewer.js'), metadata])


def shortcuts():
    conflicts, installed = [], []
    ok, mapping = run(['xmodmap', '-pm'])
    if not ok or not any(line.startswith('mod4') and 'Super' in line for line in mapping.splitlines()):
        return {'installed': [], 'conflicts': ['Super is disabled by the existing MacDesk input contract; leave it unchanged.']}
    for key, zone in [('Left', 'left'), ('Right', 'right'), ('Up', 'up'), ('Down', 'down'), ('z', 'menu')]:
        prop = '/commands/custom/<Super>' + key
        occupied, value = run(['xfconf-query', '-c', 'xfce4-keyboard-shortcuts', '-p', prop])
        wm_occupied, _ = run(['xfconf-query', '-c', 'xfce4-keyboard-shortcuts', '-p', '/xfwm4/custom/<Super>' + key])
        import shlex
        command = shlex.join([str(ROOT / 'scripts/macdesk-smart'), 'snap', zone])
        if (occupied and value != command) or wm_occupied:
            conflicts.append(key)
            continue
        if occupied or run(['xfconf-query', '-c', 'xfce4-keyboard-shortcuts', '-p', prop,
                            '-n', '-t', 'string', '-s', command])[0]:
            installed.append(key)
    return dict(installed=installed, conflicts=conflicts)


def diagnostics():
    tools = ('python3', 'gjs', 'wmctrl', 'xdotool', 'xprop', 'xrandr', 'xfconf-query',
             'inotifywait', 'ffmpeg', 'ffprobe', 'pdftoppm', 'magick', 'convert',
             'file', 'gio', 'adb', 'rish', 'termux-open', 'termux-open-url')
    from .core import request
    try:
        context = request('status')
    except (OSError, ValueError):
        context = {'core': 'not running'}
    return dict(tools={name: shutil.which(name) for name in tools}, features=flags(),
                context=context, state=str(STATE), config=str(CONFIG), cache=str(CACHE))


def install():
    import shlex
    scripts = Path.home() / '.local/share/nautilus/scripts'
    scripts.mkdir(parents=True, exist_ok=True)
    for label, action in [('MacDesk Quick Look', 'quicklook'), ('Open in Android', 'open-android'), ('Share with Android', 'share')]:
        target = scripts / label
        if not target.exists():
            target.write_text('#!/usr/bin/env python3\nimport os, subprocess\n'
                'paths = os.environ.get("NAUTILUS_SCRIPT_SELECTED_FILE_PATHS", "").splitlines()\n'
                'if len(paths) == 1:\n'
                f'    subprocess.Popen([{str(ROOT / "scripts/macdesk-smart")!r}, {action!r}, paths[0]])\n')
            target.chmod(0o700)
    for name, action in [('macdesk-core', 'core'), ('macdesk-mode', 'mode'),
                         ('macdesk-snap', 'snap'), ('macdesk-quicklook', 'quicklook'),
                         ('macdesk-memory', 'memory'), ('macdesk-open-android', 'open-android'),
                         ('macdesk-share', 'share')]:
        target = Path('/usr/local/bin') / name
        if not target.exists():
            target.write_text('#!/bin/sh\nexec ' + shlex.join(['python3', str(ROOT / 'scripts/macdesk-smart'), action]) + ' "$@"\n')
            target.chmod(0o755)
    return {'installed': True, 'shortcuts': shortcuts() if flags()['super_shortcuts'] else 'opt-in; existing keyboard contract preserved'}


def main(argv=None):
    parser = argparse.ArgumentParser(description='MacDesk optional smart desktop commands')
    parser.add_argument('command', choices=('core', 'stop', 'status', 'diagnostics', 'mode',
                         'display', 'memory', 'snap', 'shortcuts', 'quicklook', 'open-android',
                         'share', 'storage', 'android-status', 'event', 'install', '_describe', '_preview'))
    parser.add_argument('args', nargs='*')
    parser.add_argument('--describe', action='store_true')
    parser.add_argument('--window')
    args = parser.parse_args(argv)
    from .core import request
    try:
        command, values = args.command, args.args
        if command == 'core':
            from .core import Core
            return Core().serve()
        if command in ('_describe', '_preview'):
            if len(values) != 1:
                raise ValueError('Expected file')
            if command == '_describe':
                from .preview import worker
                worker(values[0])
            else:
                preview_ui(values[0])
            return 0
        if command in ('status', 'stop'):
            result = request(command)
        elif command == 'diagnostics':
            result = diagnostics()
        elif command == 'install':
            result = install()
        elif command == 'mode':
            result = request('mode', mode=values[0]) if values else request('status')
        elif command == 'display':
            from .context import Android, preferred_display
            snapshot = Android().snapshot()
            if values == ['bind']:
                result = {'bound': Android().bind(preferred_display(snapshot['displays']))}
            else:
                result = snapshot
        elif command == 'memory':
            result = request('trim' if values == ['trim'] else 'memory-ui' if values == ['ui'] else 'memory')
        elif command == 'snap':
            from .snap import snap, ZONES
            if not flags()['window_snap']:
                raise ValueError('Window Snap disabled')
            if values == ['menu']:
                ok, wid = run(['xdotool', 'getactivewindow'])
                if not ok or not wid.isdecimal():
                    raise ValueError('No active window')
                os.execvp('gjs', ['gjs', str(ROOT / 'scripts/snap-menu.js'), str(ROOT / 'scripts/macdesk-smart'), wid])
            result = {'zones': list(ZONES)} if not values else {'snapped': snap(values[0], args.window)}
        elif command == 'shortcuts':
            result = shortcuts()
        elif command == 'event':
            if values in (['remote-on'], ['remote-off']):
                result = request('remote', enabled=values[0] == 'remote-on')
            elif values in (['low-memory'], ['critical-memory']):
                result = request('pressure', level=values[0].split('-')[0])
            elif values == ['refresh']:
                result = request('refresh')
            else:
                raise ValueError('event refresh|remote-on|remote-off|low-memory|critical-memory')
        elif command == 'quicklook':
            if len(values) != 1 or not flags()['quicklook']:
                raise ValueError('Expected one file and quicklook=true')
            path = str(Path(values[0]).expanduser().resolve(strict=True))
            if args.describe:
                from .preview import worker
                worker(path)
                return 0
            try:
                result = request('preview', path=path)
            except (FileNotFoundError, ConnectionRefusedError):
                child = subprocess.Popen([sys.executable, str(ROOT / 'scripts/macdesk-smart'), '_preview', path], start_new_session=True)
                try:
                    return child.wait()
                except KeyboardInterrupt:
                    from .core import Core
                    Core.stop_child(child)
                    return 130
        elif command in ('open-android', 'share', 'storage', 'android-status'):
            from .continuity import open_android, storage_links, status
            if not flags()['continuity']:
                raise ValueError('Continuity disabled')
            if command == 'storage':
                result = storage_links()
            elif command == 'android-status':
                result = status()
            else:
                if len(values) != 1:
                    raise ValueError('Expected URL or file')
                result = {'opened': open_android(values[0], share=command == 'share')}
        print(json.dumps(result, ensure_ascii=False, indent=2))
        if command in ('snap', 'quicklook', 'open-android', 'share', 'mode', 'memory'):
            log_event('continuity' if command in ('open-android', 'share') else command, 'command completed')
        return 0
    except (OSError, ValueError, KeyError, IndexError) as error:
        print('MacDesk: ' + str(error), file=sys.stderr)
        try:
            log_event('commands', args.command + ': ' + type(error).__name__)
        except OSError:
            pass
        return 1
