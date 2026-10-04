from Xlib import X, display

d = display.Display()
r = d.screen().root
g = r.get_geometry()
for wid in r.get_full_property(d.intern_atom('_NET_CLIENT_LIST'), X.AnyPropertyType).value:
    w = d.create_resource_object('window', int(wid))
    if 'xfce4-panel' not in (w.get_wm_class() or ()):
        continue
    s = w.get_full_property(d.intern_atom('_NET_WM_STRUT'), X.AnyPropertyType)
    if s is None or len(s.value) < 4 or not s.value[3]:
        continue
    p = r.translate_coords(w, 0, 0)
    wg = w.get_geometry()
    margin = g.height-p.y-wg.height
    print(f'ROOT={g.width}x{g.height} DOCK={wg.width}x{wg.height}+{p.x}+{p.y} MARGIN={margin}', flush=True)
    assert wg.width <= g.width-20, 'dock clips the rounded end caps'
    assert margin == 12, f'dock margin {margin}, expected 12'
    assert abs(p.x-max(0,(g.width-wg.width)//2)) <= 1, 'dock not centered'
    break
else:
    raise AssertionError('bottom dock not found')
