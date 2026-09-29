"""Conservative context decisions. Unknown Android signals remain unknown."""
import re
import os
import math
import shlex
import shutil
from .common import run

MODES = ('auto', 'phone', 'tablet', 'desktop', 'remote')


def parse_displays(text):
    displays = {}
    for line in text.splitlines():
        if 'DisplayInfo{' not in line or 'displayId ' not in line:
            continue
        identity = re.search(r'displayId (\d+)', line)
        geometry = re.search(r'\breal (\d+) x (\d+)', line)
        name = re.search(r'DisplayInfo\{"([^"]*)"', line)
        kind = re.search(r'\btype (\w+)', line)
        state = re.search(r'\bstate (\w+)', line)
        density = re.search(r'\bdensity (\d+)', line)
        physical = re.search(r'density \d+ \(([\d.]+) x ([\d.]+)\) dpi', line)
        if not identity or not geometry or not kind:
            continue
        display_id = int(identity[1])
        label = name[1] if name else ''
        external = kind[1] == 'EXTERNAL'
        dex = bool(re.search(r'\bDeX\b|desktop', label, re.I)) and display_id != 0
        # A non-default ID alone never identifies an external monitor.
        role = 'DEX' if dex else 'EXTERNAL' if external else 'PHONE' if kind[1] == 'INTERNAL' else 'UNKNOWN'
        displays[display_id] = dict(id=display_id, name=label, type=kind[1], role=role,
                                   width=int(geometry[1]), height=int(geometry[2]),
                                   density=int(density[1]) if density else None,
                                   active=bool(state and state[1] == 'ON'))
        if physical and min(map(float, physical.groups())) > 40:
            displays[display_id]['diagonal_inches'] = math.hypot(int(geometry[1])/float(physical[1]), int(geometry[2])/float(physical[2]))
    return list(displays.values())


def preferred_display(displays):
    usable = [d for d in displays if d['active'] and d['role'] != 'UNKNOWN']
    priority = {'DEX': 0, 'EXTERNAL': 1, 'PHONE': 2}
    return min(usable, key=lambda d: (priority[d['role']], d['id']), default=None)


def choose_mode(context, override='auto'):
    if override in MODES and override != 'auto':
        return override
    if context.get('remote'):
        return 'remote'
    scores = {'phone': 1, 'tablet': 0, 'desktop': 0}
    if context.get('external'):
        scores['desktop'] += 5
    if context.get('keyboard') and context.get('mouse'):
        scores['desktop'] += 2
    if context.get('touch') and context.get('diagonal_inches', 0) >= 7:
        scores['tablet'] += 4
    # Resolution is corroborating evidence only, never physical size.
    if context.get('width', 0) > context.get('height', 0) and scores['desktop']:
        scores['desktop'] += 1
    return max(scores, key=scores.get)


class Governor:
    def __init__(self):
        self.state = 'ACTIVE'
        self.since = 0
        self.trimmed = False

    def update(self, state, now):
        if state not in ('ACTIVE', 'IDLE', 'BACKGROUND', 'REMOTE', 'SUSPENDED'):
            raise ValueError('Invalid governor state')
        if state != self.state:
            self.state, self.since, self.trimmed = state, now, False
        delay = 10 if state in ('BACKGROUND', 'SUSPENDED') else 60
        if state in ('BACKGROUND', 'SUSPENDED', 'IDLE') and not self.trimmed and now - self.since >= delay:
            self.trimmed = True
            return True
        return False


def visibility(windows):
    focused = re.findall(r'mCurrentFocus=([^\n]+)', windows)
    if not focused:
        return None
    if any('com.termux.x11/' in f for f in focused):
        return 'ACTIVE'
    blocks = re.split(r'(?:^|\n)\s*Window #\d+ Window\{', windows)
    x11 = [b for b in blocks[1:] if 'com.termux.x11/' in b.split('\n', 1)[0]]
    if not x11:
        return None
    if any(re.search(r'\bisVisible=true|\bisOnScreen=true', b) for b in x11):
        return 'IDLE'
    if all(re.search(r'\bisVisible=false|\bisOnScreen=false', b) for b in x11):
        return 'BACKGROUND'
    return None


def parse_inputs(text):
    result = dict(touch=False, keyboard=False, mouse=False)
    for block in re.split(r'\n\s*Device \d+:', text)[1:]:
        sources = re.search(r'Sources: ([^\n]+)', block)
        if not sources:
            continue
        result['touch'] |= 'TOUCHSCREEN' in sources[1]
        if 'IsExternal: true' in block:
            result['mouse'] |= 'MOUSE' in sources[1]
            # Android's power/volume buttons are keyboards of type 1.
            result['keyboard'] |= 'KEYBOARD' in sources[1] and 'KeyboardType: 2' in block
    return result


class Android:
    def __init__(self):
        self.adb = shutil.which(os.environ.get('MACDESK_ADB', 'adb'))
        if not self.adb:
            self.adb = shutil.which('/data/data/com.termux/files/usr/bin/adb')

    def shell(self, *args):
        if not self.adb:
            return False, ''
        # adb shell reparses argv remotely. Quote at that exact boundary.
        return run([self.adb, 'shell', shlex.join(map(str, args))], timeout=5)

    def snapshot(self):
        ok, output = self.shell('dumpsys', 'display')
        if not ok:
            return {'android_available': False, 'displays': [], 'foreground': None}
        displays = parse_displays(output)
        target = preferred_display(displays)
        result = dict(android_available=True, displays=displays, foreground=None,
                      external=bool(target and target['role'] in ('DEX', 'EXTERNAL')),
                      dex_active=bool(target and target['role'] == 'DEX'),
                      display_id=target['id'] if target else None)
        if target and target['role'] == 'PHONE' and 'diagonal_inches' in target:
            result['diagonal_inches'] = target['diagonal_inches']
        ok, inputs = self.shell('dumpsys', 'input')
        if ok:
            result.update(parse_inputs(inputs))
        # Samsung puts mCurrentFocus in the displays section, not windows.
        ok, windows = self.shell('dumpsys', 'window')
        detected = visibility(windows) if ok else None
        if detected:
            result['foreground'] = detected == 'ACTIVE'
            result['visibility'] = detected
        if displays and not any(d['active'] for d in displays):
            result['visibility'] = 'SUSPENDED'
        return result

    def bind(self, display):
        if not display or not display['active']:
            return False
        return self.shell('am', 'start', '--user', '0', '--display', str(display['id']),
                          '-n', 'com.termux.x11/.MainActivity')[0]
