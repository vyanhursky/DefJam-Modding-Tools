"""Copy source-only recipes to authoring repo and make a new additive private art archive."""
from pathlib import Path
import json,shutil,hashlib
repo=Path.cwd();tools=Path('/Users/vlad/Code/DefJam-Modding-Tools');r=repo/'logs/ui-restoration-20261017/pilot-v1';p=r/'controls-v1-20261020';b=tools/'research/menu-ui-controls-20261020';b.mkdir(exist_ok=True);sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
files=[repo/'logs/ui-restoration-20261020'/n for n in ['prepare-controls.py','prepare-controls-initial.py','complete-gym-companions.py','next-survey.py','approve-popup.py','add-controls-review.py','minimize-catalogue-diff.py']]+[p/'assemble.py',repo/'logs/ui-restoration-20261017/uv-audit/audit-next-menu-batch-20261020.py',repo/'docs/research/menu-controls-restoration-2026-10-20.md',repo/'docs/research/menu-ui-next-batch-mapping-2026-10-20.md']
for f in files:shutil.copy2(f,b/f.name)
gen=json.loads((p/'generations.json').read_text());lines=['# Exact built-in imagegen prompts — 2026-10-20','2new calls /144historical. Final alpha/palette/geometry are technically restored; raw proposals are not finals.']
for x in gen['items']:
 raw=p/(x['key']+'-raw.png');ref=p/x['reference'];lines+=['',x['key'],'transparent_background: true','reference: '+ref.name,'reference_sha256: '+sha(ref),'raw: '+raw.name,'raw_sha256: '+sha(raw),x['prompt']];x['raw_sha256']=sha(raw);x['reference_sha256']=sha(ref)
(p/'generations.json').write_text(json.dumps(gen,indent=2)+'\n');(b/'prompts.txt').write_text('\n'.join(lines)+'\n');(b/'README.md').write_text('''# Gym/controls and linked review source

Artwork/raws/review records remain PRIVATE. `assemble.py` reconstructs native
4x tiles and15studies from private sources/groups/generations. Final preparer
includes all22sources; initial survey and companion completion are historical.
`add-controls-review.py` records the initial insertion; current serving page
is archived privately after companion/approval/navigation updates. Do not rerun
it on the current page (it inserts a new section). Private final sources/groups
and review-items are authoritative inputs, never tracked. Exact prompts/args
and input/raw hashes are in prompts.txt. Source mapping script is a re-run
transcription; report describes provenance and limitations.

Reusable review navigation is packaged in src/defjam_tools/resources/
review_navigation.mjs and review_navigation.css. Link CSS and a type=module
script at the end of the existing review page; group by comparison ID or row.
No CDN, runtime install or workshop review-data mutation. Node tests:
`node --test tests/review-navigation.test.mjs`.

Owner approved previous popup/profile15studies/22IDs; current Gym15/22 and
prior16/19 remain pending. Private additive archive is
<data>/scratch/menu-ui-controls-v1-popup-approved-20261020/; prior popup pending
archive is the base. Restore source publication after GitHub sign-in is fixed.
''');(b/'SOURCE_SHA256SUMS').write_text(''.join(sha(f)+'  '+f.name+'\n' for f in sorted(b.iterdir()) if f.is_file() and f.name!='SOURCE_SHA256SUMS'))
status='''- 2026-10-20 D172/UI–D174/UI — Popup/profile15studies/22sources APPROVED.
  Frozen130newpins/473total,114reviewedIDs(96unconditional+18conditional).
  Separate22tile4xexport exact/uninstalled. Prior16/19remains pending.
  New15Gym/controlstudies/22sources pending:2restrainedpapers+13Faithful;
  complete Gymshapes50/60/64 with3narrowcompanions.2calls/144historical.
  Originalalpha/marks/UVguards/padding exact,maxRGBdelta4;473pins/2439oldPNGs
  unchanged;75isolatedaspectpairs. Review51738 nowlinkedmousewheel/drag/fit
  on105images46groups, including legacy/wipe/tallpan.60refcases/75aspects
  loaded,zerooverflow/errors,4Node+22gamefocusedtests pass. Game untouched.
  Source resources under src/defjam_tools/resources/review_navigation.*;
  recipe/prompt bundle research/menu-ui-controls-20261020/. Private additive
  archive <data>/scratch/menu-ui-controls-v1-popup-approved-20261020/.
  Native placement/clip/pan/platform validation remains pending; preserve8768,
  17workshop/Trejo and existingpacks. GitHubauthstillinvalid; commitlocal and
  publish existing branches after sign-in, then update PR62description.

'''
f=tools/'PROGRESS.md';s=f.read_text();idx=s.index('- 2026-10-20 D170/UI');s=s[:idx]+status+s[idx:];f.write_text(s);f=tools/'docs/menu-art-workflow.md';s=f.read_text();s+='\n\n## 2026-10-20: linked menu review and Gym batch\n\n'+status+'\nScroll over either image to zoom about the cursor; drag to pan both. Fit, double-click or Home resets. View/background changes retain framing; source changes reset. Before/after/wipe and bounds move together. Keep `review_navigation.mjs`/CSS in the private serving root synchronized with packaged source. Run four Node tests and verify actual mouse interaction after page changes.\n';f.write_text(s);f=tools/'.local-handoff.md';old=f.read_text() if f.exists() else '';f.write_text(status+old)
archive=Path('/Users/vlad/Code/defjam-data/scratch/menu-ui-controls-v1-popup-approved-20261020');archive.mkdir(exist_ok=False);target=archive/'session/pilot-v1';target.mkdir(parents=True)
shutil.copytree(p,target/p.name)
for n in ['review.html','review_navigation.mjs','review_navigation.css','popup-profile-approval-20261020.json']:shutil.copy2(r/n,target/n)
shutil.copytree(repo/'logs/ui-restoration-20261020/approved-pack-exports/menu-ui-popup-profile-test-v1',archive/'exports/menu-ui-popup-profile-test-v1');shutil.copytree(b,archive/'source')
for name in ['config/menu-ui-approved-artwork.json','config/menu-ui-source-shaped-exports.json']:dest=archive/'metadata'/Path(name).name;dest.parent.mkdir(exist_ok=True);shutil.copy2(repo/name,dest)
(archive/'README.md').write_text('''Additive archive,2026-10-20. New Gym/controls15studies22sources pending;
popup/profile approved130newpins/22IDs. Prior16batch remains pending.
Requires immutable base menu-ui-popup-profile-v1-pending-20261020
manifestSHA31967fe6554fd0da57c11f0a93f2c061e9f31cd26431e8fc6305ca5a76263542
and earlier archive chain. This overlay adds the new batch, popup approval,
22tile isolated export, current page/navigation and source. No game change.
''');manifest={str(f.relative_to(archive)):dict(sha256=sha(f),bytes=f.stat().st_size) for f in sorted(archive.rglob('*')) if f.is_file()};(archive/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');receipt=dict(archive=str(archive),files=len(manifest),bytes=sum(v['bytes'] for v in manifest.values()),manifest_sha256=sha(archive/'manifest.json'));(p/'archive-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
