from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image
R=Path('/Users/vlad/Code/defjam-data/hd-work/texture-workshop/experiments/fighters-local-restoration-20261030');read=lambda p:json.loads(Path(p).read_text());pix=lambda p:np.array(Image.open(p).convert('RGBA'));sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();out=[]
for r in read(R/'results.json'):
 p=Path(r['output_path']);rec=read(r['receipt_path']);im=pix(p);own=pix(rec['faithful_path']);held=np.zeros(im.shape[:2],bool);checks=dict(output_pin=sha(p)==r['output_sha256'],source_pin=sha(rec['original_path'])==rec['original_sha256'],faithful_pin=sha(rec['faithful_path'])==rec['faithful_sha256'],raw_local_pin=sha(rec['raw_local_path'])==rec['raw_local_sha256'],own_shape=im.shape==own.shape,own_alpha_exact=np.array_equal(im[...,3],own[...,3]))
 for x0,y0,x1,y1 in rec['source_holds']:held[y0*4:y1*4,x0*4:x1*4]=True
 checks['own_holds_exact']=np.array_equal(im[held],own[held]);mask=lambda n:np.array(Image.open(p.parent/(n+'.png')).convert('L'))>0
 if r['kind']=='main-state':checks['own_seam_core_exact']=np.array_equal(im[mask('seam_core')],own[mask('seam_core')]);checks['outside_active_exact']=np.array_equal(im[~mask('active')],own[~mask('active')])
 else:
  base=pix(p.parent/'continuity-baseline.png');active=mask('detail_active');support=mask('source_support');transition=mask('transition');clean=pix(rec['clean_reference_path'])[:1024,1024:2048];checks.update(clean_ref_pin=sha(rec['clean_reference_path'])==rec['clean_reference_sha256'],clean_exterior_exact=np.array_equal(im[~transition&~held,:3],clean[~transition&~held,:3]),outside_active_baseline_exact=np.array_equal(im[~active],base[~active]),active_inside_source=not np.any(active&~support))
 assert all(checks.values()),(r['key'],checks);out.append(dict(key=r['key'],source_id=r['source_id'],output_sha256=r['output_sha256'],checks=checks,assembly=rec['assembly']))
(R/'technical-audit.json').write_text(json.dumps(dict(schema=1,drafts=len(out),checks_passed=True,textures=out),indent=2)+'\n');print('PASS',len(out),'local source-palette/alpha/holds/seam/state invariants')
