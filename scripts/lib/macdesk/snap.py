"""On-demand layouts. Mouse snapping/preview remains xfwm4's responsibility."""
import re
from .common import run

ZONES = {
    'left': (0, 0, 1, 1, 2, 1), 'right': (1, 0, 2, 1, 2, 1),
    'top-left': (0, 0, 1, 1, 2, 2), 'top-right': (1, 0, 2, 1, 2, 2),
    'bottom-left': (0, 1, 1, 2, 2, 2), 'bottom-right': (1, 1, 2, 2, 2, 2),
    'third-left': (0, 0, 1, 1, 3, 1), 'third-center': (1, 0, 2, 1, 3, 1),
    'third-right': (2, 0, 3, 1, 3, 1),
    'two-thirds-left': (0, 0, 2, 1, 3, 1), 'two-thirds-right': (1, 0, 3, 1, 3, 1),
}


def rectangle(monitor, zone):
    x, y, w, h = monitor
    a, b, c, d, nx, ny = ZONES[zone]
    left, top = x + w * a // nx, y + h * b // ny
    return left, top, x + w * c // nx - left, y + h * d // ny - top


def choose_monitor(monitors, window):
    x, y, w, h = window
    def overlap(m):
        a, b, c, d = m
        return max(0, min(x+w, a+c)-max(x, a)) * max(0, min(y+h, b+d)-max(y, b))
    return max(monitors, key=overlap)


def monitors():
    ok, output = run(['xrandr', '--listactivemonitors'])
    result = []
    if ok:
        for line in output.splitlines():
            m = re.search(r'(\d+)/\d+x(\d+)/\d+([+-]\d+)([+-]\d+)', line)
            if m:
                w, h, x, y = map(int, m.groups())
                result.append((x, y, w, h))
    return result


def snap(zone, window=None):
    ok, wid = (True, window) if window else run(['xdotool', 'getactivewindow'])
    if not ok or not wid.isdecimal():
        raise ValueError('No active X11 window')
    ok, kind = run(['xprop', '-id', wid, '_NET_WM_WINDOW_TYPE'])
    if not ok or '_NET_WM_WINDOW_TYPE_NORMAL' not in kind:
        raise ValueError('Snap requires a normal application window (not a dialog/panel)')
    if zone in ('up', 'down'):
        operation = 'add' if zone == 'up' else 'remove'
        return run(['wmctrl', '-ir', wid, '-b', operation + ',maximized_vert,maximized_horz'])[0]
    if zone not in ZONES:
        raise ValueError('Unknown layout zone')
    ok, output = run(['xdotool', 'getwindowgeometry', '--shell', wid])
    values = dict(re.findall(r'^(X|Y|WIDTH|HEIGHT)=(-?\d+)$', output, re.M))
    displays = monitors()
    if not ok or len(values) != 4 or not displays:
        raise ValueError('X11 geometry unavailable')
    monitor = choose_monitor(displays, tuple(int(values[k]) for k in ('X', 'Y', 'WIDTH', 'HEIGHT')))
    # Intersect with current EWMH workarea so panel struts remain respected.
    ok, work = run(['xprop', '-root', '_NET_CURRENT_DESKTOP', '_NET_WORKAREA'])
    if ok:
        current = re.search(r'_NET_CURRENT_DESKTOP[^=]*=\s*(\d+)', work)
        area = re.search(r'_NET_WORKAREA[^=]*=\s*([\d, -]+)', work)
        if current and area:
            numbers = [int(n) for n in re.findall(r'-?\d+', area[1])]
            offset = int(current[1]) * 4
            if len(numbers) >= offset + 4:
                a, b, c, d = numbers[offset:offset+4]
                x, y, w, h = monitor
                left, top = max(x, a), max(y, b)
                right, bottom = min(x+w, a+c), min(y+h, b+d)
                if right > left and bottom > top:
                    monitor = (left, top, right-left, bottom-top)
    x, y, w, h = rectangle(monitor, zone)
    ok, extents = run(['xprop', '-id', wid, '_NET_FRAME_EXTENTS'])
    if ok and '=' in extents:
        frame = re.findall(r'\d+', extents.split('=', 1)[1])
        if len(frame) == 4:
            left, right, top, bottom = map(int, frame)
            w, h = max(1, w-left-right), max(1, h-top-bottom)
    if not run(['wmctrl', '-ir', wid, '-b', 'remove,maximized_vert,maximized_horz'])[0]:
        return False
    return run(['wmctrl', '-ir', wid, '-e', f'0,{x},{y},{w},{h}'])[0]
