"""Match bridge fine L contrast to original boundary material; no new generation or core edits."""
from pathlib import Path
from PIL import Image,ImageFilter
import numpy as np,json,hashlib
from defjam_tools.color_trial import rgb_to_lab,lab_to_rgb
p=Path('logs/ui-restoration-20261017/pilot-v1/wide-backgrounds-v1-20261020');im=Image.open(p/'tips-wide-v2.png').convert('RGB');arr=np.array(im);lab=rgb_to_lab(arr);blur=rgb_to_lab(np.array(im.filter(ImageFilter.GaussianBlur(18))));detail=lab[:,:,0]-blur[:,:,0];out=arr.copy();rows=[]
def smooth(a):
 lo=a.min();span=max(a.max()-lo,1e-6);e=((a-lo)/span*255).clip(0,255).astype('uint8');return np.array(Image.fromarray(np.repeat(e[:,None],3,axis=1)).filter(ImageFilter.GaussianBlur(24)))[:,1]/255*span+lo
for side,x0,x1,ref,gen in [('left',1216,1600,(1600,1696),(1504,1600)),('right',3520,3904,(3424,3520),(3520,3616))]:
 source=smooth(detail[:,ref[0]:ref[1]].std(1));model=smooth(detail[:,gen[0]:gen[1]].std(1));gain=np.clip(source/np.maximum(model,.25),.4,1);width=x1-x0;weight=np.ones(width)
 if side=='left':weight[:48]=np.linspace(0,1,48)
 else:weight[-48:]=np.linspace(1,0,48)
 mod=lab[:,x0:x1].copy();factor=1+(gain[:,None]-1)*weight[None,:];mod[:,:,0]=blur[:,x0:x1,0]+detail[:,x0:x1]*factor;rgb,_=lab_to_rgb(mod);out[:,x0:x1]=rgb;rows.append(dict(side=side,median_gain=float(np.median(gain)),range=[float(gain.min()),float(gain.max())],domain=[x0,0,x1,1440],source_band_hd=list(ref),generated_band_hd=list(gen),highpass_sigma_hd=18,row_sigma_hd=24,outer_fade_hd=48))
assert np.array_equal(out[:,1600:3520],arr[:,1600:3520]);assert np.array_equal(out[:,:1216],arr[:,:1216]);assert np.array_equal(out[:,3904:],arr[:,3904:]);final=Image.fromarray(out);final.save(p/'tips-wide-v3.png')
for a,w in {'4x3':1920,'16x10':2304,'16x9':2560,'21x9':3360,'32x9':5120}.items():final.crop(((5120-w)//2,0,(5120+w)//2,1440)).save(p/f'tips-{a}-draft-v3.png')
for side,x in [('left',1600),('right',3520)]:final.crop((x-384,0,x+384,1440)).save(p/f'tips-{side}-join-v3.png')
(p/'assembly-wide-v3-receipt.json').write_text(json.dumps(dict(processor_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),operation='Ldetailcontrastmatchonly,sourcecorechromaandouterexact',bridges=rows,all_unapproved=True,new_calls=0,historical_calls=162),indent=2)+'\n');print(rows)
