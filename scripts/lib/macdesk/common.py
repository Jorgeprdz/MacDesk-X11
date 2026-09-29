import json
import os
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[3]
CONFIG = Path(os.environ.get('XDG_CONFIG_HOME', Path.home() / '.config')) / 'macdesk'
STATE = Path(os.environ.get('XDG_STATE_HOME', Path.home() / '.local/state')) / 'macdesk'
CACHE = Path(os.environ.get('XDG_CACHE_HOME', Path.home() / '.cache')) / 'macdesk/quicklook'
# Host and guest can explicitly share this directory via --shared-home.
RUNTIME = Path(os.environ.get('MACDESK_RUNTIME', CONFIG / 'runtime'))


def private_dir(path):
    path.mkdir(mode=0o700, parents=True, exist_ok=True)
    if path.is_symlink() or path.stat().st_uid != os.getuid():
        raise ValueError('Unsafe MacDesk directory: ' + str(path))
    path.chmod(0o700)
    return path


def read_json(path, default=None):
    try:
        with path.open() as stream:
            return json.load(stream)
    except (OSError, ValueError):
        return {} if default is None else default


def write_json(path, value):
    private_dir(path.parent)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix='.write-')
    try:
        with os.fdopen(fd, 'w') as stream:
            json.dump(value, stream, ensure_ascii=False)
            stream.write('\n')
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def run(argv, timeout=4):
    """Bounded-time command with argv only. Callers use bounded-output tools."""
    try:
        result = subprocess.run([str(a) for a in argv], capture_output=True,
                                timeout=timeout, text=True, errors='replace')
        return result.returncode == 0, result.stdout.strip()
    except (OSError, subprocess.TimeoutExpired):
        return False, ''


def flags():
    defaults = dict(continuity=True, window_snap=True, quicklook=True,
                    desktop_mode=True, memory_governor=True, dex_binding=True,
                    android_interval=60, super_shortcuts=False)
    loaded = read_json(CONFIG / 'features.json')
    if not isinstance(loaded, dict):
        loaded = {}
    for key, value in loaded.items():
        if key in defaults and type(value) is type(defaults[key]):
            defaults[key] = value
    defaults['android_interval'] = max(60, defaults['android_interval'])
    return defaults


def log_event(module, message):
    import logging
    from logging.handlers import RotatingFileHandler
    private_dir(STATE)
    logger = logging.getLogger('macdesk.' + module)
    if not logger.handlers:
        handler = RotatingFileHandler(STATE / (module + '.log'), maxBytes=65536, backupCount=1)
        handler.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    logger.info(message)
