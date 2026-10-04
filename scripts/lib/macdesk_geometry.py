"""Pure dock identification and responsive geometry rules."""
def is_bottom_dock(window_id, known_id, y, height, strut):
    if window_id == known_id:
        return True
    if strut and len(strut) >= 4:
        if strut[2]:
            return False
        if strut[3]:
            return True
    return y > height // 2

def dock_profile(width):
    icon = 48 if width >= 1120 else 40 if width >= 1000 else 32 if width >= 880 else 24 if width >= 720 else 16
    return icon, icon+28
