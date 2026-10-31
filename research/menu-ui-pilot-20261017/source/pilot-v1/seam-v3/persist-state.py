from pathlib import Path
import hashlib,json,shutil

root=Path(__file__).resolve().parent
repo=Path('/Users/vlad/Code/DefJam-Modding-Tools')
guidance='''
Full-height coverage: the repair region and review crops must include EVERY
visible cloud band down through the horizon haze, then into stable padding.
Do not stop at an arbitrary upper-sky rectangle. Check upper, middle and lower
join regions separately, and inspect the whole height; a passing upper-sky
edge metric can hide a lower seam. Preserve an owner-accepted opposite join.
'''
p=repo/'prompts/menu-widescreen-extension.txt'
s=p.read_text()
if guidance.strip() not in s:
    p.write_text(s+guidance)
p=repo/'docs/widescreen-backgrounds.md'
s=p.read_text()
paragraph='''
The first right-side repair missed lower cloud bands because both the allowed
region and the review crop ended too high. Expand the region through the whole
visible sky and horizon haze; review upper/middle/lower joins separately and use
a full-height crop. A successful opposite-side repair stays exact. Do not infer
whole-join acceptance from an upper-sky metric or cropped before/after alone.
'''
if paragraph.strip() not in s:
    p.write_text(s+paragraph)
status='''- 2026-10-17: owner accepts left cloud join; right needed full-height repair.
  Prior right rectangle stopped at y704 and missed lower clouds/horizon haze.
  One additional built-in edit (nine pilot calls) and same boundary method now
  cover [3520,380,512,580]. Accepted left, original center and outside right
  domain exact;5/5aspect centers pass. Review51738 defaults full-height v3 and
  keeps v2/initial. Full-height close-ups and all aspect PNGs checked. Guidance
  now requires upper/middle/lower coverage. No new import;17candidates unchanged.
  Private archive <data>/scratch/menu-ui-pilot-20261017-seam-v3/. No whole-art
  approval, selection, install, game run, core changes or writer restart.

'''
p=repo/'PROGRESS.md'
s=p.read_text()
if status not in s:
    p.write_text(s.replace('## Current status\n\n','## Current status\n\n'+status,1))
p=repo/'.local-handoff.md'
s=p.read_text()
note='''## Full-height right repair2026-10-17

Owner accepts left join; right v2 missed lower sky below master y704. Read-only
review51738 defaults v3, with prior/initial versions. Accepted left+center exact;
right domain [3520,380,512,580],5/5aspect centers pass. Nine built-in pilot calls.
Latest ignored evidence in coordinating checkout logs/ui-restoration-20261017/pilot-v1/seam-v3/.
New archive /Users/vlad/Code/defjam-data/scratch/menu-ui-pilot-20261017-seam-v3/
is another overlay after v1 and seam-v2. Old archives untouched. Full-height
close-ups reveal lower horizon; prompt/workflow require full-height checks.
17workshop candidates; no import, approval, selection, install or8768restart.

'''
if note not in s:
    p.write_text(note+s)
archive=Path('/Users/vlad/Code/defjam-data/scratch/menu-ui-pilot-20261017-seam-v3')
archive.mkdir(exist_ok=False)
shutil.copytree(root,archive/'seam-v3')
shutil.copy2(root.parent/'review.html',archive/'review.html')
files={}
for p in sorted(archive.rglob('*')):
    if p.is_file():
        relative=p.relative_to(archive)
        source=root.parent/'review.html' if str(relative)=='review.html' else root/relative.relative_to('seam-v3')
        digest=hashlib.sha256(p.read_bytes()).hexdigest()
        assert digest==hashlib.sha256(source.read_bytes()).hexdigest()
        files[str(relative)]=digest
(archive/'manifest.json').write_text(json.dumps(dict(schema=1,overlay_after=['v1','seam-v2'],files=files),indent=2))
print(json.dumps({'archive':str(archive),'files_verified':len(files)}))
