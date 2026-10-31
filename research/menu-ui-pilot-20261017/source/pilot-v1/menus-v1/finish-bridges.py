"""Composite focused edits only, preserving source and outer art exactly.

Match repair grain to the source by measuring high-frequency RMS in the fixed
material context; smoothly reduce that filtering toward retained outer scenery.
No pixel in source context is filtered or painted.
"""
from pathlib import Path
from PIL import Image,ImageFilter
import numpy as np,json,hashlib,importlib.util
p=Path(__file__).resolve().parent;sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();spec=importlib.util.spec_from_file_location('seams',p.parent/'seam-v2/assemble-bridges.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);rows=json.loads((p/'bridge-layout.json').read_text());records=[]
def rms(im):
 x=np.array(im.convert('RGB')).astype(float);b=np.array(im.filter(ImageFilter.GaussianBlur(4)).convert('RGB')).astype(float);return float(np.sqrt(np.mean((x-b)**2)))
for label in ['options','jukebox']:
 old=np.array(Image.open(p/(label+'-wide-draft.png')).convert('RGB'));out=old.copy();allowed=np.zeros(old.shape[:2],bool)
 for r in [r for r in rows if r['menu']==label]:
  name=r['label'];raw=Image.open(p/(name+'-raw.png')).convert('RGB');assert abs(raw.width/raw.height-1536/1440)<.005;edit=raw.resize((1536,1440),Image.Resampling.LANCZOS);edit.save(p/(name+'-normalized.png'));crop=tuple(r['master_crop']);target=Image.open(p/(name+'-target.png')).convert('RGB');join=r['join'];left=r['side']=='left';ctx=(join,0,join+96,1440) if left else (join-96,0,join,1440);reference_rms=rms(target.crop(ctx));trials=[]
  for radius in [0,1,2,3,4,6,8]:
   filtered=edit if radius==0 else edit.filter(ImageFilter.GaussianBlur(radius));trials.append((abs(rms(filtered.crop(ctx))-reference_rms),radius))
  radius=min(trials)[1];gen=np.array(edit.crop((512,0,1024,1440))).astype(float);soft=np.array(edit.filter(ImageFilter.GaussianBlur(radius)).crop((512,0,1024,1440))).astype(float) if radius else gen
  weight=np.linspace(0,1,512) if left else np.linspace(1,0,512);gen=gen+(soft-gen)*weight[None,:,None]
  x0=crop[0]+512;x1=x0+512;fixed=old[:,x0:x1].astype(float)
  # Source-side edge extrapolation plus outer four-edge constraints preserve
  # real context while preventing a new seam where the repair meets old sides.
  fixed[:,0]=np.clip(2*old[:,x0-1].astype(float)-old[:,x0-2],0,255);fixed[:,-1]=np.clip(2*old[:,x1].astype(float)-old[:,x1+1],0,255)
  t=np.linspace(0,1,512)[:,None]
  for y in [0,-1]:fixed[y]=gen[y]+(fixed[y,0]-gen[y,0])*(1-t)+(fixed[y,-1]-gen[y,-1])*t
  matched,res=m.boundary_match(gen,fixed);out[:,x0:x1]=np.rint(matched).clip(0,255).astype('uint8');allowed[:,x0:x1]=True
  records.append(dict(label=name,raw_size=list(raw.size),normalized_size=[1536,1440],raw_sha256=sha(p/(name+'-raw.png')),domain=[x0,0,512,1440],source_context_RMS=reference_rms,grain_radius=radius,grain_weight='linear 0at retained outer,1at original source',harmonic_residual=res,protected_original_and_outer_context_exact=True))
 assert np.array_equal(out[~allowed],old[~allowed]);known=2176 if label=='options' else 1920;assert np.array_equal(out[:,1600:1600+known],old[:,1600:1600+known]);Image.fromarray(out).save(p/(label+'-wide-refined.png'))
 for side,edge in [('left',1600),('right',3776 if label=='options' else 3520)]:Image.fromarray(out).crop((edge-384,0,edge+384,1440)).save(p/(label+'-'+side+'-join.png'))
 for ratio,w in [('4x3',1920),('16x10',2304),('16x9',2560),('21x9',3360),('32x9',5120)]:x=(5120-w)//2;Image.fromarray(out).crop((x,0,x+w,1440)).save(p/(label+'-'+ratio+'-refined.png'))
 for side,x0,x1 in [('left',0,1600),('right',3520,5120)]:
  layer=Image.new('RGBA',(5120,1440));layer.paste(Image.fromarray(out[:,x0:x1]).convert('RGBA'),(x0,0));layer.save(p/(label+'-'+side+'-extension-refined.png'))
(p/'bridge-receipt.json').write_text(json.dumps(dict(records=records,source_and_retained_outer_pixels='exact',rejected_support_proofs='reflected/edge-hold material proofs not adopted',processor_sha256=sha(Path(__file__))),indent=2)+'\n');print(json.dumps(records,indent=2))
