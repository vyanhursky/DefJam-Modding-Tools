from pathlib import Path
import shutil
import subprocess

import pytest


@pytest.mark.skipif(not shutil.which('node'), reason='Node is required for wardrobe selection tests')
def test_color_changes_preserve_wearing_style_and_original_outfit_indices():
    subprocess.run(['node', str(Path(__file__).with_name('caf_wardrobe.mjs'))], check=True, capture_output=True, text=True)
