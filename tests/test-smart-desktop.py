import importlib.util
import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'scripts/lib'))


class SmartTests(unittest.TestCase):
    def test_modules_exist(self):
        self.assertIsNotNone(importlib.util.find_spec('macdesk.context'))

    def test_displays_not_accessibility_or_fixed_id(self):
        from macdesk.context import parse_displays, preferred_display
        self.assertEqual(parse_displays('Enabled features of Display [2]'), [])
        text = '''mBaseDisplayInfo=DisplayInfo{"Phone", displayId 0, real 1080 x 2340, type INTERNAL, state ON}
mBaseDisplayInfo=DisplayInfo{"Samsung DeX", displayId 7, real 3440 x 1440, type EXTERNAL, state ON}
mOverrideDisplayInfo=DisplayInfo{"Samsung DeX", displayId 7, real 3440 x 1440, type EXTERNAL, state ON}'''
        displays = parse_displays(text)
        self.assertEqual(len(displays), 2)
        self.assertEqual(preferred_display(displays)['id'], 7)
        self.assertEqual(preferred_display(parse_displays(text.replace('state ON}', 'state OFF}'))), None)

    def test_conservative_modes(self):
        from macdesk.context import choose_mode
        self.assertEqual(choose_mode({'width': 3840, 'height': 2160}), 'phone')
        self.assertEqual(choose_mode({'external': True}), 'desktop')
        self.assertEqual(choose_mode({'remote': True, 'external': True}), 'remote')
        self.assertEqual(choose_mode({'remote': True}, 'tablet'), 'tablet')
        self.assertEqual(choose_mode({'touch': True, 'diagonal_inches': 11}), 'tablet')

    def test_input_buttons_are_not_external_keyboards(self):
        from macdesk.context import parse_inputs
        state = parse_inputs('\n Device 1: power\n IsExternal: false\n Sources: KEYBOARD\n KeyboardType: 1\n Device 2: touch\n IsExternal: false\n Sources: TOUCHSCREEN\n KeyboardType: 1')
        self.assertEqual(state, dict(touch=True, keyboard=False, mouse=False))
        self.assertTrue(parse_inputs('\n Device 3: usb\n IsExternal: true\n Sources: KEYBOARD\n KeyboardType: 2')['keyboard'])

    def test_negative_monitor_geometry_and_thirds(self):
        from macdesk.snap import rectangle, choose_monitor
        monitors = [(-1920, 0, 1920, 1080), (0, 0, 2560, 1440)]
        self.assertEqual(choose_monitor(monitors, (-1600, 10, 800, 600)), monitors[0])
        a = rectangle(monitors[0], 'third-left')
        b = rectangle(monitors[0], 'two-thirds-right')
        self.assertEqual(a[2] + b[2], 1920)
        self.assertEqual(a[0] + a[2], b[0])

    def test_profile_deltas_preserve_user_changes(self):
        from macdesk.profiles import Deltas
        values = {'dpi': '96', 'panel': '28'}
        delta = Deltas({}, values.get, lambda k, v: values.__setitem__(k, v))
        delta.apply({'dpi': '144', 'panel': '40'})
        values['panel'] = '50'
        delta.apply({'dpi': '96', 'panel': '28'})
        self.assertEqual(values, {'dpi': '96', 'panel': '50'})
        delta.restore()
        self.assertEqual(values, {'dpi': '96', 'panel': '50'})

    def test_failed_restore_retains_snapshot(self):
        from macdesk.profiles import Deltas
        state = {'dpi': {'original': '96', 'applied': '144'}}
        delta = Deltas(state, lambda key: '144', lambda key, value: False)
        delta.restore()
        self.assertIn('dpi', state)
        delta.get = lambda key: None
        delta.restore()
        self.assertIn('dpi', state)

    def test_background_debounce_and_once(self):
        from macdesk.context import Governor
        governor = Governor()
        self.assertFalse(governor.update('BACKGROUND', 0))
        self.assertFalse(governor.update('ACTIVE', 3))
        self.assertFalse(governor.update('BACKGROUND', 4))
        self.assertFalse(governor.update('BACKGROUND', 13))
        self.assertTrue(governor.update('BACKGROUND', 14))
        self.assertFalse(governor.update('BACKGROUND', 60))
        self.assertFalse(governor.update('REMOTE', 61))

    def test_visibility_requires_x11_window_evidence(self):
        from macdesk.context import visibility
        self.assertIsNone(visibility('unavailable'))
        focused = 'mCurrentFocus=Window{abc com.termux/.MainActivity}\n'
        self.assertEqual(visibility(focused + ' Window #1 Window{123 com.termux.x11/.MainActivity}:\n isOnScreen=false\n isVisible=false'), 'BACKGROUND')
        self.assertEqual(visibility(focused + ' Window #1 Window{123 com.termux.x11/.MainActivity}:\n isOnScreen=true\n isVisible=true'), 'IDLE')
        self.assertEqual(visibility('mCurrentFocus=Window{123 com.termux.x11/.MainActivity}'), 'ACTIVE')
        self.assertEqual(visibility(focused + ' Window #8: WindowStateAnimator{com.termux.x11/.MainActivity}\n Window #26 Window{123 com.termux.x11/.MainActivity}:\n isOnScreen=false\n isVisible=false'), 'BACKGROUND')

    def test_bounded_text_unicode_and_no_archive_extraction(self):
        from macdesk.preview import describe, prune_cache
        import zipfile
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            text = root / 'texto á $(touch nope).txt'
            text.write_bytes(b'x' * 1024 * 1024)
            self.assertLess(len(describe(text)['text']), 270000)
            archive = root / 'space ü.zip'
            with zipfile.ZipFile(archive, 'w') as z:
                z.writestr('../escape', 'secret')
            self.assertIn('../escape', describe(archive)['text'])
            self.assertFalse((root.parent / 'escape').exists())
            cache = root / 'cache'
            cache.mkdir()
            (cache / 'old').write_bytes(b'a' * 100)
            (cache / 'new').write_bytes(b'b' * 100)
            prune_cache(cache, 100)
            self.assertLessEqual(sum(p.stat().st_size for p in cache.iterdir()), 100)


if __name__ == '__main__':
    unittest.main()
