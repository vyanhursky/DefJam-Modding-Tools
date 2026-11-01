"""Shared camera and paging regression without artwork or a private workspace."""
from pathlib import Path
import shutil
import subprocess
import unittest

@unittest.skipUnless(shutil.which('node'), 'Node is required for shared camera regression')
class PackControlsTests(unittest.TestCase):
    def test_shared_mouse_camera_and_page_sizes(self):
        subprocess.run(['node', str(Path(__file__).with_name('pack_controls.mjs'))],
                       check=True, capture_output=True, text=True)
