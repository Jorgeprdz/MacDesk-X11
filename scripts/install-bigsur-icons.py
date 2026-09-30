#!/usr/bin/env python3
"""Install OpenDesktop 1399044 in private, Gallery-excluded user storage."""
import argparse
import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import tarfile
import tempfile
import urllib.request
import xml.etree.ElementTree as ET

API = 'https://api.opendesktop.org/ocs/v1/content/data/1399044'
MAX_DOWNLOAD = 64 * 1024 * 1024
MAX_EXPANDED = 512 * 1024 * 1024


def download(url, target, limit):
    if not url.startswith('https://'):
        raise ValueError('Se requiere HTTPS')
    request = urllib.request.Request(url, headers={'User-Agent': 'MacDesk-icons/1.0'})
    with urllib.request.urlopen(request, timeout=60) as response, target.open('wb') as output:
        if not response.url.startswith('https://'):
            raise ValueError('Redireccion insegura')
        total = 0
        while chunk := response.read(65536):
            total += len(chunk)
            if total > limit:
                raise ValueError('Descarga demasiado grande')
            output.write(chunk)


def unpack(archive, destination):
    destination = Path(destination).resolve()
    with tarfile.open(archive, 'r:xz') as bundle:
        members = bundle.getmembers()
        if len(members) > 100000 or sum(m.size for m in members) > MAX_EXPANDED:
            raise ValueError('Paquete demasiado grande')
        links = []
        for member in members:
            relative = Path(member.name)
            if relative.is_absolute() or '..' in relative.parts:
                raise ValueError('Ruta insegura en el paquete')
            target = destination / relative
            if member.issym():
                links.append((target, member.linkname))
            elif member.isdir():
                target.mkdir(parents=True, exist_ok=True)
            elif member.isfile():
                target.parent.mkdir(parents=True, exist_ok=True)
                with bundle.extractfile(member) as source, target.open('xb') as output:
                    shutil.copyfileobj(source, output, 65536)
            else:
                raise ValueError('Tipo de archivo no permitido')
        # Links are created last: archive links can never redirect file writes.
        for target, linkname in links:
            # Upstream 1399044 includes one link to the author's home directory.
            if linkname == '/home/rain/.local/share/icons/BigSur/preferences/32':
                linkname = os.path.relpath(destination / 'BigSur/preferences/32', target.parent)
            if Path(linkname).is_absolute():
                raise ValueError('Enlace absoluto no permitido')
            target.parent.mkdir(parents=True, exist_ok=True)
            target.symlink_to(linkname)
        for target, _ in links:
            if not target.resolve().is_relative_to(destination):
                raise ValueError('Enlace fuera del paquete')
    for theme in ('BigSur', 'BigSur-dark'):
        if not (destination / theme / 'index.theme').is_file():
            raise ValueError('Paquete BigSur incompleto')


def install(home, dark=False):
    # HOME must be Termux private storage or the Linux user's private home.
    home = home.resolve()
    if any(str(home).startswith(p) for p in ('/sdcard', '/storage', '/mnt/media_rw')):
        raise ValueError('Ejecuta desde Termux o Linux con HOME privado, no /sdcard')
    icons = home / '.local/share/icons'
    store = home / '.local/share/macdesk/icon-themes'
    config = home / '.config/macdesk'
    for directory in (icons, store, config):
        directory.mkdir(parents=True, exist_ok=True)
        (directory / '.nomedia').touch()
    with tempfile.TemporaryDirectory(prefix='.bigsur-', dir=store) as temporary:
        stage = Path(temporary)
        (stage / '.nomedia').touch()
        metadata = stage / 'source.xml'
        download(API, metadata, 2 * 1024 * 1024)
        content = ET.parse(metadata).getroot().find('./data/content')
        if content is None:
            raise ValueError('OpenDesktop no devolvio el tema')
        url = None
        for item in content:
            if item.tag.startswith('downloadname') and item.text == 'BigSur.tar.xz':
                url = content.findtext('downloadlink' + item.tag[len('downloadname'):])
        if not url:
            raise ValueError('BigSur.tar.xz no disponible; no se instalo otro tema')
        archive = stage / 'icons.tar.xz'
        print('Descargando BigSur desde OpenDesktop…', flush=True)
        download(url, archive, MAX_DOWNLOAD)
        checksum = hashlib.sha256()
        with archive.open('rb') as source:
            while chunk := source.read(65536):
                checksum.update(chunk)
        digest = checksum.hexdigest()[:20]
        version = store / digest
        extracted = stage / 'extracted'
        extracted.mkdir()
        (extracted / '.nomedia').touch()
        unpack(archive, extracted)
        # Never overwrite an unmanaged theme directory or link.
        for name in ('BigSur', 'BigSur-dark'):
            link = icons / name
            if link.exists() or link.is_symlink():
                if not link.is_symlink() or not link.resolve().is_relative_to(store):
                    raise ValueError(f'{link} ya existe: renombralo para conservarlo y reintenta')
        if not version.exists():
            extracted.rename(version)
        for name in ('BigSur', 'BigSur-dark'):
            link = icons / name
            pending = stage / name
            # Relative link works across Termux HOME -> Debian /root bind mount.
            pending.symlink_to(os.path.relpath(version / name, icons))
            pending.replace(link)
    theme = 'BigSur-dark' if dark else 'BigSur'
    (config / 'icon-theme').write_text(theme + '\n')
    # XFCE executes this inside the correct session bus, including older MacDesk.
    autostart = home / '.config/autostart'
    autostart.mkdir(parents=True, exist_ok=True)
    (autostart / 'macdesk-bigsur-icons.desktop').write_text(
        '[Desktop Entry]\nType=Application\nName=MacDesk BigSur icons\n'
        f'Exec=xfconf-query -c xsettings -p /Net/IconThemeName -s {theme}\n'
        'OnlyShowIn=XFCE;\nStartupNotify=false\nTerminal=false\n')
    applied = False
    if os.environ.get('DBUS_SESSION_BUS_ADDRESS') and shutil.which('xfconf-query'):
        try:
            result = subprocess.run(['xfconf-query', '-c', 'xsettings', '-p',
                                     '/Net/IconThemeName', '-s', theme],
                                    timeout=10, capture_output=True)
            applied = result.returncode == 0
        except subprocess.TimeoutExpired:
            pass
    print(f'Instalado: {icons / theme}')
    print('Tema aplicado.' if applied else
          'Selecciona BigSur en XFCE > Apariencia > Iconos, o inicia tu proxima sesion.')
    print('Carpetas ocultas + .nomedia. No se reinicio ni cerro ninguna aplicacion.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dark', action='store_true', help='seleccionar BigSur-dark')
    args = parser.parse_args()
    try:
        install(Path.home(), args.dark)
    except (OSError, ValueError, RuntimeError, tarfile.TarError, ET.ParseError) as error:
        parser.exit(1, f'No se pudo instalar BigSur: {error}\n')
