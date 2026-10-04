"""Coordinated Android and desktop theme changes with best-effort rollback."""


def change_android_mode(mode, read, write):
    before = read()
    try:
        write(mode)
        after = read()
        if after['night_mode'] != mode:
            raise RuntimeError('Android rechazó el cambio de apariencia')
    except Exception as error:
        try:
            write(before['night_mode'])
        except Exception:
            raise RuntimeError(str(error) + '; no se pudo restaurar Android') from error
        raise
    return {**after, 'previous_mode': before['night_mode']}


def desktop_values(dark, icon_theme='BigSur'):
    theme = 'GoldenGate-Dark' if dark else 'GoldenGate-Light'
    icon_base = 'MacDesk-Desktop' if icon_theme.startswith('MacDesk-Desktop') else ('BigSur' if icon_theme.startswith('BigSur') else 'WhiteSur-MacDesk')
    return [('xsettings', '/Net/ThemeName', theme),
            ('xsettings', '/Net/IconThemeName', icon_base + ('-dark' if dark else '')),
            ('xfwm4', '/general/theme', theme),
            ('gnome', 'color-scheme', 'prefer-dark' if dark else 'default'),
            ('gnome', 'gtk-theme', theme)]


def apply_global_dark(dark, android, xfget, xfset, save):
    values = desktop_values(dark, xfget('xsettings', '/Net/IconThemeName', 'BigSur'))
    previous = [(channel, prop, xfget(channel, prop, value))
                for channel, prop, value in values]
    response = android({'action': 'dark_mode', 'enabled': dark})
    try:
        for channel, prop, value in values:
            xfset(channel, prop, 'string', value)
        save({'dark': dark})
    except Exception as error:
        rollback_errors = []
        for channel, prop, value in previous:
            try:
                xfset(channel, prop, 'string', value)
            except Exception:
                rollback_errors.append('MacDesk')
        try:
            android({'action': 'dark_mode', 'mode': response['previous_mode']})
        except Exception:
            rollback_errors.append('Android')
        suffix = ('; no se pudo restaurar ' + ', '.join(sorted(set(rollback_errors)))) if rollback_errors else ''
        raise RuntimeError(str(error) + suffix) from error
    return response
