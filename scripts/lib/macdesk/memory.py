"""Best-effort RSS accounting; never used as authority to terminate a process."""
import os
from pathlib import Path
import re
from .common import CACHE


def measure(core_pid=None, children=()):
    rows = {}
    for folder in Path('/proc').glob('[0-9]*'):
        try:
            stat = (folder / 'stat').read_text()
            fields = stat[stat.rfind(')')+2:].split()
            status = (folder / 'status').read_text()
            rss = re.search(r'^VmRSS:\s+(\d+)', status, re.M)
            argv = (folder / 'cmdline').read_bytes().split(b'\0')
            rows[int(folder.name)] = dict(parent=int(fields[1]),
                rss=int(rss[1]) if rss else None,
                name=stat[stat.find('(')+1:stat.rfind(')')], argv=argv)
        except (OSError, ValueError, IndexError):
            continue
    # Anchor on this core's XFCE session ancestry, not all processes of a UID.
    anchor = core_pid or os.getpid()
    visited = set()
    while anchor in rows and anchor not in visited:
        visited.add(anchor)
        if rows[anchor]['name'] in ('xfce4-session', 'startxfce4'):
            break
        parent = rows[anchor]['parent']
        if parent <= 1:
            break
        anchor = parent
    valid_anchor = anchor in rows and rows[anchor]['name'] in ('xfce4-session', 'startxfce4')
    owned = {core_pid or os.getpid(), *children}
    session = {anchor} if valid_anchor else set(owned)
    for _ in range(32):
        expanded = session | {pid for pid, r in rows.items() if r['parent'] in session}
        if expanded == session:
            break
        session = expanded
    buckets = dict(core_kib=0, helpers_kib=0, xfce_kib=0, applications_kib=0)
    infrastructure = {'xfce4-session', 'xfwm4', 'xfce4-panel', 'xfdesktop',
                      'xfsettingsd', 'plank', 'dbus-daemon', 'xfconfd'}
    unknown = 0
    for pid in session:
        row = rows.get(pid)
        if not row or row['rss'] is None:
            unknown += 1
            continue
        key = 'core_kib' if pid == core_pid else 'helpers_kib' if pid in owned else 'xfce_kib' if row['name'] in infrastructure else 'applications_kib'
        buckets[key] += row['rss']
    available = None
    try:
        match = re.search(r'^MemAvailable:\s+(\d+)', Path('/proc/meminfo').read_text(), re.M)
        available = int(match[1]) if match else None
    except OSError:
        pass
    cache = sum(p.stat().st_size for p in CACHE.glob('*') if p.is_file() and not p.is_symlink()) if CACHE.exists() else 0
    observed_total = sum(buckets.values())
    if core_pid not in rows or rows[core_pid]['rss'] is None:
        buckets['core_kib'] = None
    if not valid_anchor:
        buckets['xfce_kib'] = None
        buckets['applications_kib'] = None
    return dict(**buckets, total_rss_kib=observed_total if valid_anchor and not unknown else None,
                observed_rss_kib=observed_total if any(p in rows for p in session) else None,
                x11_android_kib=None, android_available_kib=available,
                cache_bytes=cache, session_processes=len(session),
                session_scope_verified=valid_anchor, inaccessible_processes=unknown,
                note='RSS sums shared pages more than once. Android X11 is outside guest ancestry; null means unknown.')
