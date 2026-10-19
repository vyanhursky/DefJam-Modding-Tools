"""Record approved menu papers/counts in both projects; never overwrite an earlier archive."""
from pathlib import Path
import shutil,json,hashlib
repo=Path('/Users/vlad/.codex/worktrees/01c5/DefJamFFNY-recomp');r=repo/'logs/ui-restoration-20261017/pilot-v1';p=r/'results-approved-v1';t=Path('/Users/vlad/Code/DefJam-Modding-Tools');dest=Path('/Users/vlad/Code/defjam-data/scratch/menu-ui-results-approved-inventory-20261019');assert not dest.exists()
state='''- 2026-10-19 D156: owner APPROVESall6results/rematch/reward-earned panels;
  results-approval-20261019.json freezes60files/18tiles/6mosaics+alphas/30stage
  studies. NoapprovedPNGchanged;101pilotcalls unchanged,nogeneration. Review
  51738firstsectionapproved;nativegameacceptance separate. Remainingunique
  source-IDcensus:71covered(63approved+8conditionalMode),1,252/1,323registered
  flows notcustomrestored;core1,763/1,834,broad11,190/11,261. Scopesoverlap,
  existingFaithfulHDcoverslibrary;notbackground/jobcounts.23confirmednextart:
  Extras4/phone2/venueframes3/title shield+localizedStart8/supportemblems6;
  additionalframes/popups/Story/header/Extrasfragments stillneedclassification.
  Exactcoverageledger/remainingCSV inpilot-v1/results-approved-v1/;source report
  menu-ui-remaining-inventory-2026-10-19.md. Newimmutable privateoverlay
  menu-ui-results-approved-inventory-20261019,applytoCOPYofearlierpilot.
  NextExtrasnotes thenStoryphone/venue/popup/title/support;noautomaticmassbatch.
  Modeconditionalrightlighting,Optionsscroll andallnativeintegration/testing
  later. No8768/17candidate/Trejo writes/import/install/game/build/runtime/core/
  commit/push. Earlierblocks historical.
'''
f=t/'PROGRESS.md';f.write_text(f.read_text().replace('## Current status\n','## Current status\n\n'+state,1));f=t/'.local-handoff.md';f.write_text('# All six menu papers approved / remaining census — 2026-10-19 D156\n\n'+state+'\nReview http://127.0.0.1:51738/review.html. Previousblocks historical.\n\n'+f.read_text());f=t/'docs/menu-art-workflow.md';f.write_text(f.read_text()+'\n## Six menu papers approved / remaining census — 2026-10-19 D156\n\n'+state)
dest.mkdir(parents=True);shutil.copytree(p,dest/'pilot-v1/results-approved-v1');shutil.copy2(r/'review.html',dest/'pilot-v1/review.html');shutil.copy2(r/'results-approval-20261019.json',dest/'pilot-v1/results-approval-20261019.json');shutil.copy2(r/'results-v1/references.json',dest/'pilot-v1/results-v1/references.json') if (dest/'pilot-v1/results-v1').exists() else None
for row in json.loads((r/'results-approval-20261019.json').read_text())['files']:
 out=dest/'pilot-v1'/row['path'];out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(r/row['path'],out)
shutil.copy2(r/'results-v1/references.json',dest/'pilot-v1/results-v1/references.json')
for rel in ['all-menu-texture-aliases.csv','registered-screens.csv','summary.json']:
 out=dest/'ui-restoration-20261017'/rel;out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(r.parent/rel,out)
for rel in ['PROGRESS.md','docs/research/menu-ui-remaining-inventory-2026-10-19.md']:
 out=dest/'recomp-records'/rel;out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(repo/rel,out)
for rel in ['PROGRESS.md','.local-handoff.md','docs/menu-art-workflow.md']:
 out=dest/'authoring-records'/rel;out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(t/rel,out)
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();files=[dict(path=str(f.relative_to(dest)),sha256=sha(f),bytes=f.stat().st_size) for f in sorted(dest.rglob('*')) if f.is_file()];m=dest/'manifest.json';m.write_text(json.dumps(dict(recipe='Overlay onCOPYofpriorpilot,earlierarchivesunchanged. Approvedartonly;raws/originals/recipes retained in previousresults-v1archive.',files=files),indent=2)+'\n');assert all(sha(dest/a['path'])==a['sha256'] for a in files);v=dict(path=str(dest),files=len(files),bytes=sum(a['bytes'] for a in files),manifest_sha256=sha(m));(p/'archive-receipt.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v,indent=2))
