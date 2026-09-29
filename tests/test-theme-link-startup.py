import pathlib
import subprocess
import tempfile
import unittest

SOURCE = pathlib.Path(__file__).resolve().parents[1] / "scripts/session-start"

class ThemeLinkStartup(unittest.TestCase):
    def test_existing_dangling_theme_does_not_abort_startup(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            themes = root / "themes"
            themes.mkdir()
            link = themes / "Tahoe-Dark"
            link.symlink_to(root / "missing-theme")
            source = SOURCE.read_text()
            block = source[source.index("mkdir -p /usr/local/share/themes"):source.index("nautilus_desktop=")]
            block = block.replace("/usr/local/share/themes", str(themes))
            result = subprocess.run(["sh", "-ec", block], env={"ROOT":str(root)}, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(link.is_symlink())
            self.assertEqual(link.readlink(), root / "missing-theme")

if __name__ == "__main__":
    unittest.main()
