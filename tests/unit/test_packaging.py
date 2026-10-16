import json
from pathlib import Path
import subprocess
import sys

import pytest
from defjam_tools import cli, paths, texture_workshop, model_workshop


def test_profile_paths_are_relative_to_profile_and_explicit_flags_win(tmp_path):
    profile=tmp_path/'profile.json'
    profile.write_text(json.dumps(dict(schema=1,corpus='corpus',workspace='work',port=8768)))
    parsed=cli.read_profile(profile)
    assert parsed['workspace']==str(tmp_path/'work')
    assert cli.dispatch_args('serve',['--port','8769'],parsed)==['serve','--corpus',str(tmp_path/'corpus'),'--workspace',str(tmp_path/'work'),'--port','8768','--port','8769']
    assert cli.dispatch_args('workshop',['import','--asset','a'],parsed)[0]=='import'


@pytest.mark.parametrize('value',[dict(schema=2),dict(schema=1,port=1),dict(schema=1,workspace=''),dict(schema=1,unexpected=True)])
def test_invalid_profile_is_rejected(tmp_path,value):
    p=tmp_path/'profile.json';p.write_text(json.dumps(value))
    with pytest.raises(ValueError):cli.read_profile(p)


def test_source_tree_private_output_guard_covers_root_not_only_package():
    root=paths.source_root()
    assert (root/'pyproject.toml').is_file()
    with pytest.raises(ValueError):paths.require_private_output(root/'private-assets')


def test_all_ui_and_vendor_resources_exist_without_recomp_checkout():
    here=texture_workshop.HERE
    for route in [('model-viewer',),('model-viewer.js',),('model-viewer.css',),('vendor','three.core.min.js'),('vendor','loaders','GLTFLoader.js'),('vendor','utils','BufferGeometryUtils.js')]:
        assert model_workshop.static_file(route,here)[0]
    for name in ['texture_workshop.html','texture_workshop.js','texture_workshop.css','hd_corpus.html','profiles/hd-runtime-aliases.json']:
        assert (here/name).is_file()


def test_cli_runs_as_module_from_an_unrelated_directory(tmp_path):
    result=subprocess.run([sys.executable,'-m','defjam_tools','--version'],cwd=tmp_path,capture_output=True,text=True,check=True)
    assert '0.1.0' in result.stdout
