import hashlib
import json

import pytest
from defjam_tools import fighter_motion as tool


def inputs(tmp_path):
    files=[tmp_path/name for name in ('model.o','face.o','subject.ord','subject.orl','counterpart.ord','counterpart.orl')]
    for i,path in enumerate(files):
        path.write_bytes(('synthetic-'+str(i)).encode())
    return files


def test_pair_export_uses_shared_compilation_and_explicit_component_fragment(tmp_path,monkeypatch):
    files=inputs(tmp_path)
    def shared(recomp,game,command,**options):
        assert command=='export-pair'
        request=json.loads(options['pair_request'].read_text())
        assert request['template_choice']==21
        assert request['model']['sha256']==hashlib.sha256(files[0].read_bytes()).hexdigest()
        assert request['counterpart']['links']['path']==str(files[5])
        return {'protocol':'fighter-authoring-api-1','ok':True,'component_compilation':True,
                'native_playtest':False,'graphs':{'subject':{'format':'fighter-motion-graph-1'},
                                                'counterpart':{'format':'fighter-motion-graph-1'}}}
    monkeypatch.setattr(tool,'contract',shared)
    destination=tmp_path/'export'
    report=tool.export_pair('recomp','game',*files,21,destination)
    source=json.loads((destination/'pair-source.json').read_text())
    assert source['template_choice']==21
    for role in ('subject','counterpart'):
        assert hashlib.sha256((destination/source[role]['path']).read_bytes()).hexdigest()==source[role]['sha256']
    assert not report['native_playtest']
    assert {p.name for p in destination.iterdir()}=={'subject.json','counterpart.json','pair-source.json','pair-export.json'}
    with pytest.raises(ValueError,match='already exists'):
        tool.export_pair('recomp','game',*files,21,destination)


def test_failed_runtime_validation_never_publishes_component(tmp_path,monkeypatch):
    files=inputs(tmp_path)
    def reject(*args,**kwargs):
        raise ValueError('Source motion has unsupported parent controls')
    monkeypatch.setattr(tool,'contract',reject)
    with pytest.raises(ValueError,match='controls'):
        tool.export_pair('recomp','game',*files,21,tmp_path/'export')
    assert not (tmp_path/'export').exists()


@pytest.mark.parametrize('choice',[True,-1,82])
def test_invalid_template_choice_leaves_no_output(tmp_path,choice):
    files=inputs(tmp_path)
    with pytest.raises(ValueError,match='template choice'):
        tool.export_pair('recomp','game',*files,choice,tmp_path/'export')
    assert not (tmp_path/'export').exists()
