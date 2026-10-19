"""Preserve approved art separately from new drafts; source-only workflow docs."""
from pathlib import Path
import hashlib,json,shutil

root=Path(__file__).resolve().parent
pilot=root.parent
repo=Path('/Users/vlad/Code/DefJam-Modding-Tools')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
approval=json.loads((pilot/'skyline-approval.json').read_text())
assert sha(pilot/'seam-v3/title-skyline-wide-master-v3.png')==approval['master']['sha256']
p=repo/'docs/menu-art-workflow.md'
assert not p.exists(),'Versioned guide already exists; review before replacement'
shutil.copy2(root/'menu-art-workflow.md',p)
guide_note='''
For the second batch, a rigid roof silhouette required technical alpha/geometry
registration to the source edge's measured slope; color blending alone left a
step. Keep AI texture proposals but verify straight architectural planes and
their source coordinates. Generated-side alpha remains subject to art review.
One square bridge output changed resolution1254→1024 while retaining the50%
join and24%poster-top landmark. Uniform full-canvas resolution normalization is
allowed only when aspect and landmark registration agree, with actual sizes and
transforms recorded. Reject crop, zoom, perspective or registration drift; never
silently stretch a repair in one axis. Restore protected pixels afterward.
'''
for relative in ['docs/menu-art-workflow.md','docs/widescreen-backgrounds.md']:
    p=repo/relative
    s=p.read_text()
    if guide_note.strip() not in s:p.write_text(s+guide_note)
    if relative.endswith('menu-art-workflow.md'):
        shutil.copy2(p,root/'menu-art-workflow.md')
p=repo/'prompts/menu-widescreen-extension.txt'
s=p.read_text()
s=s.replace('Reject unrequested registration/dimension changes; never silently resize a repair crop.',
    'Reject crop/aspect or landmark registration drift. A full-canvas resolution change may be normalized uniformly only when aspect and fixed landmarks agree; record raw/target dimensions and the transform. Never silently resize or stretch a repair crop.')
p.write_text(s)
for relative,text in [('docs/README.md','\n- [Menu art production and approved skyline recipe](menu-art-workflow.md)\n'),
                      ('prompts/README.md','\nThe [approved skyline recipe and production gates](../docs/menu-art-workflow.md) retain the exact accepted workflow, failure cases and approval scope.\n')]:
    p=repo/relative;s=p.read_text()
    if text.strip() not in s:p.write_text(s+text)
status='''- 2026-10-17: Vlad APPROVED isolated skyline v3 and requested remaining
  backgrounds. Exact master SHA256683e5481d3bef12a27be00a1eda0afbbcfcefdbc3583be862f00ee21b809f2f0
  and all5crops pinned in private skyline-approval.json. Full standalone approved
  archive <data>/scratch/menu-ui-approved-skyline-v3-20261017/; exact prompts,
  originals/raws, masks, processors, receipts and hashes retained. New source-only
  docs/menu-art-workflow.md is the entry point; prompt and seam guides linked.
  New batch:5restrained derivatives(city,tower,lit wall,shutter,surround),9new
  built-in calls(18pilot total), shared dark/lit detail, exact source alpha/graphics/
  padding/seams and medianLab0. New title+mode studies:5groups×5aspects verified,
  both mode envelopes share structure; original offstage right wall reused.
  Roof contour registration and duplicate-poster repair documented. New art is
  UNAPPROVED. Review51738 shows it above the approved reference. No new imports;
  17workshop candidates/session unchanged. No game/run/install/core changes.
  New private archive <data>/scratch/menu-ui-second-batch-20261017/. Next: owner
  art/alpha/lighting review before source-shaped imports and runtime integration.

'''
p=repo/'PROGRESS.md';s=p.read_text()
if status not in s:s=s.replace('## Current status\n\n','## Current status\n\n'+status,1)
s=s.replace('Blaze, Nyne, Trejo are the pilot; 13 retained drafts (11 imagegen, two deterministic',
    'The fighter pilot (Blaze, Nyne, Trejo) retains13drafts plus4menu trials,17workshop candidates total. The13fighter drafts comprise11imagegen and two deterministic')
# Keep original paragraph grammar if the historical phrase was replaced.
s=s.replace('color trials), 13 imagegen request records, zero queued.',
    'color trials;13imagegen request records, zero queued. Wide-art drafts are separate private experiments.')
p.write_text(s)
local='''## Approved skyline and next batch2026-10-17

Owner approved exact isolated skyline seam-v3 master (SHA683e5481d3bef12a27be00a1eda0afbbcfcefdbc3583be862f00ee21b809f2f0) and five aspect crops. This does not approve separate restoration tile trials or new layers.
Approved standalone archive /Users/vlad/Code/defjam-data/scratch/menu-ui-approved-skyline-v3-20261017/ (complete chain+manifest+approval).
New unapproved batch /Users/vlad/Code/defjam-data/scratch/menu-ui-second-batch-20261017/ (self-contained pilot tree+manifest).
Review http://127.0.0.1:51738/review.html shows five study groups×five aspects, all loaded; five new restrained comparisons, raw history, original-area overlay and approved reference.
Nine new built-in calls,18pilot total;5new derivatives, no workshop import.17candidate records/session untouched. Read docs/menu-art-workflow.md and coordinating recomp report docs/research/menu-ui-second-batch-results-2026-10-17.md.
Title active bounds310/446 and offsets102/16; opaque bottom padding must be clipped. Mode shutter230×354; surround512.5×480 at source448.5 overlap and stage316.2, reaches828.63—reuse offstage art. Lit/dark share detail, retain original light fields.
Roof alpha registration and mode duplicate repair are retained private processors, not adopted core or game-verified results. Next review new art/side alpha/lighting before source-mapped imports/runtime work. Original skyline immutable; writer8768 intact. No game/install/selection/source-core change/commit/push.

'''
p=repo/'.local-handoff.md';s=p.read_text()
if local not in s:p.write_text(local+s)

approved=Path('/Users/vlad/Code/defjam-data/scratch/menu-ui-approved-skyline-v3-20261017')
new=Path('/Users/vlad/Code/defjam-data/scratch/menu-ui-second-batch-20261017')
approved.mkdir(exist_ok=False)
shutil.copytree(pilot,approved/'experiment',ignore=shutil.ignore_patterns('batch2','__pycache__'))
shutil.copy2(root/'menu-art-workflow.md',approved/'README.md')
# A dedicated approved-only review avoids references to the new, unapproved batch.
links=' '.join('<p><a href="experiment/seam-v3/'+r['path']+'">'+k+'</a></p>' for k,r in json.loads((pilot/'seam-v3/receipt.json').read_text())['outputs'].items())
(approved/'review.html').write_text('<!doctype html><meta charset="utf-8"><title>Approved skyline v3</title><style>body{background:#111;color:#eee;font:16px system-ui}img{width:100%}a{color:#d8e592}</style><h1>Owner-approved isolated skyline v3</h1><p>Artwork approval2026-10-17; game validation remains separate.</p><img src="experiment/seam-v3/title-skyline-32x9-v3.png">'+links+'<p><a href="experiment/skyline-approval.json">Approval, hashes and provenance index</a></p><p><a href="README.md">Complete recipe</a></p>')
new.mkdir(exist_ok=False)
shutil.copytree(pilot,new/'pilot-v1',ignore=shutil.ignore_patterns('__pycache__'))
shutil.copy2(root/'menu-art-workflow.md',new/'README.md')
reports=['menu-ui-second-batch-results-2026-10-17.md','menu-title-remaining-layers-2026-10-17.md','menu-mode-remaining-layers-2026-10-17.md','menu-pilot-uv-layout-2026-10-17.md','menu-ui-seam-audit-2026-10-17.md']
source_repo=Path('/Users/vlad/.codex/worktrees/01c5/DefJamFFNY-recomp')
for dst in [approved,new]:
    (dst/'documentation').mkdir()
    for report in reports:shutil.copy2(source_repo/'docs/research'/report,dst/'documentation'/report)
    manifest={str(p.relative_to(dst)):sha(p) for p in sorted(dst.rglob('*')) if p.is_file()}
    # Verify every copied artwork/provenance file against the local source tree.
    folder='experiment' if dst==approved else 'pilot-v1'
    for p in (dst/folder).rglob('*'):
        if p.is_file():assert sha(p)==sha(pilot/p.relative_to(dst/folder))
    (dst/'manifest.json').write_text(json.dumps(dict(schema=1,files=manifest,
        approved_art_master_sha256=approval['master']['sha256'],role='approved skyline only' if dst==approved else 'new batch unapproved'),indent=2))
    print(json.dumps({'archive':str(dst),'files':len(manifest),'copies_verified':True}))
