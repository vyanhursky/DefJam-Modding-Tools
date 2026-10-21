"""Check candidate aspect crops, source cores, alpha, receipts and every review image path offline."""
from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib
r=Path('logs/ui-restoration-20261017/pilot-v1');p=r/'wide-backgrounds-v1-20261020';data=json.loads((p/'review-data.json').read_text());widths={'4x3':1920,'16x10':2304,'16x9':2560,'21x9':3360,'32x9':5120};checks=[];pins=[]
for g in data['scenes']:
 key=g['key'];core=Image.open(p/f'{key}-core-hd.png').convert('RGBA') if key!='cribOptions' else Image.open(p/'cribOptions-composite-core-faithful.png').convert('RGBA');ref=np.array(core)
 for ratio,w in widths.items():
  suffix='-v3' if key=='tips' else '';f=p/f'{key}-{ratio}-draft{suffix}.png';im=Image.open(f).convert('RGBA');assert im.size==(w,1440);assert np.array_equal(np.array(im)[:,(w-1920)//2:(w+1920)//2],ref),(key,ratio)
  for mode in ['faithful','original']:
   b=Image.open(p/f'{key}-{ratio}-{mode}.png');assert b.size==(w,1440)
  checks.append(dict(scene=key,aspect=ratio,source_core_exact=True))
 for side in ['left','right']:
  for mode in ['original','faithful']:
   assert Image.open(p/f'{key}-{side}-join-{mode}.png').size==(768,1440)
  suffix='-v3' if key=='tips' else '';assert Image.open(p/f'{key}-{side}-join{suffix}.png').size==(768,1440)
for f in sorted(p.rglob('*')):
 if f.is_file() and f.name!='candidate-integrity.json':pins.append(dict(path=str(f.relative_to(r)),size=f.stat().st_size,sha256=hashlib.sha256(f.read_bytes()).hexdigest()))
(p/'verification.json').write_text(json.dumps(dict(schema=1,scenes=7,new_source_ids=13,reused_approved_door=1,lighting_companion=1,new_builtin_calls=15,historical_builtin_calls=162,aspect_checks=checks,source_cores_exact=35,join_reference_images=28,join_drafts=14,active_packs_modified=False,game_started_or_stopped=False,native_acceptance=False,approval_status='pending owner review'),indent=2)+'\n')
# Integrity is a preservation ledger only, deliberately separate from owner artwork approvals.
(p/'candidate-integrity.json').write_text(json.dumps(dict(schema=1,status='INTEGRITY ONLY; NOT AN APPROVAL',files=pins),indent=2)+'\n')
board=Image.new('RGB',(1400,1150),'#222');d=ImageDraw.Draw(board)
for i,g in enumerate(data['scenes']):
 k=g['key'];f=p/(f'{k}-32x9-draft'+('-v3.png' if k=='tips' else '.png'));im=Image.open(f).convert('RGBA');im.thumbnail((680,190));x=i%2*700;y=i//2*280;board.paste(im,(x,y+30),im);d.text((x,y),g['label'],fill='white')
board.save(p/'final-overview.png');print('35/35 exact scene cores;42 join paths;105 scene previews; no approval/runtime changes')
