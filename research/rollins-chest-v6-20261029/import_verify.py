#!/usr/bin/env python3
"""Import and verify a chest-only review child through the live single writer."""
import argparse,base64,copy,hashlib,io,json,struct
from pathlib import Path
from urllib.request import Request,urlopen
import numpy as np
from PIL import Image


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for k in ['root','stage']:ap.add_argument('--'+k,type=Path,required=True)
    args=ap.parse_args();root=args.root;token=None
    def api(path,payload=None,binary=False):
        with urlopen(Request('http://127.0.0.1:8768'+path,data=None if payload is None else json.dumps(payload).encode(),headers={} if payload is None else {'Content-Type':'application/json','X-Workshop-Token':token}),timeout=90) as r:
            data=r.read();return data if binary else json.loads(data)
    def sha(data):return hashlib.sha256(data).hexdigest()
    config=api('/api/config');token=config['token'];workspace=Path(config['workspace']);assert workspace==root.parents[1]
    before=api('/api/export-review');views=api('/api/models')
    (root/'before-import-workshop.json').write_text(json.dumps(before,indent=2)+'\n',encoding='utf8')
    (root/'before-import-models.json').write_text(json.dumps(views,indent=2)+'\n',encoding='utf8')
    row=json.loads((args.stage/'receipt.json').read_text(encoding='utf8'));aid=row['asset'];path=Path(row['output'])
    assert sha(path.read_bytes())==row['output_sha256']
    label='Henry Rollins · v6 · Chest skin + CREEPY CRAWL · v5A base'
    candidate=next((c for c in api('/api/asset/'+aid)['candidates'] if c['label']==label and c['sha256']==row['output_sha256'] and c['parent']==row['parent']),None)
    if not candidate:
        brief='Owner2026-10-29 prefers v5A and requests chest skin/tattoo restoration. Exact two submitted prompts and direct-skin result:\n'+(root/'prompts.json').read_text(encoding='utf8')+'\n'+(root/'blocked-chest-skin.json').read_text(encoding='utf8')
        job=api('/api/request',dict(asset=aid,style='faithful',revision=row['parent'],note=brief))
        candidate=api('/api/import',dict(asset=aid,image=base64.b64encode(path.read_bytes()).decode(),label=label,style='faithful',parent=row['parent'],request_id=job['id'],prompt=brief+'\nTechnical assembly:\n'+json.dumps(row)))
    rev=candidate['id'];changes=[];skipped=[]
    def review(target,note,status,flag=True,tags=None):
        d=api('/api/asset/'+aid);old=d['review'] if target=='asset' else next(c['review'] for c in d['candidates'] if c['id']==target)
        expected=before['reviews'].get(aid+':'+target)
        if expected and old['version']!=expected['version']:skipped.append(target);return
        payload=copy.deepcopy(old);payload.update(notes=note,status=status,flag=flag)
        if tags is not None:payload['tags']=list(dict.fromkeys([*payload['tags'],*tags]))
        saved=api('/api/review/'+aid+'/'+target,payload);changes.append(dict(target=target,before=old,after=saved))
    note='v6 chest-only child of preferred v5A. New imagegen CREEPY CRAWL tattoo restoration; front chest skin uses finer, stronger detail from the previously generated skin material with original diffuse hue/shading. Direct anatomical chest generation was service-blocked; no such output imported. Check chest grain scale, tattoo oval/strokes/lettering and joins. All pixels outside verified chest scope, including v5A back/arms/head/hair/clothes/boots, and alpha stay exact. New child UNAPPROVED/unselected; prompts/masks/receipts in experiments/rollins-chest-v6-20261029/.'
    review(rev,note,'unreviewed',tags=['wave6','chest-only','v5A-base'])
    review(row['parent'],'Owner2026-10-29 prefers v5A and requests chest skin/tattoo repair. Keep this as the exact preferred base. New v6 edits chest only; full v5A approval is pending that revision. Earlier notes are backed up in experiments/rollins-chest-v6-20261029/before-import-workshop.json.','needs_revision',tags=['preferred-base'])
    review('asset','Current review: '+note,'unreviewed')
    listing=api('/api/models');active=listing['state'].get('fighter');view=copy.deepcopy(listing['state']['views']['rollins']);view['right']=rev
    api('/api/model-view',dict(fighter='rollins',view=view))
    if active:api('/api/model-view',dict(fighter=active,view=api('/api/models')['state']['views'][active]))
    final=api('/api/export-review');models=api('/api/models')
    for asset,items in before['candidates'].items():
        for c in items:assert c in final['candidates'][asset] and sha((workspace/c['path']).read_bytes())==c['sha256']
    changed_keys={aid+':'+r['target'] for r in changes}
    for key,value in before['reviews'].items():
        if key not in changed_keys:assert final['reviews'][key]==value
    png=api('/api/image/'+aid+'/'+rev,binary=True);assert sha(png)==row['output_sha256']
    actual=np.asarray(Image.open(io.BytesIO(png)).convert('RGBA'))
    plan=json.loads((root/'plan.json').read_text(encoding='utf8'));parent=np.asarray(Image.open(workspace/plan['parent']['path']).convert('RGBA'))
    mask=np.asarray(Image.open(args.stage/'chest-scope-mask.png'))>0
    assert np.array_equal(actual[...,3],parent[...,3]) and np.array_equal(actual[~mask],parent[~mask])
    glb=api('/api/model/rollins/model.glb?revision='+rev,binary=True);assert struct.unpack_from('<4sII',glb)==(b'glTF',2,len(glb))
    chunks={};offset=12
    while offset<len(glb):
        length,kind=struct.unpack_from('<II',glb,offset);offset+=8;chunks[kind]=glb[offset:offset+length];offset+=length
    doc=json.loads(chunks[0x4e4f534a]);v=doc['bufferViews'][doc['images'][0]['bufferView']];start=v.get('byteOffset',0)
    embedded=np.asarray(Image.open(io.BytesIO(chunks[0x004e4942][start:start+v['byteLength']])).convert('RGBA'));assert np.array_equal(embedded,actual)
    for fighter,old in views['state']['views'].items():
        for key,value in old.items():
            if fighter=='rollins' and key=='right':continue
            assert models['state']['views'][fighter][key]==value
    assert models['state']['fighter']==views['state']['fighter']
    report=dict(schema=1,revision=rev,label=label,sha256=row['output_sha256'],review_changes=changes,skipped_concurrent_notes=skipped,
        old_candidate_metadata_and_pngs_exact=True,outside_chest_and_alpha_exact=True,glb_pixels_exact=True,
        camera_preferences_preserved=True,new_child_approved=False,total_candidates=sum(map(len,final['candidates'].values())),total_requests=len(final['requests']))
    (root/'import-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
    print(json.dumps({k:v for k,v in report.items() if k!='review_changes'},indent=2))


if __name__=='__main__':main()
