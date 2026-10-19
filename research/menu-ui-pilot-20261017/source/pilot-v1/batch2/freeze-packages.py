"""Finalize package documentation before freezing; artwork bytes remain exact."""
from pathlib import Path
import hashlib,json,shutil
root=Path(__file__).resolve().parent
repo=Path('/Users/vlad/Code/DefJam-Modding-Tools')
old='One square bridge output changed resolution1254→1024 while retaining the50%\njoin and24%poster-top landmark.'
new='A1024square bridge target returned1254square; assembly uniformly restored the\noriginal1440square crop. The50%join and24%poster-top landmark stayed registered.'
for relative in ['docs/menu-art-workflow.md','docs/widescreen-backgrounds.md']:
    p=repo/relative;s=p.read_text();assert old in s;p.write_text(s.replace(old,new))
shutil.copy2(repo/'docs/menu-art-workflow.md',root/'menu-art-workflow.md')
base=Path('/Users/vlad/Code/defjam-data/scratch')
for folder in ['menu-ui-approved-skyline-v3-20261017','menu-ui-second-batch-20261017']:
    dst=base/folder
    for name,source in [('menu-widescreen-extension.txt',repo/'prompts/menu-widescreen-extension.txt'),
                        ('widescreen-backgrounds.md',repo/'docs/widescreen-backgrounds.md'),
                        ('menu-art-workflow.md',repo/'docs/menu-art-workflow.md')]:
        shutil.copy2(source,dst/'documentation'/name)
    readme=(root/'menu-art-workflow.md').read_text().replace('../prompts/menu-widescreen-extension.txt','documentation/menu-widescreen-extension.txt').replace('(widescreen-backgrounds.md)','(documentation/widescreen-backgrounds.md)')
    (dst/'README.md').write_text(readme)
    shutil.copy2(Path('docs/research/menu-ui-second-batch-results-2026-10-17.md'),dst/'documentation/menu-ui-second-batch-results-2026-10-17.md')
    if folder.startswith('menu-ui-approved'):
        (dst/'experiment/review.html').write_text('<!doctype html><meta charset="utf-8"><meta http-equiv="refresh" content="0;url=../review.html"><a href="../review.html">Approved skyline review</a>')
    else:
        for name in ['verify-final.py','verification.json','menu-art-workflow.md','freeze-packages.py']:
            shutil.copy2(root/name,dst/'pilot-v1/batch2'/name)
    manifest_path=dst/'manifest.json'
    manifest=json.loads(manifest_path.read_text())
    manifest['files']={str(p.relative_to(dst)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(dst.rglob('*')) if p.is_file() and p!=manifest_path}
    master=dst/('experiment' if folder.startswith('menu-ui-approved') else 'pilot-v1')/'seam-v3/title-skyline-wide-master-v3.png'
    assert hashlib.sha256(master.read_bytes()).hexdigest()==manifest['approved_art_master_sha256']
    manifest_path.write_text(json.dumps(manifest,indent=2))
    print(folder,len(manifest['files']),'files; approved art exact')
