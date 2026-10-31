from pathlib import Path
from PIL import Image,ImageFilter
import numpy as np,json,hashlib,importlib.util
p=Path(__file__).resolve().parent;old=p.parent/'menus-v1';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();spec=importlib.util.spec_from_file_location('seams',p.parent/'seam-v2/assemble-bridges.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);rows=json.loads((p/'layout.json').read_text());records=[]
for menu in ['options','jukebox']:
 im=Image.open(p/(menu+'-wide-hard.png')).convert('RGB');out=np.array(im);src=np.array(Image.open(old/(menu+'-wide-refined.png')).convert('RGB'))
 for r in rows:
  if r['menu']!=menu:continue
  left=r['side']=='left';edge=1600 if left else 3520;x0,x1=(edge-384,edge) if left else (edge,edge+384);raw=out.copy();radius=3 if menu=='options' else 1.5
  gen=raw[:,x0:x1].astype(float);soft=np.array(im.filter(ImageFilter.GaussianBlur(radius)))[:,x0:x1].astype(float);t=np.linspace(0,1,384) if left else np.linspace(1,0,384);gen+=(soft-gen)*t[None,:,None]
  fixed=gen.copy()
  fixed[:,0]=np.clip(2*raw[:,x0-1].astype(float)-raw[:,x0-2],0,255);fixed[:,-1]=np.clip(2*raw[:,x1].astype(float)-raw[:,x1+1],0,255)
  u=np.linspace(0,1,384)[:,None]
  for y in [0,-1]:fixed[y]=gen[y]+(fixed[y,0]-gen[y,0])*(1-u)+(fixed[y,-1]-gen[y,-1])*u
  matched,res=m.boundary_match(gen,fixed);out[:,x0:x1]=np.rint(matched).clip(0,255).astype('uint8');records.append(dict(label=r['label'],generated_source='-courses-raw' if menu=='jukebox' else '-raw',allowed_master=[0,0,1600,1440] if left else [3520,0,1600,1440],boundary_matching_domain=[x0,0,384,1440],grain_softness_radius=radius,residual=res))
 assert np.array_equal(out[:,1600:3520],src[:,1600:3520])
 if menu=='options':assert np.array_equal(out[:,:3520],src[:,:3520])
 Image.fromarray(out).save(p/(menu+'-wide-v2.png'))
 for ratio,w in [('4x3',1920),('16x10',2304),('16x9',2560),('21x9',3360),('32x9',5120)]:x=(5120-w)//2;Image.fromarray(out).crop((x,0,x+w,1440)).save(p/(menu+'-'+ratio+'-v2.png'))
 for side,edge in [('left',1600),('right',3520)]:
  Image.fromarray(out).crop((edge-384,0,edge+384,1440)).save(p/(menu+'-'+side+'-join.png'));Image.fromarray(src).crop((edge-384,0,edge+384,1440)).save(p/(menu+'-'+side+'-before.png'))
 # Complete right architecture reference, not merely a narrow source boundary.
 if menu=='options':Image.fromarray(out).crop((3100,0,5120,1440)).save(p/'options-door-complete.png')
(p/'assembly-receipt.json').write_text(json.dumps(dict(records=records,source_centers_exact=True,options_all_pixels_left_of_original_right_bound_exact=True,calls=5,pilot_total=54,processor_sha256=sha(Path(__file__)),note='Numerical matching is a diagnostic; visual masonry/architecture alignment reviewed separately.'),indent=2)+'\n')
