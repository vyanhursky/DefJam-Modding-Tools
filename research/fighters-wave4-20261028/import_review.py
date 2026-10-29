#!/usr/bin/env python3
"""Import headwear repairs and reconcile owner feedback through the live writer.

Backed-up reviews are version checked. Never discard a concurrent review edit.
Old notes/images survive in the immutable pre-operation private backup/history.
"""
import argparse
import base64
import copy
import hashlib
import json
from pathlib import Path
from urllib.request import Request, urlopen


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root', type=Path, required=True)
    args=ap.parse_args(); root=args.root; base='http://127.0.0.1:8768'; token=None
    def api(path, payload=None):
        headers={} if payload is None else {'Content-Type':'application/json','X-Workshop-Token':token}
        with urlopen(Request(base+path, data=None if payload is None else json.dumps(payload).encode(), headers=headers), timeout=90) as r:
            return json.load(r)
    config=api('/api/config'); token=config['token']; workspace=Path(config['workspace'])
    assert root.parents[1]==workspace
    original=json.loads((root/'before-workshop.json').read_text(encoding='utf8'))
    oldplans=json.loads((root.parent/'fighters-wave3-20261028/review-import-receipt.json').read_text(encoding='utf8'))['imported']
    current={r['fighter']:dict(r) for r in oldplans}
    journal=root/'import-review-receipt.json'
    done=json.loads(journal.read_text(encoding='utf8')) if journal.exists() else dict(schema=1, imported=[], reviews=[], archived=[])
    def save(): journal.write_text(json.dumps(done, indent=2)+'\n', encoding='utf8')
    for row in json.loads((root/'assembly-receipt.json').read_text(encoding='utf8'))['records']:
        name, aid=row['fighter'], row['asset']; path=Path(row['output'])
        assert hashlib.sha256(path.read_bytes()).hexdigest()==row['output_sha256']
        label=name.title()+' · v4 · Restored headwear gaps + source palette'
        candidate=next((c for c in api('/api/asset/'+aid)['candidates'] if c['sha256']==row['output_sha256'] and c['label']==label and c['parent']==row['parent']), None)
        if not candidate:
            note='Owner feedback2026-10-28: repair missed headwear. Reuse raw v3; only verified cloth inside omitted holds may change. Keep all other v3 pixels exact. No new generation.\n'+json.dumps(row)
            request=api('/api/request', dict(asset=aid, style='faithful', revision=row['parent'], note=note))
            candidate=api('/api/import', dict(asset=aid, image=base64.b64encode(path.read_bytes()).decode(), label=label, style='faithful', parent=row['parent'], prompt=note, request_id=request['id']))
        new=dict(fighter=name, asset=aid, revision=candidate['id'], sha256=candidate['sha256'], label=label)
        current[name]=new
        if not any(r['revision']==candidate['id'] for r in done['imported']): done['imported'].append(new); save()
    def review(aid, rev, changes):
        key=aid+':'+rev
        if any(r['key']==key for r in done['reviews']): return
        detail=api('/api/asset/'+aid)
        old=detail['review'] if rev=='asset' else next(c['review'] for c in detail['candidates'] if c['id']==rev)
        backed=original['reviews'].get(key)
        if backed and old['version']!=backed['version']:
            raise ValueError('Concurrent review change; preserve and reconcile manually: '+key)
        payload=copy.deepcopy(old); payload.update(changes)
        saved=api('/api/review/'+aid+'/'+rev, payload)
        done['reviews'].append(dict(key=key, before=old, after=saved)); save()
    notes={
      'nyne': 'Owner feedback2026-10-28: Nyne looks good. Current v3 visually accepted; keep this exact draft. No outstanding revision request. In-game verification and pack selection remain separate.',
      'trejo': 'Owner feedback2026-10-28: Trejo looks good. Current v3 visually accepted; keep this exact draft. Earlier tattoo revision requests are resolved for this review. Preserve Debbie Danielle handwriting paths and the original buckle animal/tree placement. In-game verification and pack selection remain separate.',
      'redman': 'v4 for review: recovered the missed headwear strips/panel from existing raw v3 using actual clothing UV coverage. All pixels outside the repair mask, including accepted skin/body/face, and full alpha are exact v3. Check the repaired headwear from front, sides and back. Awaiting owner approval.',
      'blaze': 'v4 for review: restored head/face/hair and source-matched skin/clothes from v3, plus repaired cap corner. The previously displayed revision was published v1, with its original head and warmer body palette. v4 is now the saved right comparison. Check likeness, beard/hair, cap, jersey/denim color and neck join against Original in unlit RGB. Awaiting owner approval.',
      'rollins': 'INCOMPLETE: v3 restores head/face/hair only. Body, arm tattoos, trousers and boots remain Faithful HD, not imagegen-restored. The new body attempt on2026-10-28 was blocked by the image service output safety filter; no output imported. Head retained. Do not treat this fighter as complete or ready for bulk calibration.'}
    for name, row in current.items():
        accepted=name in ('nyne','trejo')
        review(row['asset'], row['revision'], dict(notes=notes[name], flag=not accepted,
               status='approved' if accepted else 'needs_revision' if name=='rollins' else 'unreviewed'))
        shared='Current review: '+notes[name]
        detail=api('/api/asset/'+row['asset']); changes=dict(notes=shared, flag=not accepted, status='unreviewed')
        if name=='blaze':
            regions=copy.deepcopy(detail['review']['regions'])
            for region in regions:
                if region['kind']=='protect' and 'face' in region['note'].lower():
                    region.update(kind='reference', note='Owner-authorized head/face/hair restoration since2026-10-28. Preserve likeness, proportions and expression; original face is the reference.')
            changes.update(regions=regions, tags=[t for t in detail['review']['tags'] if t!='face-preserve'])
        review(row['asset'], 'asset', changes)
    # Preserve old immutable draft provenance; summarize why they were superseded.
    for name in ('blaze','redman'):
        old=next(r for r in oldplans if r['fighter']==name)
        review(old['asset'], old['revision'], dict(flag=False, notes='Superseded by current v4, which repairs omitted headwear while preserving this v3 elsewhere. Current review notes are on the child. Exact earlier notes retained in experiments/fighters-wave4-20261028/before-workshop.json.'))
    models=api('/api/models'); active=models['state'].get('fighter'); before_views=copy.deepcopy(models['state']['views'])
    for name in ('redman','blaze'):
        view=copy.deepcopy(api('/api/models')['state']['views'][name]); view['right']=current[name]['revision']
        api('/api/model-view', dict(fighter=name, view=view))
    if active: api('/api/model-view', dict(fighter=active, view=api('/api/models')['state']['views'][active]))
    after_views=api('/api/models')['state']['views']
    for name, old in before_views.items():
        for key in old:
            if name in ('redman','blaze') and key=='right': continue
            assert old[key]==after_views[name][key]
    # Archive obsolete choices, preserving approved/selected, published0.1, left
    # comparisons and the 2D session's chosen lanes/target. Never remove files.
    state=api('/api/export-review'); keep={r['revision'] for r in current.values()}|{'r-af704d282bab415a','r-f90e9080f10840a3','r-342bd7dadb964b67'}
    for v in after_views.values(): keep.update([v['left'],v['right']])
    keep.update(state.get('session',{}).get('lanes',{}).values()); keep.add(state.get('session',{}).get('target'))
    for aid in {r['asset'] for r in current.values()}:
        for c in api('/api/asset/'+aid)['candidates']:
            r=c['review']
            if c['id'] in keep or r['selected'] or r['status']=='approved' or 'archived' in r['tags']: continue
            payload=copy.deepcopy(r); payload['tags'].append('archived')
            api('/api/review/'+aid+'/'+c['id'],payload)
            done['archived'].append(dict(asset=aid,revision=c['id'],prior_review=r)); save()
    done.update(current=current, camera_and_other_view_fields_preserved=True, active_fighter_preserved=True,
                no_art_removed=True, published_0_1_unchanged=True, notes_backup='before-workshop.json')
    save()
    print(json.dumps(dict(current={k:r['revision'] for k,r in current.items()}, imported=len(done['imported']), reconciled_reviews=len(done['reviews']), archived=len(done['archived'])), indent=2))


if __name__=='__main__': main()
