"""Sync authorized source-only authoring handoffs and create a new immutable private overlay."""
from pathlib import Path
import json,hashlib,shutil
repo=Path('/Users/vlad/.codex/worktrees/01c5/DefJamFFNY-recomp');r=repo/'logs/ui-restoration-20261017/pilot-v1';p=r/'results-v1';t=Path('/Users/vlad/Code/DefJam-Modding-Tools');dest=Path('/Users/vlad/Code/defjam-data/scratch/menu-ui-results-v1-hiscores-approved-20261019');assert not dest.exists()
state='''- 2026-10-19 D154-D155: High Scores v1 APPROVED13pins;92Battle/Rewards/
  HighScorespins exact. Newfirstsection51738 Results&Rematch:6DRAFTsource-shaped
  panels/rematch/matchSm1..4/rewardun,18tiles.6built-in calls/101total;sourcealpha,
  printedink/rules/UVpadding/4nativepxedgeguards exact;onlytinyfinepaperLdetail
  adopted,sourcechroma/broadfolds retained. Sm4bottomrighty255overlap retained.
  30aspectpairs keeporiginalpanel scale/placement/centered640×480viewport;wide
  margins transparent,nooutpaint/stretch. Sm2 .05px/rewardx110.5previewrounding
  noted,exactAPTmatrices retained.1161priorPNGs/92pins/18tileguards/6alphas/
  protectedgraphics/30centers exact. Browser30stagecases×2+24refs/channels×5
  imagesload,3BGs/wipe50%/draft+side/bounds75%/nooverflow/zeroerrors.
  Exactprompts/raws/recipes coordinating pilot-v1/results-v1/;source report
  menu-result-rematch-panels-2026-10-19.md. Newprivate overlay
  menu-ui-results-v1-hiscores-approved-20261019;applytoCOPYofpriorpilot,
  earlierarchivesimmutable. Nextownerpaperfeedback,thenExtrasnotes/Storyphone/
  frames aftermapping;softlightmaps retained. Nativegame/Optionsscroll/Mode
  conditionalrightlighting pending. No8768/17candidate/Trejo writes/import/
  install/game/build/runtime/coreedit/commit/push. Historicalblocks below.
'''
f=t/'PROGRESS.md';f.write_text(f.read_text().replace('## Current status\n','## Current status\n\n'+state,1));f=t/'.local-handoff.md';f.write_text('# High Scores approved / six paper drafts — 2026-10-19 D154-D155\n\n'+state+'\nReview http://127.0.0.1:51738/review.html. Previousblocks historical.\n\n'+f.read_text());f=t/'docs/menu-art-workflow.md';f.write_text(f.read_text()+(p/'workflow.md').read_text())
dest.mkdir(parents=True);shutil.copytree(p,dest/'pilot-v1/results-v1');shutil.copytree(r/'hiscores-approved-v1',dest/'pilot-v1/hiscores-approved-v1');shutil.copy2(r/'review.html',dest/'pilot-v1/review.html')
for name in ['battle-fighter-approval-20261019.json','battle-setup-approval-20261019.json','rewards-approval-20261019.json','hiscores-approval-20261019.json']:shutil.copy2(r/name,dest/'pilot-v1'/name)
for row in json.loads((r/'hiscores-approval-20261019.json').read_text())['files']:
 out=dest/'pilot-v1'/row['path'];out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(r/row['path'],out)
for rel in ['next-scope/audit-result-panels.py','next-scope/result-panels-metadata.json','uv-audit/audit_pilot_uv.py']:
 out=dest/'ui-restoration-20261017'/rel;out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(r.parent/rel,out)
for rel in ['PROGRESS.md','docs/research/menu-result-rematch-panels-2026-10-19.md']:
 out=dest/'recomp-records'/rel;out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(repo/rel,out)
for rel in ['PROGRESS.md','.local-handoff.md','docs/menu-art-workflow.md']:
 out=dest/'authoring-records'/rel;out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(t/rel,out)
h=dest/'toolchain/defjam_tools';h.mkdir(parents=True);(h/'__init__.py').write_text('')
for name in ['color_trial.py','paths.py']:shutil.copy2(t/'src/defjam_tools'/name,h/name)
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();files=[dict(path=str(f.relative_to(dest)),sha256=sha(f),bytes=f.stat().st_size) for f in sorted(dest.rglob('*')) if f.is_file()];m=dest/'manifest.json';m.write_text(json.dumps(dict(recipe='Apply toCOPYofpriorpilot. Earlierarchivesimmutable. PriorBattle/Rewardsimages retainedinearlieroverlays;exactapprovalpins retainedhere.',files=files),indent=2)+'\n');assert all(sha(dest/f['path'])==f['sha256'] for f in files);receipt=dict(path=str(dest),files=len(files),bytes=sum(f['bytes'] for f in files),manifest_sha256=sha(m));(p/'archive-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
