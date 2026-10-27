#!/usr/bin/env python3
"""Assemble wave-two drafts in an isolated staging workspace, never the live one.

Inputs: private root prepared with staging-workshop, before/workshop.json,
raw/*.png and prompt JSONs; accepted corpus. No generation, approvals or installs.
"""
import argparse, io, json, hashlib
from pathlib import Path
import numpy as np
from PIL import Image
from defjam_tools import color_trial as color, face_detail, model_workshop
from defjam_tools.texture_workshop import Workshop, WorkspaceLock, assemble_generated, empty_review


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def png(image):
    buffer=io.BytesIO();image.save(buffer,format='PNG',compress_level=3);return buffer.getvalue()


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--root',type=Path,required=True);ap.add_argument('--corpus',type=Path,required=True)
    args=ap.parse_args();root=args.root;workspace=root/'staging-workshop'
    if (root/'assembly.json').exists():ap.error('Existing assembly receipt; use immutable new inputs')
    before=json.loads((root/'before/workshop.json').read_text());store=Workshop(args.corpus,workspace)
    assert store.data['reviews']==before['reviews']
    face_prompts={j['name']:j['prompt'] for j in json.loads((root/'face-prompts.json').read_text())}
    prompts={j['name']:j['prompt'] for j in json.loads((root/'prompts.json').read_text())}
    definitions={
      'blaze':('5c9b3229151c2853656113a8df7e3f91effdef5ae68c9bdd567e5a71bbe9c91a','r-af704d282bab415a',[[.5,0,.5,.5]],[(200,700,620,1024)]),
      'nyne':('a25c4fdd4998993c94d18ad0f5169c7ad6e6b898c711482777303c7ba3a18517','r-f90e9080f10840a3',[[.5,0,.5,.51]],[(0,840,1024,1024)]),
      'trejo':('1900051b32443a33a745c088a08231d039d80c9eb96483f4b43456a2a3f68f24','r-342bd7dadb964b67',[[.49,0,.51,.51]],[(0,850,600,1024),(0,680,110,800)]),
      'redman':('61ca4a5526f266aa676e52bff3ac615eff3bb85f8d32f6375e81cce2da374c6b','',[[.49,0,.51,.5]],[]),
    }
    records=[]
    def request(aid,parent,prompt):
        job=store.queue_request(aid,'faithful',parent or 'asset',prompt)
        def update():
            next(j for j in store.data['requests'] if j['id']==job['id'])['prompt']=prompt
        store.transaction(update);return job['id']
    def imported(aid,raw,label,parent,prompt,job=''):
        item=store.import_candidate(aid,raw,label,'faithful',parent,prompt,request_id=job)
        review=empty_review();review.update(flag=True,notes='Owner-authorized wave-two review draft. Not approved/selected. Check likeness, UV seams, color, tattoos and material detail against source and 0.1. See candidate prompt for exact assembly and provenance.')
        store.save_review(aid,item['id'],review)
        return item
    with WorkspaceLock(workspace):
        for name,(aid,parent_id,protect,held) in definitions.items():
            baseline_path=store.image_path(aid,'faithful');ref=Image.open(baseline_path).convert('RGBA')
            geometry_path=workspace/'models'/name/'geometry.json';geometry=json.loads(geometry_path.read_text())
            index=json.loads(geometry_path.with_name('index.json').read_text());assert sha(geometry_path)==index['geometry_sha256']
            _,_,seams,_,_=color.geometry_masks(geometry,512,protect)
            if name=='redman':
                raw_path=root/'raw/redman-rich-detail-v1.png'
                raw,assembly=assemble_generated(raw_path.read_bytes(),baseline_path,store.asset(aid),dict(scale=4,preserve_alpha=True,protected_regions=protect))
                parent=Image.open(io.BytesIO(raw)).convert('RGBA')
            else:
                parent=Image.open(store.image_path(aid,parent_id)).convert('RGBA');assembly=None
            if name!='trejo':
                result,report,masks,verified=color.correct(ref,parent,geometry,protect,'source-palette',require_seams=bool(seams))
                for key,image in masks.items():image.save(root/'raw'/f'{name}-{key}.png')
                prompt=(prompts[name] if name=='redman' else 'Owner requested body/face color matching. Existing accepted body art is the edit target, Faithful reference controls palette.')
                recipe=dict(geometry_sha256=sha(geometry_path),reference_sha256=sha(baseline_path),body_report=report,seams=verified,assembly=assembly)
                text=prompt+'\nTechnical assembly (not an imagegen request): '+json.dumps(recipe)
                job=request(aid,'',prompts[name]) if name=='redman' else ''
                item=imported(aid,png(result),name.title()+' · Source palette v2' if name!='redman' else 'Redman · Rich Original Detail v1 · Source palette',parent_id,text,job)
                records.append(dict(fighter=name,kind='body-palette',revision=item['id'],parent=parent_id,report=recipe));parent_id=item['id'];parent=result
            if name=='redman':continue
            raw_path=root/'raw'/f'{name}-face-headwear.png'
            face_seams=[dict(body=s['face']) for s in seams]
            guard=color.seam_guard(2048,face_seams,inner=12,outer=48)
            result,report=face_detail.merge(ref,parent,Image.open(raw_path),(1024,0,2048,1024),held,guard)
            # Every proven face-side seam core stays baseline-identical.
            core=guard>=1
            core[:,:1024]=False;core[1024:]=False
            assert np.array_equal(np.asarray(result)[core],np.asarray(ref)[core])
            recipe=dict(face_report=report,face_seam_edges=len(seams),geometry_sha256=sha(geometry_path),reference_sha256=sha(baseline_path),raw_sha256=sha(raw_path),processor_sha256=sha(Path(face_detail.__file__)))
            prompt=face_prompts[name]+'\nOwner authorization: 2026-10-27 improve face textures/headwear, body/face color matching, preserve likeness.\nTechnical assembly: '+json.dumps(recipe)
            job=request(aid,parent_id,face_prompts[name]);item=imported(aid,png(result),name.title()+' · face/headwear detail v2 · palette matched',parent_id,prompt,job)
            records.append(dict(fighter=name,kind='face-headwear',revision=item['id'],parent=parent_id,report=recipe))
        aid='4f1b25d80e683f2a80e7071d5a50c576066ec49831419048f5ff7f15dccdd31d'
        for attempt,error in enumerate(json.loads((root/'rollins-failures.json').read_text()),1):
            job=request(aid,'',error['prompt'])
            def blocked():
                q=next(q for q in store.data['requests'] if q['id']==job);q.update(status='blocked',error=error['error'])
            store.transaction(blocked)
        assert all(store.data['reviews'][key]==value for key,value in before['reviews'].items())
        assert all(store.candidate(aid,c['id'])==c for aid,items in before['candidates'].items() for c in items)
        models=model_workshop.catalog(store)
        assert len(models['models'])==5
        for model in models['models']:
            assert model_workshop.model_glb(store,model['id'],'faithful')[:4]==b'glTF'
        for item in records:
            aid=definitions[item['fighter']][0]
            assert model_workshop.model_glb(store,item['fighter'],item['revision'])[:4]==b'glTF'
        receipt=dict(schema=1,records=records,total_candidates=sum(map(len,store.data['candidates'].values())),total_requests=len(store.data['requests']),models=5,old_candidates_and_reviews_exact=True,live_workspace_modified=False,rollins_generation_blocked=True)
        (root/'assembly.json').write_text(json.dumps(receipt,indent=2)+'\n')
        print(json.dumps({k:v for k,v in receipt.items() if k!='records'},indent=2))
        for item in records:print(item['fighter'],item['kind'],item['revision'])


if __name__=='__main__':main()
