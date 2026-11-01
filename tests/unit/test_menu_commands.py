"""Private input boundaries and the relocated menu builder, using synthetic art."""
import hashlib
import importlib
import json
from pathlib import Path
from types import SimpleNamespace
import sys
import zipfile
import pytest
from PIL import Image
from defjam_tools import menu_release


@pytest.mark.parametrize('name', ['menu_artwork','menu_pack','menu_wide','menu_branding','menu_release'])
def test_menu_cli_requires_explicit_private_inputs(name, monkeypatch):
    monkeypatch.setattr(sys, 'argv', ['test-menu'])
    with pytest.raises(SystemExit) as error:
        importlib.import_module('defjam_tools.'+name).main()
    assert error.value.code == 2


def test_release_uses_private_recipe_root_and_packaged_wide_exporter(tmp_path, monkeypatch):
    # No source-tree config or generated corpus is available to this build.
    private=tmp_path/'private';private.mkdir();config=private/'config';config.mkdir()
    art=tmp_path/'art';art.mkdir();base=tmp_path/'baseline';base.mkdir()
    components=tmp_path/'components';component=components/'synthetic';component.mkdir(parents=True)
    sid='a'*64;tile=component/'tile.png';Image.new('RGBA',(16,16),(90,80,70,255)).save(tile)
    digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    (component/'manifest.ini').write_text('[textures]\n'+sid+'=tile.png\n')
    receipt=component/'receipt.json';receipt.write_text(json.dumps({'entries':[{'source_id':sid,'output_sha256':digest(tile)}]}))
    catalogue=config/'approvals.json';catalogue.write_text(json.dumps({'approval_records':[],'reviewed_sources':[{'source_id':sid,'aliases':[{'width':4,'height':4}]}]}))
    (config/'registrations.json').write_text(json.dumps({'sources':[],'files':[]}))
    (config/'wide.json').write_text(json.dumps({'name':'Synthetic sides','status':'synthetic','layers':[],'stretch':[]}))
    (art/'transition.json').write_text('{"parts":[]}')
    recipe=config/'recipe.json';recipe.write_text(json.dumps(dict(runtime_registrations='config/registrations.json',wide_table='config/wide.json',transition_sources='transition.json',base_components=[],approved_components=['synthetic'],component_receipt_sha256={'synthetic':digest(receipt)},retained_core_inputs=[],retained_core_sha256={},expected_source_ids=1,name='Synthetic menu',version='0.0.0',status='synthetic')))
    # The child module must resolve the same source version during local and CI tests.
    import defjam_tools
    monkeypatch.setenv('PYTHONPATH',str(Path(defjam_tools.__file__).resolve().parents[1]))
    out=tmp_path/'exports'/'synthetic-menu'
    result=menu_release.build(SimpleNamespace(recipe=recipe,recipe_root=private,catalogue=catalogue,out=out,base_mods=base,approved_components=components,art_root=art))
    assert result['native_textures']==1 and result['wide_entries']==0
    assert (out/'textures'/f'{sid}.png').read_bytes()==tile.read_bytes()
    with zipfile.ZipFile(out.with_suffix('.zip')) as archive:
        assert archive.testzip() is None
    with pytest.raises(FileExistsError,match='Immutable'):
        menu_release.build(SimpleNamespace(recipe=recipe,recipe_root=private,catalogue=catalogue,out=out,base_mods=base,approved_components=components,art_root=art))
