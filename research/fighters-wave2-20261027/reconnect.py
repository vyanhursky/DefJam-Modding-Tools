#!/usr/bin/env python3
"""Explicit backed-up corpus rebind and additive import for this review batch.

Requires confirmed saved browser notes, an offline live workspace and unchanged
preparation snapshot. Never resets reviews or installs a mod. A migration receipt
versions the binding change; original JSON and local profile are backed up first.
"""
import argparse,copy,hashlib,json,shutil,socket
from pathlib import Path
from defjam_tools.texture_workshop import Workshop,WorkspaceLock,atomic_json


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for name in ['root','workspace','corpus','profile','code-profile']:ap.add_argument('--'+name,type=Path,required=True)
    ap.add_argument('--saved-notes-confirmed',action='store_true',required=True)
    args=ap.parse_args();root=args.root;live=args.workspace.resolve();stage=root/'staging-workshop'
    assert stage.resolve()!=live
    assert json.loads((root/'assembly.json').read_text())['old_candidates_and_reviews_exact']
    probe=socket.socket();probe.settimeout(.3)
    try:
        if probe.connect_ex(('127.0.0.1',8768))==0:raise ValueError('Port 8768 already has an owner')
    finally:probe.close()
    dest=live/'backups/fighters-wave2-rebind-20261027';dest.mkdir(exist_ok=False)
    with WorkspaceLock(live):
        if (live/'workshop.json').read_bytes()!=(root/'before/workshop.json').read_bytes():
            raise ValueError('Live reviews changed; merge and revalidate before reconnecting')
        if (live/'model-viewer.json').read_bytes()!=(root/'before/model-viewer.json').read_bytes():
            raise ValueError('Live camera state changed; preserve it before reconnecting')
        old=json.loads((live/'workshop.json').read_text());new=json.loads((stage/'workshop.json').read_text())
        for key,value in old['reviews'].items():assert new['reviews'][key]==value
        for aid,items in old['candidates'].items():
            for item in items:
                assert item in new['candidates'][aid]
                assert sha(live/item['path'])==sha(stage/item['path'])==item['sha256']
        for job in old['requests']:assert job in new['requests']
        oldids={j['id'] for j in old['requests']}
        for job in new['requests']:
            if job['id'] not in oldids and job.get('parent_image'):
                path=Path(job['parent_image']);relative=path.relative_to(stage.resolve())
                job['parent_image']=str(live/relative)
        plans=[]
        for folder in ['candidates','raw','models']:
            for file in (stage/folder).rglob('*'):
                if not file.is_file():continue
                target=live/file.relative_to(stage)
                if target.exists():
                    if sha(file)!=sha(target):raise ValueError('Refuse overwriting existing artifact: '+str(target))
                else:plans.append((file,target))
        # Backup exact metadata before publishing any new binding.
        for name in ['workshop.json','model-viewer.json']:shutil.copyfile(live/name,dest/name)
        shutil.copyfile(args.profile,dest/'local.json')
        for file,target in plans:
            target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(file,target)
        experiment=live/'experiments/fighters-wave2-20261027';experiment.mkdir(exist_ok=False)
        for file in root.iterdir():
            if file.name=='staging-workshop':continue
            if file.is_dir():shutil.copytree(file,experiment/file.name)
            else:shutil.copyfile(file,experiment/file.name)
        import defjam_tools.face_detail as face,defjam_tools.color_trial as color
        shutil.copyfile(face.__file__,experiment/'face_detail_processor.py')
        shutil.copyfile(color.__file__,experiment/'color_trial_processor.py')
        atomic_json(live/'workshop.json',new)
        profile=json.loads(args.profile.read_text());profile['corpus']=str(args.corpus.resolve())
        profile['workspace']=str(live);profile['port']=8768
        atomic_json(args.profile,profile);atomic_json(args.code_profile,profile)
        store=Workshop(args.corpus,live)
        assert store.data==new
        assert all(store.data['reviews'][k]==v for k,v in old['reviews'].items())
        assert (live/'model-viewer.json').read_bytes()==(dest/'model-viewer.json').read_bytes()
        receipt=dict(schema=1,migration='validated-corpus-rebind-additive-import-v1',
                     old_corpus_id=old['corpus_id'],new_corpus_id=new['corpus_id'],
                     workspace_path_preserved=str(live),backup=str(dest),browser_notes_saved_confirmed=True,
                     original_candidate_count=sum(map(len,old['candidates'].values())),
                     new_candidate_count=sum(map(len,new['candidates'].values())),
                     old_reviews_requests_candidates_and_camera_preserved=True,
                     before_workshop_sha256=sha(dest/'workshop.json'),after_workshop_sha256=sha(live/'workshop.json'),
                     copied_files=len(plans),active_game_modified=False)
        atomic_json(dest/'migration.json',receipt);atomic_json(root/'live-migration.json',receipt)
        print(json.dumps(receipt,indent=2))


if __name__=='__main__':main()
