import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts/lib'))
from macdesk_geometry import is_bottom_dock,dock_profile

class DockGeometryTests(unittest.TestCase):
    def test_growing_screen_keeps_dock_above_midpoint_identified(self):
        self.assertTrue(is_bottom_dock(2,None,481,1080,[0,0,0,90]))
    def test_remembered_dock_survives_temporary_strut_removal(self):
        self.assertTrue(is_bottom_dock(2,2,481,1080,[]))
    def test_top_panel_never_selected_from_top_strut(self):
        self.assertFalse(is_bottom_dock(1,None,580,1080,[0,0,41,0]))
    def test_initial_bottom_panel_without_strut(self):
        self.assertTrue(is_bottom_dock(2,None,990,1080,[]))
        self.assertFalse(is_bottom_dock(1,None,0,1080,[]))
    def test_responsive_profiles_restore_full_icons_on_wide_screen(self):
        self.assertEqual(dock_profile(768),(24,52))
        self.assertEqual(dock_profile(904),(32,60))
        self.assertEqual(dock_profile(1920),(48,76))
if __name__=='__main__':unittest.main()
