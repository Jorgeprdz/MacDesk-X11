"""Reuse Termux:X11 clipboard; Android actions are explicit, on demand."""
import shutil
from pathlib import Path
from urllib.parse import urlsplit
from .common import run
from .context import Android


def host_tool(name):
    return shutil.which(name) or shutil.which('/data/data/com.termux/files/usr/bin/' + name)


def open_android(value, share=False):
    parsed = urlsplit(value)
    if not share and parsed.scheme in ('https', 'http') and parsed.netloc:
        tool = host_tool('termux-open-url')
        if tool:
            return run([tool, value])[0]
        return Android().shell('am', 'start', '--user', '0', '-a',
                               'android.intent.action.VIEW', '-d', value)[0]
    path = Path(value).expanduser().resolve(strict=True)
    if not path.is_file():
        raise ValueError('Android open/share requires a regular file')
    # termux-open provides a content:// FileProvider grant. Never send file://
    # via adb, and never copy a private file into public storage automatically.
    tool = host_tool('termux-open')
    if not tool:
        raise ValueError('termux-open unavailable in this environment; run from Termux')
    # Shared-home guest path must be translated to the FileProvider's Android
    # filesystem; Android cannot resolve /root inside a PRoot mount namespace.
    if path.is_relative_to('/root'):
        path = Path('/data/data/com.termux/files/home') / path.relative_to('/root')
    elif not any(path.is_relative_to(p) for p in ('/sdcard', '/storage', '/data/data/com.termux/files/home')):
        raise ValueError('File is outside Android-accessible shared/home storage')
    return run([tool, '--send' if share else '--view', str(path)])[0]


def storage_links():
    destination = Path.home() / 'Android'
    if destination.is_symlink():
        raise ValueError('Android link directory must not be a symlink')
    destination.mkdir(exist_ok=True)
    status = {}
    for label, folder in [('Downloads', 'Download'), ('Pictures', 'Pictures'),
                          ('Documents', 'Documents'), ('Movies', 'Movies'), ('Music', 'Music')]:
        source, link = Path('/sdcard') / folder, destination / label
        if not source.is_dir():
            status[label] = 'unavailable: Android storage permission/bind required'
        elif link.exists() or link.is_symlink():
            status[label] = 'existing (preserved)'
        else:
            link.symlink_to(source, target_is_directory=True)
            status[label] = str(source)
    return status


def status():
    android = Android()
    result = {'clipboard': 'Delegated to Termux:X11 clipboardEnable; Android focus/permission restrictions apply'}
    for key, args in {'battery': ('dumpsys', 'battery'), 'network': ('cmd', 'wifi', 'status'),
                      'display': ('dumpsys', 'display')}.items():
        ok, value = android.shell(*args)
        result[key] = value[:32768] if ok else 'unavailable'
    return result
