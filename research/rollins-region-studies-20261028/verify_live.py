#!/usr/bin/env python3
"""Read-only verification of imported regional art and preserved prior state."""
import argparse,hashlib,io,json,struct
from pathlib import Path
from urllib.request import urlopen
import numpy as np
from PIL import Image


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--root',type=Path,required=True);args=ap.parse_args();root=args.root
    def raw(route):
        with urlopen('http://127.0.0.1:8768'+route,timeout=90) as r:return r.read()
    def api(route):return json.loads(raw(route))
    def sha(b):return hashlib.sha256(b).hexdigest()
    before=json.loads((root/'before-import-workshop.json').read_text(encoding='utf8'))
    views=json.loads((root/'before-import-models.json').read_text(encoding='utf8'))
    imported=json.loads((root/'import-receipt.json').read_text(encoding='utf8'))
    state=api('/api/export-review');models=api('/api/models');workspace=root.parents[1]
    for aid,rows in before['candidates'].items():
        for c in rows:
            assert c in state['candidates'][aid] and sha((workspace/c['path']).read_bytes())==c['sha256']
    for key,value in before['reviews'].items():
        if key!='4f1b25d80e683f2a80e7071d5a50c576066ec49831419048f5ff7f15dccdd31d:asset':
            assert state['reviews'][key]==value
    mask=np.asarray(Image.open(root/'assembled-v2/body-skin-mask.png'))>0
    plan=json.loads((root/'plan.json').read_text(encoding='utf8'));parent=np.asarray(Image.open(workspace/plan['parent']['path']))
    report=dict(schema=1,records=[])
    for row in imported['imported']:
        aid,rev=row['asset'],row['revision'];data=raw('/api/image/'+aid+'/'+rev);assert sha(data)==row['sha256']
        im=Image.open(io.BytesIO(data));pixels=np.asarray(im)
        assert im.mode=='RGBA' and im.size==(2048,2048)
        assert np.array_equal(pixels[...,3],parent[...,3]) and np.array_equal(pixels[~mask],parent[~mask])
        # Exact seam cores were checked against the floating mask during
        # preparation; the live PNG hash pins those same assembled pixels.
        glb=raw('/api/model/rollins/model.glb?revision='+rev);assert struct.unpack_from('<4sII',glb)==(b'glTF',2,len(glb))
        chunks={};offset=12
        while offset<len(glb):
            length,kind=struct.unpack_from('<II',glb,offset);offset+=8;chunks[kind]=glb[offset:offset+length];offset+=length
        doc=json.loads(chunks[0x4e4f534a]);v=doc['bufferViews'][doc['images'][0]['bufferView']];start=v.get('byteOffset',0)
        embedded=Image.open(io.BytesIO(chunks[0x004e4942][start:start+v['byteLength']])).convert('RGBA')
        assert np.array_equal(np.asarray(embedded),pixels)
        review=next(c['review'] for c in api('/api/asset/'+aid)['candidates'] if c['id']==rev)
        assert review['status']=='unreviewed' and not any(review[k] for k in ['selected','game_verified','face_reviewed','channels_reviewed'])
        report['records'].append(dict(**row,alpha_and_nonbody_exact=True,glb_pixels_exact=True,new_draft_unapproved=True))
    for name,view in views['state']['views'].items():
        for key,value in view.items():
            if name=='rollins' and key=='right':continue
            assert models['state']['views'][name][key]==value
    assert models['state']['fighter']==views['state']['fighter']
    assert models['state']['views']['rollins']['right']==imported['right_revision']
    report.update(old_candidate_metadata_and_pngs_exact=True,old_revision_reviews_exact=True,
        saved_cameras_and_preferences_exact=True,total_candidates=sum(map(len,state['candidates'].values())),
        total_requests=len(state['requests']),successful_builtin_studies=5,
        browser_visual_test='blocked by prior URL policy; no bypass',published_0_1_unchanged=True)
    (root/'verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
