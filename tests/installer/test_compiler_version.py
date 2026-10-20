"""Build tooling runs on Python 3; client source remains Python 2.7 compatible."""
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from build_tools.compiler import sync_source_version


class SourceVersionTests(unittest.TestCase):
    def test_sync_preserves_other_code_and_line_endings(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / 'version.py'
            source.write_bytes(b"# coding: utf-8\r\nVERSION = '0.1.2-beta.5'  # runtime\r\nOTHER = 1\r\n")
            sync_source_version(root, {'version_source': 'version.py'}, '0.1.2-beta.6')
            self.assertEqual(source.read_bytes(),
                             b"# coding: utf-8\r\nVERSION = '0.1.2-beta.6'  # runtime\r\nOTHER = 1\r\n")
            stamp = source.stat().st_mtime_ns
            sync_source_version(root, {'version_source': 'version.py'}, '0.1.2-beta.6')
            self.assertEqual(source.stat().st_mtime_ns, stamp)
