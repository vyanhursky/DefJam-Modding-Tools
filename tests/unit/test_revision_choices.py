"""Run the shared browser selection regression without a private workspace."""
from pathlib import Path
import shutil
import subprocess
import unittest

@unittest.skipUnless(shutil.which('node'), 'Node is required for browser selection regression tests')
class RevisionChoicesTests(unittest.TestCase):
    def test_saved_panes_targets_and_approval_survive_archive_toggle(self):
        subprocess.run(['node',str(Path(__file__).with_name('revision_choices.mjs'))],
                       check=True,capture_output=True,text=True)
