"""Release packaging boundary checks; synthetic files, no game/artwork bytes."""
import importlib.util
import json
from pathlib import Path
import pytest

from defjam_tools import menu_release as release

def test_native_mapping_cannot_accidentally_include_wide_entries(tmp_path):
    manifest=tmp_path/'manifest.ini'
    a,b='a'*64,'b'*64
    manifest.write_text('[textures]\n'+a+'=textures/a.png\n[wide]\n'+b+'=-512:wide/b.png\n')
    assert dict(release.mappings(manifest,'textures'))=={a:'textures/a.png'}


def test_component_files_cannot_escape_the_component(tmp_path):
    root=tmp_path/'component';root.mkdir()
    (root/'native.png').write_bytes(b'synthetic input')
    (tmp_path/'outside.png').write_bytes(b'outside')
    assert release.safe_file(root,'native.png')==root/'native.png'
    with pytest.raises(ValueError,match='escapes root'):
        release.safe_file(root,'../outside.png')


def test_component_symlink_cannot_escape_the_component(tmp_path):
    root=tmp_path/'component';root.mkdir()
    (tmp_path/'outside.png').write_bytes(b'outside')
    try:
        (root/'link.png').symlink_to(tmp_path/'outside.png')
    except OSError as error:
        if getattr(error, 'winerror', None) == 1314:
            pytest.skip('Windows symlink privilege unavailable; traversal checked separately')
        raise
    with pytest.raises(ValueError,match='escapes root'):
        release.safe_file(root,'link.png')
