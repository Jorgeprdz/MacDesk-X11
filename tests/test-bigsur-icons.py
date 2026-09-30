import importlib.util
import io
from pathlib import Path
import tarfile
import tempfile
import unittest

spec = importlib.util.spec_from_file_location(
    'icons', Path(__file__).resolve().parents[1] / 'scripts/install-bigsur-icons.py')
icons = importlib.util.module_from_spec(spec)
spec.loader.exec_module(icons)


class ExtractionTests(unittest.TestCase):
    def archive(self, root, entries):
        path = root / 'test.tar.xz'
        with tarfile.open(path, 'w:xz') as bundle:
            for name, link in entries:
                item = tarfile.TarInfo(name)
                if link is not None:
                    item.type = tarfile.SYMTYPE
                    item.linkname = link
                    bundle.addfile(item)
                else:
                    item.size = 1
                    bundle.addfile(item, io.BytesIO(b'x'))
        return path

    def test_relative_links_and_unicode(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            archive = self.archive(root, [('BigSur/index.theme', None),
                ('BigSur-dark/index.theme', None), ('BigSur/ícono con espacio.svg', None),
                ('BigSur-dark/link.svg', '../BigSur/ícono con espacio.svg')])
            icons.unpack(archive, root / 'out')
            self.assertEqual((root / 'out/BigSur-dark/link.svg').read_text(), 'x')

    def test_reject_escape(self):
        for entry in [('../escape', None), ('/absolute', None), ('link', '../../escape')]:
            with self.subTest(entry=entry), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                archive = self.archive(root, [entry])
                with self.assertRaises(ValueError):
                    icons.unpack(archive, root / 'out')


if __name__ == '__main__':
    unittest.main()
