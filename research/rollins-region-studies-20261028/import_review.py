#!/usr/bin/env python3
"""Import two unapproved regional studies through the existing live writer."""
import argparse,base64,copy,hashlib,json
from pathlib import Path
from urllib.request import Request,urlopen


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root',type=Path,required=True);ap.add_argument('--stage',type=Path,required=True)
    args=ap.parse_args();root=args.root;token=None
    def api(path,payload=None):
        with urlopen(Request('http://127.0.0.1:8768'+path,data=None if payload is None else json.dumps(payload).encode(),headers={} if payload is None else {'Content-Type':'application/json','X-Workshop-Token':token}),timeout=90) as r:return json.load(r)
    config=api('/api/config');token=config['token'];assert Path(config['workspace'])==root.parents[1]
    before=api('/api/export-review');models=api('/api/models')
    (root/'before-import-workshop.json').write_text(json.dumps(before,indent=2)+'\n',encoding='utf8')
    (root/'before-import-models.json').write_text(json.dumps(models,indent=2)+'\n',encoding='utf8')
    receipts=json.loads((args.stage/'receipt.json').read_text(encoding='utf8'))
    prompts=json.loads((root/'prompts.json').read_text(encoding='utf8'))
    journal=root/'import-receipt.json';done=json.loads(journal.read_text(encoding='utf8')) if journal.exists() else dict(schema=1,imported=[])
    def save():journal.write_text(json.dumps(done,indent=2)+'\n',encoding='utf8')
    for row in receipts['records']:
        aid=row['asset'];path=Path(row['output']);assert hashlib.sha256(path.read_bytes()).hexdigest()==row['output_sha256']
        letter='A' if row['method']=='direct' else 'B'
        label='Henry Rollins · v5'+letter+' · '+('Localized tattoos + skin detail' if letter=='A' else 'Source contours + skin/ink grain')
        candidate=next((c for c in api('/api/asset/'+aid)['candidates'] if c['sha256']==row['output_sha256'] and c['parent']==row['parent'] and c['label']==label),None)
        if not candidate:
            brief='Owner-authorized regional studies: five successful built-in generations; this request records their technical assembly, not a new imagegen call.\n'+json.dumps(prompts)
            job=api('/api/request',dict(asset=aid,style='faithful',revision=row['parent'],note=brief))
            candidate=api('/api/import',dict(asset=aid,image=base64.b64encode(path.read_bytes()).decode(),label=label,style='faithful',parent=row['parent'],request_id=job['id'],prompt=brief+'\nAssembly:\n'+json.dumps(row)))
        detail=api('/api/asset/'+aid);review=next(c['review'] for c in detail['candidates'] if c['id']==candidate['id'])
        note=('v5A: localized imagegen sun/arm artwork plus generated plain skin detail. Known SEARCH & DESTROY lettering regenerated; tiny uncertain arm/emblem lettering stays exact source. Inspect sun rays/face, script alignment, arm designs and body/head join; stronger interpretation, not authenticated reconstruction. '
              if letter=='A' else 'v5B: generated skin grain plus tiny generated ink-detail residuals inside existing dark ink. Original tattoo contours and all held lettering remain the source; fine interpretation is deliberately restrained. ')
        note+='Both retain approved v4 head/hair/clothing/boots, all non-skin pixels, material alpha and16paired head/body seam cores exactly. Small emblem uses source contours in both; raw decal and direct emblem redraw were not adopted. New body draft is UNAPPROVED/unselected. Compare with v4 and the other v5 option; receipts/prompts/raw in experiments/rollins-region-studies-20261028/.'
        if review['notes']!=note:
            review.update(notes=note,flag=True,status='unreviewed',tags=['wave5','regional-studies',row['method'],'body-review'])
            api('/api/review/'+aid+'/'+candidate['id'],review)
        saved=dict(method=row['method'],asset=aid,revision=candidate['id'],sha256=candidate['sha256'],label=label)
        if not any(x['revision']==saved['revision'] for x in done['imported']):done['imported'].append(saved);save()
    aid=done['imported'][0]['asset'];detail=api('/api/asset/'+aid);old=detail['review'];backed=before['reviews'].get(aid+':asset')
    if backed and old['version']!=backed['version']:raise ValueError('Concurrent shared review change; preserve it')
    shared=copy.deepcopy(old);shared.update(flag=True,status='unreviewed',notes='New v5A/v5B body studies are ready: regional tattoo art and skin-material generations succeeded. Existing v4 head/hair/clothes/boots are owner accepted and retained exactly in both. A is richer localized tattoo detail; B retains source contours with subtle ink/skin grain. Tiny uncertain lettering held; small emblem stays source-constrained. Review the new body details before approval. Previous full-atlas blocked attempts remain in history; no longer an active generation blocker. No new draft approved/selected or game verified.')
    api('/api/review/'+aid+'/asset',shared)
    listing=api('/api/models');active=listing['state'].get('fighter');oldview=copy.deepcopy(listing['state']['views']['rollins']);view=copy.deepcopy(oldview)
    view['right']=next(r['revision'] for r in done['imported'] if r['method']=='direct')
    api('/api/model-view',dict(fighter='rollins',view=view))
    if active:api('/api/model-view',dict(fighter=active,view=api('/api/models')['state']['views'][active]))
    actual=api('/api/models')['state'];assert actual.get('fighter')==active
    for key,value in oldview.items():
        if key!='right':assert actual['views']['rollins'][key]==value
    done.update(shared_review_before=old,shared_review_after=shared,other_view_fields_preserved=True,right_revision=view['right'],new_drafts_approved=False)
    save();print(json.dumps(done['imported'],indent=2))


if __name__=='__main__':main()
