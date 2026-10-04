"""On-demand notification snapshots. Android text is never evaluated as markup."""
from datetime import datetime
from zoneinfo import ZoneInfo
import re
import time


def notification_time(timestamp):
    if not timestamp:
        return ""
    return datetime.fromtimestamp(timestamp / 1000, ZoneInfo("America/Mexico_City")).strftime("%H:%M")


def expire_response(path, delay=30):
    # A single bounded expiry after an on-demand query, not a notification poll.
    time.sleep(delay)
    path.unlink(missing_ok=True)


def parse_notification(key, dump):
    parts = key.split('|')
    if len(parts) < 5 or not re.fullmatch(r'[A-Za-z0-9_.]+', parts[1]):
        return None
    if 'NotificationRecord(' not in dump:
        return None
    extras = {}
    for match in re.finditer(
        r'^\s*android\.(title|text|bigText|subText)=\w+ \((.*?)\)\s*'
        r'(?=^\s*android\.|^\s*\}|\Z)', dump, re.M | re.S
    ):
        extras[match[1]] = match[2].strip()
    sensitive = bool(re.search(r'mSensitiveContent=true\b', dump))
    title = extras.get('title', '')[:256]
    text = (extras.get('bigText') or extras.get('text') or '')[:3000]
    if sensitive:
        title, text = 'Notificación', 'Contenido protegido por Android'
    if not title and not text:
        text = 'Esta notificación no ofrece una vista de texto.'
    timestamp = re.search(r'mUpdateTimeMs=(\d+)', dump)
    if not timestamp:
        timestamp = re.search(r'^\s*when=(\d+)', dump, re.M)
    group = re.search(r'^\s*groupKey=(.*)$', dump, re.M)
    return {
        'package': parts[1], 'title': title, 'text': text,
        'timestamp': int(timestamp[1]) if timestamp else 0,
        'group': group[1].strip() if group else key,
        'summary': bool(re.search(r'^\s*flags=.*\bGROUP_SUMMARY\b', dump, re.M)),
    }


def notification_snapshot(keys_text, read, user_id=0, limit=40, budget=12):
    keys = []
    for key in keys_text.splitlines():
        key = key.strip()
        parts = key.split('|')
        if len(parts) >= 5 and parts[0] in (str(user_id), '-1'):
            keys.append(key)
    records, unavailable = [], 0
    deadline = time.monotonic() + budget
    for key in keys[:limit]:
        if time.monotonic() >= deadline:
            break
        try:
            item = parse_notification(key, read(key))
        except (OSError, RuntimeError):
            item = None
        if item is None:
            unavailable += 1
        else:
            records.append(item)
    children = {n['group'] for n in records if not n['summary']}
    records = [n for n in records if not n['summary'] or n['group'] not in children]
    records.sort(key=lambda n: n['timestamp'], reverse=True)
    return {'notifications': records, 'total': len(keys), 'unavailable': unavailable,
            'truncated': len(keys) > limit or time.monotonic() >= deadline}
