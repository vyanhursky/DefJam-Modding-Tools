"""Repair both original wall joins, leaving core and all exterior beyond128nativepx exact."""
from pathlib import Path
from PIL import Image,ImageFilter
import numpy as np,json,hashlib
from defjam_tools.color_trial import rgb_to_lab,lab_to_rgb
p=Path(__file__).resolve().parent;sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();base=Image.open(p/'profile-wall-wide-v1.png').convert('RGB');arr=np.array(base);out=arr.copy();receipt=[]
def smooth(arr):
 lo=arr.min(0);span=np.maximum(arr.max(0)-lo,1);e=np.clip((arr-lo)/span*255,0,255).astype('uint8');im=Image.fromarray(np.repeat(e[:,None,:],3,axis=1)).filter(ImageFilter.GaussianBlur(12));return np.array(im)[:,1].astype(float)/255*span+lo
for side in ['left','right']:
 raw=Image.open(p/f'profile-wall-{side}-bridge-raw.png').convert('RGB');err=abs(raw.width/raw.height-.8)/.8;assert err<.02;native=raw.resize((384,480),Image.Resampling.LANCZOS);norm=native.resize((1152,1440),Image.Resampling.LANCZOS);nl=rgb_to_lab(np.array(norm));gap=nl[:,384:768].copy();x0,x1=(1216,1600) if side=='left' else (3520,3904);fixed=rgb_to_lab(arr);left=smooth(fixed[:,x0-16:x0].mean(1))-smooth(nl[:,368:384].mean(1));right=smooth(fixed[:,x1:x1+16].mean(1))-smooth(nl[:,768:784].mean(1));left=np.clip(left,[-8,-6,-6],[8,6,6]);right=np.clip(right,[-8,-6,-6],[8,6,6]);t=np.linspace(0,1,384);gap+=left[:,None,:]*(1-t)[None,:,None]+right[:,None,:]*t[None,:,None];rgb,_=lab_to_rgb(gap);proposal=rgb.astype(float);blend=np.ones(384)
 if side=='left':blend[:24]=np.linspace(0,1,24)
 else:blend[-24:]=np.linspace(1,0,24)
 out[:,x0:x1]=np.round(proposal*blend[None,:,None]+arr[:,x0:x1]*(1-blend)[None,:,None]).astype('uint8');receipt.append(dict(side=side,raw_size=list(raw.size),aspect_error=err,adopted_master_rect=[x0,0,x1,1440],gap_native=[128,0,256,480],source_center_changed=False,outer_fade_hd=24,endpoint_Lab_clamp=[8,6,6],profile_sigma_hd=12))
assert np.array_equal(out[:,1600:3520],arr[:,1600:3520]);assert np.array_equal(out[:,:1216],arr[:,:1216]);assert np.array_equal(out[:,3904:],arr[:,3904:]);im=Image.fromarray(out);im.save(p/'profile-wall-wide-v2.png');checks=[]
for ratio,w in {'4x3':1920,'16x10':2304,'16x9':2560,'21x9':3360,'32x9':5120}.items():
 crop=im.crop(((5120-w)//2,0,(5120+w)//2,1440));crop.save(p/f'profile-wall-{ratio}-draft-v2.png');assert np.array_equal(np.array(crop)[:,(w-1920)//2:(w+1920)//2],arr[:,1600:3520]);checks.append(dict(ratio=ratio,center_exact=True))
for side,x in [('left',1600),('right',3520)]:im.crop((x-384,0,x+384,1440)).save(p/f'profile-wall-{side}-join-v2.png')
(p/'assembly-wide-v2-receipt.json').write_text(json.dumps(dict(processor_sha256=sha(Path(__file__)),bridges=receipt,centers=checks,original_core_and_outer_exact=True,new_calls=2,batch_calls=15,historical_calls=142,all_unapproved=True),indent=2)+'\n');v=json.loads((p/'verification.json').read_text());(p/'verification-v1.json').write_text(json.dumps(v,indent=2)+'\n');v.update(new_builtin_calls=15,historical_total=142,wall_revision='v2bothjoinrepair',sourcecore_outerexact=True);(p/'verification.json').write_text(json.dumps(v,indent=2)+'\n');print('Both128pxjoinbands repaired;core/outerexact;v1history retained')
