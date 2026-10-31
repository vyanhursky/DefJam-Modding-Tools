"""Immutable private overlay; keep the live authoring writer/candidates untouched."""
from pathlib import Path
import hashlib,json,shutil
repo=Path('/Users/vlad/.codex/worktrees/01c5/DefJamFFNY-recomp');r=repo/'logs/ui-restoration-20261017/pilot-v1';p=r/'rewards-v1';t=Path('/Users/vlad/Code/DefJam-Modding-Tools');dest=Path('/Users/vlad/Code/defjam-data/scratch/menu-ui-rewards-v1-battle-approved-20261019');assert not dest.exists()
state='''- 2026-10-19 D150-D151: setupv5 APPROVED13pins,+39fighterpins frozen.
  All4Battle backgrounds approved;gameintegration separate. Next Rewards/Unlock
  sharedwall DRAFT on51738firstpanel:2IDs/3labels/2layouts/15aspectpairs.
  Native699×480,512+188parts/1pxoverlap511;stagecrop29 vs50.4. Originalalpha
  52..255 andbakededgefade retained in4:3/source-shapedexports;widecoverage
  replacesoldperipheralfade andmoves96pxvignette toviewouteredge. Onlytrusted
  native40..659interior isRGBexact;fullwide4:3RGBAcenter equality NOTclaimed.
  Sixbuilt-in calls/92total,full-referenceleftrepeat rejected;native-onlysides,
  sourcepalette/materialprofiles and2fullheight256pxsidebridges adopted.
  1051priorPNGs/52Battlepins/sourcealpha/padding exact. Browser15cases×6+2alpha
  loads,wipe50%/center1920/aspectlock/bounds75%/draft+side/nooverflow/zeroerrors.
  Exactprompts/raws/rejections/recipes coordinating pilot-v1/rewards-v1/;report
  menu-rewards-unlock-backgrounds-2026-10-19.md. Newprivate overlay
  menu-ui-rewards-v1-battle-approved-20261019;earlierarchivesimmutable.
  Nextownervisualreview;nativegamevalidationlater. No8768/17candidate/Trejo
  writes/import/install/game/build/runtime/core/commit/push.
'''
f=t/'PROGRESS.md';f.write_text(f.read_text().replace('## Current status\n','## Current status\n\n'+state,1));f=t/'.local-handoff.md';f.write_text('# Battle approved / Rewards shared-wall draft — 2026-10-19 D150-D151\n\n'+state+'\nReview http://127.0.0.1:51738/review.html. Earlier blocks below are historical.\n\n'+f.read_text());f=t/'docs/menu-art-workflow.md';f.write_text(f.read_text()+(p/'workflow.md').read_text())
dest.mkdir(parents=True);shutil.copytree(p,dest/'pilot-v1/rewards-v1');shutil.copytree(r/'battle-approved-v5',dest/'pilot-v1/battle-approved-v5');shutil.copy2(r/'review.html',dest/'pilot-v1/review.html')
for manifest in ['battle-setup-approval-20261019.json','battle-fighter-approval-20261019.json']:
 shutil.copy2(r/manifest,dest/'pilot-v1'/manifest)
 for row in json.loads((r/manifest).read_text())['files']:
  out=dest/'pilot-v1'/row['path'];out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(r/row['path'],out)
for rel in ['next-scope/audit-rewards-backgrounds.py','next-scope/rewards-background-metadata.json','uv-audit/audit_pilot_uv.py']:
 out=dest/'ui-restoration-20261017'/rel;out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(r.parent/rel,out)
for rel in ['PROGRESS.md','docs/research/menu-rewards-unlock-backgrounds-2026-10-19.md']:
 out=dest/'recomp-records'/rel;out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(repo/rel,out)
for rel in ['PROGRESS.md','.local-handoff.md','docs/menu-art-workflow.md']:
 out=dest/'authoring-records'/rel;out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(t/rel,out)
helpers=dest/'toolchain/defjam_tools';helpers.mkdir(parents=True);(helpers/'__init__.py').write_text('')
for name in ['color_trial.py','paths.py']:shutil.copy2(t/'src/defjam_tools'/name,helpers/name)
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();files=[dict(path=str(f.relative_to(dest)),sha256=sha(f),bytes=f.stat().st_size) for f in sorted(dest.rglob('*')) if f.is_file()];m=dest/'manifest.json';m.write_text(json.dumps(dict(recipe='Apply overlay to COPY of previous pilot; historical archives unchanged. Use retained inputs/auditmetadata/source checkout for reproduction.',files=files),indent=2)+'\n');assert all(sha(dest/f['path'])==f['sha256'] for f in files);receipt=dict(path=str(dest),files=len(files),bytes=sum(f['bytes'] for f in files),manifest_sha256=sha(m));(p/'archive-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
