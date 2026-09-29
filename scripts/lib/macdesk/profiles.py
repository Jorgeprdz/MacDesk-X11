"""Reversible deltas, never a copy of an entire XFCE configuration."""
from .common import STATE, read_json, write_json, run


class Deltas:
    def __init__(self, state, get, put):
        self.state, self.get, self.put = state, get, put

    def apply(self, desired):
        for key, value in desired.items():
            current = self.get(key)
            if current is None:
                continue
            item = self.state.get(key)
            if item and current != item['applied']:
                item['user_changed'] = True
            if item and item.get('user_changed'):
                continue
            if current == value:
                continue
            if self.put(key, value) is not False:
                self.state[key] = dict(original=item['original'] if item else current,
                                       applied=value)

    def restore(self):
        for key, item in list(self.state.items()):
            current = self.get(key)
            if current is None:
                continue  # bus unavailable: keep the recovery snapshot
            if item.get('user_changed') or current != item['applied']:
                del self.state[key]  # intentional user change, never undo it
            elif self.put(key, item['original']) is not False:
                del self.state[key]


def get_property(key):
    channel, prop = key.split(':', 1)
    ok, value = run(['xfconf-query', '-c', channel, '-p', prop])
    return value if ok else None


def put_property(key, value):
    channel, prop = key.split(':', 1)
    return run(['xfconf-query', '-c', channel, '-p', prop, '-s', value])[0]


class Profiles:
    def __init__(self):
        self.path = STATE / 'profile-deltas.json'
        saved = read_json(self.path)
        if not isinstance(saved, dict):
            saved = {}
        saved = {key: item for key, item in saved.items()
                 if isinstance(item, dict) and isinstance(item.get('original'), str)
                 and isinstance(item.get('applied'), str)}
        self.deltas = Deltas(saved, get_property, put_property)

    def apply(self, mode, snap=True):
        dpi, size = {'phone': (144, 40), 'tablet': (120, 36),
                     'desktop': (96, 28), 'remote': (96, 28)}[mode]
        desired = {'xsettings:/Xft/DPI': str(dpi)}
        # Discover panel IDs instead of assuming panel-1.
        ok, output = run(['xfconf-query', '-c', 'xfce4-panel', '-l'])
        if ok:
            for prop in output.splitlines():
                if prop.startswith('/panels/panel-') and prop.endswith('/size'):
                    desired['xfce4-panel:' + prop] = str(size)
        key = 'xfwm4:/general/use_compositing'
        original = self.deltas.state.get(key, {}).get('original')
        if mode == 'remote':
            desired[key] = 'false'
        elif original is not None:
            desired[key] = original
        if snap:
            desired['xfwm4:/general/tile_on_move'] = 'true'
        self.deltas.apply(desired)
        write_json(self.path, self.deltas.state)

    def restore(self):
        self.deltas.restore()
        write_json(self.path, self.deltas.state)
