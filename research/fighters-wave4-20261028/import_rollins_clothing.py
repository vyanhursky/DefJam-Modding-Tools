#!/usr/bin/env python3
"""Import the partial Rollins clothes pass through the single live writer."""
import argparse
import base64
import copy
import hashlib
import json
from pathlib import Path
from urllib.request import Request,urlopen


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--root',type=Path,required=True)
    root=ap.parse_args().root; token=None
    def api(path,payload=None):
        with urlopen(Request('http://127.0.0.1:8768'+path,data=None if payload is None else json.dumps(payload).encode(),headers={} if payload is None else {'Content-Type':'application/json','X-Workshop-Token':token}),timeout=90) as r:
            return json.load(r)
    config=api('/api/config');token=config['token'];assert Path(config['workspace'])==root.parents[1]
    before=api('/api/export-review');models=api('/api/models')
    for name,data in [('before-clothing-workshop.json',before),('before-clothing-models.json',models)]:
        if not (root/name).exists(): (root/name).write_text(json.dumps(data,indent=2)+'\n',encoding='utf8')
    row=json.loads((root/'rollins-clothing-receipt.json').read_text(encoding='utf8'))
    aid=row['asset'];path=Path(row['output']);assert hashlib.sha256(path.read_bytes()).hexdigest()==row['output_sha256']
    label='Henry Rollins · v4 · Restored head + trousers/boots · skin pending'
    candidate=next((c for c in api('/api/asset/'+aid)['candidates'] if c['label']==label and c['sha256']==row['output_sha256'] and c['parent']==row['parent']),None)
    if not candidate:
        job=api('/api/request',dict(asset=aid,style='faithful',revision=row['parent'],note=row['prompt']))
        candidate=api('/api/import',dict(asset=aid,image=base64.b64encode(path.read_bytes()).decode(),label=label,style='faithful',parent=row['parent'],prompt=row['prompt']+'\nTechnical assembly:\n'+json.dumps({k:v for k,v in row.items() if k!='prompt'}),request_id=job['id']))
    detail=api('/api/asset/'+aid);revision=candidate['id'];current=next(c['review'] for c in detail['candidates'] if c['id']==revision)
    note='PARTIAL v4: restored head retained from v3; black trousers and boots now imagegen-restored and source-palette matched. Check weave, seams, laces, leather and original black/gray contrast. Body skin and arm tattoos are byte-identical to v3/Faithful HD and STILL NOT RESTORED: the body generation was service-blocked. Head/skin/tattoos/alpha and all noncloth pixels stay exact. Awaiting clothing review; fighter incomplete.'
    if current['notes']!=note:
        current.update(notes=note,flag=True,status='needs_revision',tags=['wave4','clothing-restoration','body-skin-blocked'])
        api('/api/review/'+aid+'/'+revision,current)
    old=next(c['review'] for c in detail['candidates'] if c['id']==row['parent']);old['flag']=False
    if 'archived' not in old['tags']:old['tags'].append('archived');api('/api/review/'+aid+'/'+row['parent'],old)
    shared=detail['review'];shared.update(notes='Current review: '+note,flag=True,status='unreviewed')
    api('/api/review/'+aid+'/asset',shared)
    active=models['state'].get('fighter');view=copy.deepcopy(api('/api/models')['state']['views']['rollins']);view['right']=revision
    api('/api/model-view',dict(fighter='rollins',view=view))
    if active:api('/api/model-view',dict(fighter=active,view=api('/api/models')['state']['views'][active]))
    path=root/'import-review-receipt.json';receipt=json.loads(path.read_text(encoding='utf8'))
    oldcurrent=receipt['current']['rollins'];new=dict(fighter='rollins',asset=aid,revision=revision,sha256=candidate['sha256'],label=label)
    receipt.update(rollins_clothing_added=new,rollins_previous_current=oldcurrent)
    receipt['current']['rollins']=new
    (root/'final-current.json').write_text(json.dumps(receipt['current'],indent=2)+'\n',encoding='utf8')
    path.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf8')
    print(json.dumps(new,indent=2))


if __name__=='__main__':main()
