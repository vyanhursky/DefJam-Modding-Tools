"""Save a new immutable private overlay and synchronize source-only authoring notes."""
from pathlib import Path
import hashlib,json,shutil
repo=Path('/Users/vlad/.codex/worktrees/01c5/DefJamFFNY-recomp');r=repo/'logs/ui-restoration-20261017/pilot-v1';p=r/'battle-left-light-v5';tools=Path('/Users/vlad/Code/DefJam-Modding-Tools');dest=Path('/Users/vlad/Code/defjam-data/scratch/menu-ui-battle-left-light-v5-20261019');assert not dest.exists()
state='''- 2026-10-19 D149: owner corrects requested lighting side to LEFT;rightfine.
  Currentv5 on51738 uses v3base,restoring ENTIREpre-v4right exactly. V4labelled
  revertedhistory,v3/v2/v1 retained. Improvedbrickdetail unchanged;scalar light
  correction only x640..1600,y0..720. One built-in guide/86total;Gaussian32guide,
  native64pxbandprofiles Gaussian16,320pxdecay,onset640..800,fade480..720.
  1035priorPNGs/39approvedfighterpins/5centers/nativecenter/entirepre-v4right/
  outside domain exact. Browser5ratios×6images+4history+3fighterpaths+2proofs
  load,wipe50%/center1920/aspectlock/nooverflow/zeroerrors. Exactprompt/raw/recipe
  coordinating pilot-v1/battle-left-light-v5/;report menu-battle-left-lighting-v5-
  2026-10-19.md. Newprivate menu-ui-battle-left-light-v5-20261019 overlay,earlier
  archivesimmutable. Nextowner visualreview/nativegamecheckslater. No8768/
  17candidate/Trejo changes/import/install/game/build/runtime/core/commit/push.
'''
f=tools/'PROGRESS.md';f.write_text(f.read_text().replace('## Current status\n','## Current status\n\n'+state,1))
f=tools/'.local-handoff.md';f.write_text('# Battle upper-left lighting v5 — 2026-10-19 D149\n\n'+state+'\nReview http://127.0.0.1:51738/review.html. Prior blocks below are historical.\n\n'+f.read_text())
f=tools/'docs/menu-art-workflow.md';f.write_text(f.read_text()+(p/'workflow.md').read_text())
dest.mkdir(parents=True);shutil.copytree(p,dest/'pilot-v1/battle-left-light-v5');shutil.copy2(r/'review.html',dest/'pilot-v1/review.html')
for rel in ['battle-left-v3/cmtype-wide-v3.png','battle-fighter-approval-20261019.json']:
 t=dest/'pilot-v1'/rel;t.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(r/rel,t)
for rel in ['PROGRESS.md','docs/research/menu-battle-left-lighting-v5-2026-10-19.md']:
 t=dest/'recomp-records'/rel;t.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(repo/rel,t)
for rel in ['PROGRESS.md','.local-handoff.md','docs/menu-art-workflow.md']:
 t=dest/'authoring-records'/rel;t.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(tools/rel,t)
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();files=[dict(path=str(f.relative_to(dest)),sha256=sha(f),bytes=f.stat().st_size) for f in sorted(dest.rglob('*')) if f.is_file()];m=dest/'manifest.json';m.write_text(json.dumps(dict(recipe='Apply to COPY of previous pilot; earlier archives unchanged.',files=files),indent=2)+'\n');assert all(sha(dest/f['path'])==f['sha256'] for f in files);receipt=dict(path=str(dest),files=len(files),bytes=sum(f['bytes'] for f in files),manifest_sha256=sha(m));(p/'archive-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
