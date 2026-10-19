"""Publish source-only guidance and preserve private refinement evidence."""
from pathlib import Path
import hashlib
import json
import shutil

root=Path(__file__).resolve().parent
repo=Path('/Users/vlad/Code/DefJam-Modding-Tools')
for name,relative in [('menu-widescreen-extension.txt','prompts/menu-widescreen-extension.txt'),
                      ('widescreen-backgrounds.md','docs/widescreen-backgrounds.md')]:
    dest=repo/relative
    if dest.exists():
        assert dest.read_bytes()==(root/name).read_bytes(), 'Do not overwrite an existing version'
    else:
        shutil.copy2(root/name,dest)
for relative,line in [('prompts/README.md','\nMenu scenery uses [menu-widescreen-extension.txt](menu-widescreen-extension.txt)\nwith [the final-composite and seam-review workflow](../docs/widescreen-backgrounds.md).\nIt is a manual prompt scaffold; the workshop queue does not automatically append it.\n'),
                      ('docs/README.md','\n- [Widescreen menu scenery and seam review](widescreen-backgrounds.md)\n')]:
    p=repo/relative
    old=p.read_text()
    if line.strip() not in old:
        p.write_text(old+line)
p=repo/'PROGRESS.md'
old=p.read_text()
new='''- 2026-10-17: owner says menu pilot color accuracy is good; requested cloud
  continuity at original4:3 boundaries across future backgrounds. Two focused
  built-in edits use FINAL assembled context, explicit generated-side regions and
  cloud-feature tracing. Private one-sided harmonic boundary matching preserves
  original center and all pixels outside two repair domains; five aspect centers
  exact. Eight built-in pilot calls total; old versions/raw outputs retained.
  Review51738 now defaults to Refined cloud joins, with initial version and
  left/right before/after. No new workshop import;17candidates remain. Color
  feedback is not whole-art approval. Added manual prompt/workflow docs, no core
  or queue-preset change. Private archive <data>/scratch/menu-ui-pilot-20261017-seam-v2/.
  Check structural flow and both repair-band edges before extending remaining
  title layers. No game test, selection, approval, installation or server restart.

'''
if new not in old:
    old=old.replace('## Current status\n\n','## Current status\n\n'+new,1)
    old=old.replace('  new-side seams/brightness and other layers remain unfinished. No approval,',
                    '  initial side seams prompted the focused refinement above; other layers remain unfinished. No approval,')
    p.write_text(old)
p=repo/'.local-handoff.md'
old=p.read_text()
new='''## Cloud-join refinement2026-10-17

Color accepted by owner as a direction; whole art remains unapproved. Read-only
review51738 defaults to Refined cloud joins with all five ratios, initial version
and left/right close-ups. No import or writer/session changes;17candidates remain.
New immutable private archive: /Users/vlad/Code/defjam-data/scratch/menu-ui-pilot-20261017-seam-v2/
Original v1 archive below stays untouched. New archive is an overlay: copy its
seam-v2/ folder and review.html into a COPY of v1 to reopen independently.
Two additional built-in calls (eight pilot calls total), exact prompts/raw outputs,
context/guide coordinates, processor and preservation checks retained. Source-only
manual scaffold prompts/menu-widescreen-extension.txt and docs/widescreen-backgrounds.md
define final-composite context, feature tracing and inner/outer seam checks.
No automated preset wiring or runtime wide support. Review before next layer.

'''
if new not in old:
    p.write_text(new+old)
archive=Path('/Users/vlad/Code/defjam-data/scratch/menu-ui-pilot-20261017-seam-v2')
archive.mkdir(exist_ok=False)
shutil.copytree(root,archive/'seam-v2')
shutil.copy2(root.parent/'review.html',archive/'review.html')
files={}
for p in sorted(archive.rglob('*')):
    if p.is_file():
        relative=p.relative_to(archive)
        source=root.parent/'review.html' if str(relative)=='review.html' else root/relative.relative_to('seam-v2')
        digest=hashlib.sha256(p.read_bytes()).hexdigest()
        assert digest==hashlib.sha256(source.read_bytes()).hexdigest()
        files[str(relative)]=digest
(archive/'manifest.json').write_text(json.dumps(dict(schema=1,
    role='Immutable refinement overlay; v1 remains separate',files=files),indent=2))
print(json.dumps({'archive':str(archive),'files_verified':len(files),'source_guides':2}))
