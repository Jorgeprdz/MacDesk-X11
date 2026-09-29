"""Bounded preview preparation. Only invoked for a user-selected file."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import struct
import subprocess
import tarfile
import time
import zipfile
from .common import CACHE, ROOT, private_dir, run

TEXT_LIMIT = 256 * 1024
ENTRY_LIMIT = 1000
CACHE_LIMIT = 32 * 1024 * 1024


def prune_cache(path=CACHE, limit=CACHE_LIMIT):
    if not path.exists():
        return
    entries = [p for p in path.iterdir() if p.is_file() and not p.is_symlink()]
    entries.sort(key=lambda p: p.stat().st_mtime_ns)
    total = sum(p.stat().st_size for p in entries)
    for p in entries:
        if total <= limit:
            break
        total -= p.stat().st_size
        p.unlink(missing_ok=True)


def zip_listing(path):
    # Python ZipFile materializes the central directory: cap it BEFORE opening.
    with path.open('rb') as f:
        f.seek(max(0, path.stat().st_size - 65557))
        tail = f.read(65557)
    pos = tail.rfind(b'PK\x05\x06')
    if pos < 0 or len(tail) - pos < 22:
        return 'Invalid or unsupported ZIP directory'
    record = struct.unpack_from('<4s4H2LH', tail, pos)
    count, size = record[4], record[5]
    if count > ENTRY_LIMIT or size > 2 * 1024 * 1024 or count == 65535:
        return 'ZIP directory exceeds preview budget (1000 entries / 2 MiB); not loaded.'
    with zipfile.ZipFile(path) as z:
        return '\n'.join(f'{i.file_size:>12}  {i.filename[:1024]}' for i in z.infolist()[:ENTRY_LIMIT])


def describe(path):
    path = Path(path).expanduser().resolve(strict=True)
    info = path.stat()
    if not stat.S_ISREG(info.st_mode):
        raise ValueError('Preview accepts regular files only')
    result = dict(title=path.name, text=f'{path.name}\n{info.st_size:,} bytes', image=None)
    suffix = path.suffix.lower()
    if suffix in ('.txt', '.md', '.json', '.xml', '.log', '.csv', '.py', '.sh'):
        with path.open('rb') as stream:
            data = stream.read(TEXT_LIMIT)
        result['text'] = data.decode('utf-8', errors='replace')
        if info.st_size > TEXT_LIMIT:
            result['text'] += '\n[Preview limited to 256 KiB]'
    elif suffix == '.zip':
        result['text'] += '\n' + zip_listing(path)
    elif suffix in ('.tar', '.tgz', '.gz', '.bz2', '.xz'):
        # Stream metadata; never extract payloads. Worker has a hard timeout.
        with tarfile.open(path, 'r|*') as archive:
            lines = []
            for index, item in enumerate(archive):
                if index >= ENTRY_LIMIT:
                    lines.append('[Listing limited to 1000 entries]')
                    break
                lines.append(f'{item.size:>12}  {item.name[:1024]}')
                archive.members.clear()
            result['text'] += '\n' + '\n'.join(lines)
    elif suffix == '.7z':
        result['text'] += '\n' + archive_listing(path)
    elif suffix in ('.jpg', '.jpeg', '.png', '.webp', '.gif'):
        if info.st_size <= 32 * 1024 * 1024:
            result['image'] = native_image(path, info)
        else:
            result['text'] += '\nImage exceeds 32 MiB input limit.'
    elif suffix == '.svg':
        # Do not resolve XML entities, linked images or network resources.
        if info.st_size <= 1024*1024:
            data = path.read_bytes()
            if any(token in data.lower() for token in (b'<!doctype', b'<!entity', b'href', b'url', b'@import')):
                result['text'] += '\nSVG external-resource preview refused.'
            else:
                result['image'] = native_image(path, info)
        else:
            result['text'] += '\nSVG exceeds 1 MiB input limit.'
    elif suffix == '.pdf' or suffix in ('.mp4', '.mkv', '.webm', '.mp3', '.m4a', '.wav', '.flac'):
        if suffix == '.pdf' and info.st_size > 32*1024*1024:
            result['text'] += '\nPDF exceeds 32 MiB input budget; not decoded.'
            return result
        private_dir(CACHE)
        key = hashlib.sha256(f'{path}:{info.st_size}:{info.st_mtime_ns}'.encode()).hexdigest()
        image = CACHE / (key + '.png')
        if image.exists():
            os.utime(image, None)
            result['image'] = str(image)
            prune_cache()
            return result
        if shutil.which('gjs'):
            # Evince/GStreamer are reused before considering optional tools.
            ok, metadata = run(['gjs', ROOT / 'scripts/quicklook-render.js', path, image], timeout=10)
            if ok:
                result['text'] += '\n' + json.loads(metadata)['text'][:TEXT_LIMIT]
            else:
                image.unlink(missing_ok=True)
                result['text'] += '\nNative preview unavailable or resource budget exceeded.'
        elif suffix == '.pdf':
            if shutil.which('pdftoppm'):
                if not image.exists():
                    run(['pdftoppm', '-f', '1', '-singlefile', '-scale-to', '1280', '-png',
                         path, str(image)[:-4]], timeout=8)
            else:
                result['text'] += '\npdftoppm unavailable; PDF rendering requires poppler-utils.'
        else:
            if shutil.which('ffprobe'):
                ok, metadata = run(['ffprobe', '-v', 'error', '-show_entries',
                                    'format=duration,size:format_tags=title,artist,album',
                                    '-of', 'json', str(path)], timeout=4)
                if ok:
                    result['text'] += '\n' + metadata[:TEXT_LIMIT]
            if shutil.which('ffmpeg') and not image.exists():
                run(['ffmpeg', '-nostdin', '-v', 'error', '-i', path, '-frames:v', '1',
                     '-vf', 'scale=960:540:force_original_aspect_ratio=decrease',
                     '-threads', '1', '-y', image], timeout=8)
            if not shutil.which('ffmpeg'):
                result['text'] += '\nffmpeg unavailable; media thumbnail unavailable.'
        if image.exists() and image.stat().st_size <= CACHE_LIMIT:
            os.utime(image, None)
            result['image'] = str(image)
        prune_cache()
    return result


def native_image(path, info):
    private_dir(CACHE)
    key = hashlib.sha256(f'{path}:{info.st_size}:{info.st_mtime_ns}'.encode()).hexdigest()
    target = CACHE / (key + '.png')
    if not target.exists():
        ok, _ = run(['gjs', ROOT / 'scripts/quicklook-render.js', path, target], timeout=10)
        if not ok:
            target.unlink(missing_ok=True)
            return None
    os.utime(target, None)
    prune_cache()
    return str(target) if target.exists() else None


def archive_listing(path):
    import ctypes as c
    try:
        lib = c.CDLL('libarchive.so.13')
    except OSError:
        return '7z listing unavailable: libarchive.so.13 is not installed.'
    signatures = {
        'archive_read_new': (c.c_void_p, []),
        'archive_read_support_filter_all': (c.c_int, [c.c_void_p]),
        'archive_read_support_format_all': (c.c_int, [c.c_void_p]),
        'archive_read_open_filename': (c.c_int, [c.c_void_p, c.c_char_p, c.c_size_t]),
        'archive_read_next_header': (c.c_int, [c.c_void_p, c.POINTER(c.c_void_p)]),
        'archive_entry_pathname': (c.c_char_p, [c.c_void_p]),
        'archive_entry_size': (c.c_longlong, [c.c_void_p]),
        'archive_read_data_skip': (c.c_int, [c.c_void_p]),
        'archive_read_free': (c.c_int, [c.c_void_p]),
    }
    for name, (ret, args) in signatures.items():
        function = getattr(lib, name)
        function.restype, function.argtypes = ret, args
    archive = lib.archive_read_new()
    if not archive:
        return 'Archive allocation failed'
    try:
        lib.archive_read_support_filter_all(archive)
        lib.archive_read_support_format_all(archive)
        if lib.archive_read_open_filename(archive, os.fsencode(path), 10240) != 0:
            return 'Archive cannot be opened (corrupt, encrypted or unsupported)'
        lines, entry = [], c.c_void_p()
        for _ in range(ENTRY_LIMIT):
            status = lib.archive_read_next_header(archive, c.byref(entry))
            if status == 1:
                break
            if status < 0:
                lines.append('[Archive metadata error]')
                break
            name = (lib.archive_entry_pathname(entry) or b'')[:1024].decode('utf-8', 'replace')
            lines.append(f'{lib.archive_entry_size(entry):>12}  {name}')
            if lib.archive_read_data_skip(archive) < 0:
                break
        else:
            lines.append('[Listing limited to 1000 entries]')
        return '\n'.join(lines)
    finally:
        lib.archive_read_free(archive)


def worker(path):
    """Resource budget applies to decoders/archives, never the desktop/core."""
    import json
    import resource
    # SpiderMonkey reserves a multi-GiB *virtual* JIT arena even for tiny files;
    # a 512 MiB RLIMIT_AS prevents GJS from initializing. Native decoders use
    # input/pixel/time limits instead; archive/text workers retain the AS cap.
    if Path(path).suffix.lower() in ('.txt', '.md', '.json', '.xml', '.log', '.zip', '.tar', '.gz', '.tgz', '.7z'):
        resource.setrlimit(resource.RLIMIT_AS, (512 * 1024 * 1024,) * 2)
    resource.setrlimit(resource.RLIMIT_CPU, (10, 10))
    # Unlike address-space limits, DATA permits SpiderMonkey's untouched JIT
    # address reservation while bounding writable heap/mmap allocations.
    resource.setrlimit(resource.RLIMIT_DATA, (256 * 1024 * 1024,) * 2)
    resource.setrlimit(resource.RLIMIT_FSIZE, (CACHE_LIMIT,) * 2)
    print(json.dumps(describe(path), ensure_ascii=False))
