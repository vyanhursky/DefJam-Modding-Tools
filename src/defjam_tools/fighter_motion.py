"""Export paired typed graphs through the runtime's verified compiler."""
import hashlib
import json
from pathlib import Path
import tempfile

from .fighter_pack import contract,ordinary

MAX_FILE=64*1024**2


def export_pair(recomp,game,model,face,subject_data,subject_links,counterpart_data,counterpart_links,choice,destination,
                *,tags=None,cameras=None):
    destination=ordinary(destination)
    if destination.exists():
        raise ValueError('Pair destination already exists; choose a new folder')
    if type(choice) is not int or not 0<=choice<82:
        raise ValueError('Pair template choice must be between0 and81')
    if (tags is None)!=(cameras is None):
        raise ValueError('Paired timeline export requires both tags and camera source files')

    def spec(path):
        path=ordinary(path)
        with path.open('rb') as stream:
            data=stream.read(MAX_FILE+1)
        if not 0<len(data)<=MAX_FILE:
            raise ValueError('Pair input exceeds its file budget')
        return {'path':str(path),'sha256':hashlib.sha256(data).hexdigest()}

    request={'format':'fighter-pair-export-request-1','template_choice':choice,'model':spec(model),'face':spec(face),
             'subject':{'data':spec(subject_data),'links':spec(subject_links)},
             'counterpart':{'data':spec(counterpart_data),'links':spec(counterpart_links)}}
    if tags is not None:
        request.update(format='fighter-pair-export-request-2',tags=spec(tags),cameras=spec(cameras))
    destination.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.fighter-pair-',dir=destination.parent) as temporary:
        stage=Path(temporary)
        path=stage/'request.json';path.write_text(json.dumps(request,indent=2)+'\n',encoding='utf-8')
        result=contract(recomp,game,'export-pair',pair_request=path)
        if not result.get('component_compilation') or result.get('native_playtest') is not False:
            raise ValueError('Runtime did not compile the paired component')
        source={'template_choice':choice}
        outputs=[]
        for role in ('subject','counterpart'):
            data=(json.dumps(result['graphs'][role],indent=2)+'\n').encode('utf-8')
            (stage/(role+'.json')).write_bytes(data)
            outputs.append(role+'.json')
            source[role]={'path':role+'.json','sha256':hashlib.sha256(data).hexdigest()}
        if tags is not None:
            for role in ('subject_tags','counterpart_tags','camera'):
                value=result['timelines'][role]
                data=(json.dumps(value['timeline'] if role=='camera' else value,indent=2)+'\n').encode()
                name=role+'.json';(stage/name).write_bytes(data);outputs.append(name)
                descriptor={'path':name,'sha256':hashlib.sha256(data).hexdigest()}
                source[role]={'template':value['template'],'timeline':descriptor} if role=='camera' else descriptor
        report={k:v for k,v in result.items() if k not in ('graphs','timelines')}
        report.update(schema='fighter-pair-export-1',source=source)
        (stage/'pair-source.json').write_text(json.dumps(source,indent=2)+'\n',encoding='utf-8')
        (stage/'pair-export.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
        # Publish only after shared compilation succeeds. Exclusive destination
        # preserves an existing authoring workspace, including a create race.
        destination.mkdir()
        for name in [*outputs,'pair-source.json','pair-export.json']:
            with (destination/name).open('xb') as stream:
                stream.write((stage/name).read_bytes())
    return report
