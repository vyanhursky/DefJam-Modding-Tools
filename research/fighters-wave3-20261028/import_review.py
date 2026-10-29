#!/usr/bin/env python3
"""Import verified drafts via the live single writer; soft-archive older choices.

Archived tags hide obsolete entries by default but retain IDs, PNGs, notes,
parents and prompts. Published0.1, approved/selected and saved-view choices stay.
"""
import argparse,base64,copy,hashlib,json
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.error import HTTPError


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--root',type=Path,required=True);ap.add_argument('--stage',type=Path,required=True);args=ap.parse_args()
    root=args.root;base='http://127.0.0.1:8768';token=None
    def api(path,payload=None):
        req=Request(base+path,data=None if payload is None else json.dumps(payload).encode(),headers={} if payload is None else {'Content-Type':'application/json','X-Workshop-Token':token})
        with urlopen(req,timeout=90) as response:return json.load(response)
    config=api('/api/config');token=config['token'];workspace=Path(config['workspace'])
    if workspace!=root.parents[1]:raise ValueError('Wrong live workspace')
    stage=json.loads((args.stage/'receipt.json').read_text());records=stage['records']
    journal=root/'import-state.json';done=json.loads(journal.read_text()) if journal.exists() else {'schema':1,'imported':[]}
    def save():journal.write_text(json.dumps(done,indent=2)+'\n')
    for row in records:
        name,aid=row['name'],row['source_id'];path=Path(row['output'])
        if hashlib.sha256(path.read_bytes()).hexdigest()!=row['output_sha256']:raise ValueError('Prepared output changed')
        detail=api('/api/asset/'+aid)
        label={'rollins':'Henry Rollins'}.get(name,name.title())+' · v3 · Natural head + original clothing palette'
        prior=next((c for c in detail['candidates'] if c['sha256']==row['output_sha256'] and c['parent']==row['parent'] and c['label']==label),None)
        if prior:
            if not any(j['revision']==prior['id'] for j in done['imported']):done['imported'].append(dict(fighter=name,asset=aid,revision=prior['id'],sha256=prior['sha256'],label=label));save()
            continue
        brief='Owner feedback2026-10-28: restore face/hair/head/headwear of all five, slightly more realistic skin/hair, source-color-match all clothes. Preserve likeness and expression.\n'+row['prompt']
        job=api('/api/request',{'asset':aid,'style':'faithful','revision':row['parent'] or 'asset','note':brief})
        prompt=row['prompt']+'\nTechnical assembly, input pins and checks:\n'+json.dumps({k:v for k,v in row.items() if k!='prompt'})
        candidate=api('/api/import',{'asset':aid,'image':base64.b64encode(path.read_bytes()).decode(),'label':label,'style':'faithful','parent':row['parent'],'prompt':prompt,'request_id':job['id']})
        assert candidate['sha256']==row['output_sha256']
        detail=api('/api/asset/'+aid);review=next(c['review'] for c in detail['candidates'] if c['id']==candidate['id'])
        review.update(flag=True,tags=['wave3','head-restoration','clothing-palette'],notes='Review v3: face/hair/head/headwear restored with slightly more realistic detail; source-palette correction covers clothing, shoes and headwear. Parent skin outside the head patch is unchanged; full alpha and standalone facial tiles held. Check likeness, hair, original garment palette, UV seams and material detail. Unapproved/unselected. Exact prompts, raw patches and processors retained in experiments/fighters-wave3-20261028/.')
        api('/api/review/'+aid+'/'+candidate['id'],review)
        done['imported'].append(dict(fighter=name,asset=aid,revision=candidate['id'],sha256=candidate['sha256'],label=label));save();print('Imported',name,candidate['id'],flush=True)
    assert len(done['imported'])==5
    before=api('/api/export-review');(root/'pre-archive-workshop.json').write_text(json.dumps(before,indent=2,ensure_ascii=False)+'\n')
    models=api('/api/models');keep={c['revision'] for c in done['imported']}|{'r-af704d282bab415a','r-f90e9080f10840a3','r-342bd7dadb964b67'}
    for view in models['state'].get('views',{}).values():keep.update(view.get(k,'') for k in ['left','right'])
    session=before.get('session',{});keep.add(session.get('target',''));keep.update(session.get('lanes',{}).values())
    fighterids={r['source_id'] for r in records};archived=[];skipped=[]
    for aid in fighterids:
        detail=api('/api/asset/'+aid)
        for candidate in detail['candidates']:
            review=candidate['review'];revision=candidate['id']
            if revision in keep or review['selected'] or review['status']=='approved' or 'archived' in review['tags']:continue
            if len(review['tags'])>=30:skipped.append(revision);continue
            payload=copy.deepcopy(review);payload['tags'].append('archived')
            try:saved=api('/api/review/'+aid+'/'+revision,payload)
            except HTTPError as error:
                if error.code==409:skipped.append(revision);continue
                raise
            for key,value in review.items():
                if key not in ('tags','version','updated'):assert saved[key]==value
            archived.append(dict(asset=aid,revision=revision,label=candidate['label'],sha256=candidate['sha256'],prior_tags=review['tags']))
    after=api('/api/export-review')
    for aid,items in before['candidates'].items():
        for candidate in items:
            assert candidate in after['candidates'][aid]
            assert hashlib.sha256((workspace/candidate['path']).read_bytes()).hexdigest()==candidate['sha256']
    report=dict(schema=1,imported=done['imported'],archived=archived,skipped_changed_or_full_tags=skipped,
                total_candidates=sum(map(len,after['candidates'].values())),archive_is_recoverable=True,
                no_pngs_removed_or_changed=True,published_0_1_and_saved_view_choices_retained=True)
    (root/'review-import-receipt.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Archived',len(archived),'older revisions; total candidates retained',report['total_candidates'])


if __name__=='__main__':main()
