from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
p=Path(__file__).resolve().parent;old=p.parent/'menus-v1';rows=json.loads((p/'layout.json').read_text());receipt=[]
for menu in ['options','jukebox']:
 src=np.array(Image.open(old/(menu+'-wide-refined.png')).convert('RGB'));out=src.copy()
 for r in rows:
  if r['menu']!=menu:continue
  edit=np.array(Image.open(p/(r['label']+('-courses-normalized.png' if menu=='jukebox' else '-normalized.png'))).convert('RGB'));x=r['crop'][0];join=r['join'];left=r['side']=='left'
  if left:out[:,x:x+join]=edit[:,:join]
  else:out[:,x+join:x+2320]=edit[:,join:]
  # Raw source-context diagnostics reveal model registration before blending.
  check=Image.fromarray(out).crop((1600-240,0,1600+240,1440)) if left else Image.fromarray(out).crop((3520-240,0,3520+240,1440));check.save(p/(r['label']+'-hard-join.png'))
 assert np.array_equal(out[:,1600:3520],src[:,1600:3520])
 if menu=='options':assert np.array_equal(out[:,:3520],src[:,:3520])
 Image.fromarray(out).save(p/(menu+'-wide-hard.png'))
