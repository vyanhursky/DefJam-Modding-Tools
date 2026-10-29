#!/usr/bin/env python3
"""Read-only live identity/PNG/GLB/review checks for the wave-four receipt."""
import argparse
import hashlib
import io
import json
from pathlib import Path
import struct
from urllib.request import urlopen
import numpy as np
from PIL import Image


def main():
    ap=argparse.ArgumentParser(description=__doc__); ap.add_argument('--root',type=Path,required=True)
    args=ap.parse_args(); root=args.root; base='http://127.0.0.1:8768'
    def raw(path):
        with urlopen(base+path, timeout=90) as r: return r.read()
    def api(path): return json.loads(raw(path))
    def sha(b): return hashlib.sha256(b).hexdigest()
    before=json.loads((root/'before-workshop.json').read_text(encoding='utf8'))
    oldmodels=json.loads((root/'before-models.json').read_text(encoding='utf8'))
    receipt=json.loads((root/'import-review-receipt.json').read_text(encoding='utf8'))
    state=api('/api/export-review'); models=api('/api/models'); config=api('/api/config'); workspace=Path(config['workspace'])
    for aid, rows in before['candidates'].items():
        for c in rows:
            assert c in state['candidates'][aid]
            assert sha((workspace/c['path']).read_bytes())==c['sha256']
    for request in before['requests']: assert request in state['requests']
    report=dict(schema=1,old_candidate_metadata_and_pngs_exact=True,old_requests_retained=True, records=[])
    for name, row in receipt['current'].items():
        aid, rev=row['asset'],row['revision']; detail=api('/api/asset/'+aid)
        candidate=next(c for c in detail['candidates'] if c['id']==rev)
        png=raw('/api/image/'+aid+'/'+rev); assert sha(png)==row['sha256']==candidate['sha256']
        im=Image.open(io.BytesIO(png)); assert im.size==(2048,2048) and im.mode=='RGBA'
        faithful=Image.open(io.BytesIO(raw('/api/image/'+aid+'/faithful')))
        assert np.array_equal(np.asarray(im)[...,3],np.asarray(faithful)[...,3])
        view=models['state']['views'][name]; assert view['right']==rev
        for key,value in oldmodels['state']['views'][name].items():
            if name in ('redman','blaze','rollins') and key=='right': continue
            assert view[key]==value
        glb=raw('/api/model/'+name+'/model.glb?revision='+rev)
        assert struct.unpack_from('<4sII',glb)==(b'glTF',2,len(glb))
        offset=12; chunks={}
        while offset<len(glb):
            length,kind=struct.unpack_from('<II',glb,offset); offset+=8
            chunks[kind]=glb[offset:offset+length]; offset+=length
        doc=json.loads(chunks[0x4e4f534a]); imageview=doc['bufferViews'][doc['images'][0]['bufferView']]
        start=imageview.get('byteOffset',0); embedded=chunks[0x004e4942][start:start+imageview['byteLength']]
        # Export normalizes PNG encoding; compare decoded RGBA, not compression.
        embedded_image=Image.open(io.BytesIO(embedded)).convert('RGBA')
        assert np.array_equal(np.asarray(embedded_image),np.asarray(im))
        r=candidate['review']; accepted=name in ('nyne','trejo')
        assert r['status']==('approved' if accepted else 'needs_revision' if name=='rollins' else 'unreviewed')
        assert not r['selected'] and not r['game_verified']
        report['records'].append(dict(fighter=name, revision=rev, sha256=sha(png),
                                      png_hash_and_glb_pixels_exact=True, material_alpha_exact=True,
                                      review_status=r['status'], selected=False, game_verified=False))
    assert models['state']['fighter']==oldmodels['state']['fighter']
    for path, text in [('/model-viewer','revision-notice'),('/model-viewer.js','Older texture on the right'),('/model-viewer.css','.revision-notice')]:
        assert text.encode() in raw(path)
    report.update(total_candidates=sum(map(len,state['candidates'].values())),
                  archived=sum('archived' in r['tags'] for r in state['reviews'].values()),
                  models=len(models['models']), camera_preferences_and_left_choices_exact=True,
                  browser_visual_test='blocked by existing URL policy; no bypass',
                  rollins_body='incomplete; built-in output moderation blocked generation')
    (root/'verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
    print(json.dumps(report,indent=2))


if __name__=='__main__': main()
