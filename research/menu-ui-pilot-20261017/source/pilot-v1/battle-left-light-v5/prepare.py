from pathlib import Path
from PIL import Image
import json,hashlib
r=Path('/Users/vlad/.codex/worktrees/01c5/DefJamFFNY-recomp/logs/ui-restoration-20261017/pilot-v1');p=r/'battle-left-light-v5';p.mkdir(exist_ok=True);sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();(p/'before-hashes.json').write_text(json.dumps({str(f.relative_to(r)):sha(f) for f in r.rglob('*.png') if p not in f.parents},indent=2)+'\n');(p/'review-before.html').write_bytes((r/'review.html').read_bytes());a=Image.open(r/'battle-left-v3/cmtype-wide-v3.png').convert('RGB');a.crop((640,0,2080,720)).save(p/'lighting-target.png');a.crop((1120,0,2080,640)).save(p/'left-light-before.png');print('V3 is authoritative base: pre-v4 right retained')
