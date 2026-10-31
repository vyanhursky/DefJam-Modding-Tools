"""Private immutable snapshot and source-only authoring handoff update."""
from pathlib import Path
import hashlib,json,shutil
repo=Path('/Users/vlad/.codex/worktrees/01c5/DefJamFFNY-recomp');r=repo/'logs/ui-restoration-20261017/pilot-v1';p=r/'hiscores-v1';t=Path('/Users/vlad/Code/DefJam-Modding-Tools');dest=Path('/Users/vlad/Code/defjam-data/scratch/menu-ui-hiscores-v1-rewards-approved-20261019');assert not dest.exists()
state='''- 2026-10-19 D152-D153: sharedRewardswall APPROVED27pins(+52Battle).
  Independent HighScoresDRAFT firstpanel51738:640×480,512+128tiles,opaque,
  root0,0;fullboard native48,86..588,440 protected. Sourcealpha/padding/seam
  exact.3built-in calls/95total;restorationtinywallLdetail only +2native-edge
  brick sides,sourcepalette/native-density. Fullcenter exact inall5ratios.
  1126priorPNGs/79approvalpins/wholeboard/5centers exact. Browser5ratios×6+
  2refs×2imagesload,wipe50%/center1920/aspectlock/bounds75%/draft+side/nooverflow/
  zeroerrors. Exactjobs/raws/recipes coordinating pilot-v1/hiscores-v1/;report
  menu-hiscores-background-results-2026-10-19.md.21source references inspected
  forremainingqueue:result/rematchpapers,Extrasnotes,Storyphone;not21backgrounds.
  Softlightmaps leftunchanged. Newprivate menu-ui-hiscores-v1-rewards-approved-
  20261019 overlay;earlierarchivesimmutable. NextownerHighScoresreview;nativegame
  checks later. No8768/17candidate/Trejowrites/import/install/game/build/runtime/
  core/commit/push.
'''
f=t/'PROGRESS.md';f.write_text(f.read_text().replace('## Current status\n','## Current status\n\n'+state,1));f=t/'.local-handoff.md';f.write_text('# Rewards approved / High Scores draft — 2026-10-19 D152-D153\n\n'+state+'\nReview http://127.0.0.1:51738/review.html. Prior blocks below are historical.\n\n'+f.read_text());f=t/'docs/menu-art-workflow.md';f.write_text(f.read_text()+(p/'workflow.md').read_text())
dest.mkdir(parents=True);shutil.copytree(p,dest/'pilot-v1/hiscores-v1');shutil.copytree(r/'rewards-approved-v1',dest/'pilot-v1/rewards-approved-v1');shutil.copytree(r/'remaining-menus-v1',dest/'pilot-v1/remaining-menus-v1');shutil.copy2(r/'review.html',dest/'pilot-v1/review.html')
for manifest in ['rewards-approval-20261019.json','battle-setup-approval-20261019.json','battle-fighter-approval-20261019.json']:shutil.copy2(r/manifest,dest/'pilot-v1'/manifest)
for row in json.loads((r/'rewards-approval-20261019.json').read_text())['files']:
 out=dest/'pilot-v1'/row['path'];out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(r/row['path'],out)
for rel in ['next-scope/audit-hiscores-backgrounds.py','next-scope/hiscores-background-metadata.json','uv-audit/audit_pilot_uv.py']:
 out=dest/'ui-restoration-20261017'/rel;out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(r.parent/rel,out)
for rel in ['PROGRESS.md','docs/research/menu-hiscores-background-results-2026-10-19.md']:
 out=dest/'recomp-records'/rel;out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(repo/rel,out)
for rel in ['PROGRESS.md','.local-handoff.md','docs/menu-art-workflow.md']:
 out=dest/'authoring-records'/rel;out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(t/rel,out)
h=dest/'toolchain/defjam_tools';h.mkdir(parents=True);(h/'__init__.py').write_text('')
for name in ['color_trial.py','paths.py']:shutil.copy2(t/'src/defjam_tools'/name,h/name)
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();files=[dict(path=str(f.relative_to(dest)),sha256=sha(f),bytes=f.stat().st_size) for f in sorted(dest.rglob('*')) if f.is_file()];m=dest/'manifest.json';m.write_text(json.dumps(dict(recipe='Apply to COPY of previous pilot. Earlier archives immutable; Battle images remain in prior overlay,exact pins retained here.',files=files),indent=2)+'\n');assert all(sha(dest/f['path'])==f['sha256'] for f in files);receipt=dict(path=str(dest),files=len(files),bytes=sum(f['bytes'] for f in files),manifest_sha256=sha(m));(p/'archive-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
