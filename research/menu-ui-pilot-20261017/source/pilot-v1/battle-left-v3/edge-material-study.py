from pathlib import Path
from PIL import Image,ImageFilter
import numpy as np,json
from defjam_tools.color_trial import rgb_to_lab,lab_to_rgb
p=Path(__file__).resolve().parent;r=p.parent;base=Image.open(r/'battle-setup-v2/cmtype-wide-v2.png').convert('RGB');b=np.array(base);gen=Image.open(p/'normalized.png').convert('RGB').crop((0,0,1600,1440));gen=gen.resize((534,480),Image.Resampling.LANCZOS).resize((1600,1440),Image.Resampling.LANCZOS);g=rgb_to_lab(np.array(gen));s=rgb_to_lab(b[:,1600:1696]);gp=g[:,1088:1600]
def smooth(v):
 # Use RGB float profile via explicit padded convolution,not8bit filters.
 k=np.exp(-np.arange(-192,193,dtype=float)**2/(2*64**2));k/=k.sum();return np.stack([np.convolve(np.pad(v[:,c],(192,192),mode='edge'),k,'valid') for c in range(v.shape[1])],1)
sm=smooth(s.mean(1));gm=smooth(gp.mean(1));sv=np.maximum(smooth((s*s).mean(1))-sm*sm,.01);gv=np.maximum(smooth((gp*gp).mean(1))-gm*gm,.01);gain=np.clip(np.sqrt(sv/gv),.3,1.6);out=(g-gm[:,None,:])*gain[:,None,:]+sm[:,None,:];rgb,_=lab_to_rgb(out);a=b.copy();a[78:,:1600]=rgb[78:]
# Only8px additive boundary conditioning,source is never painted over.
delta=b[:,1600].astype(float)-a[:,1599].astype(float)
for i in range(8):a[78:,1599-i]=np.rint(a[78:,1599-i]+delta[78:]*(1-i/8)**2).clip(0,255).astype('uint8')
t=np.linspace(0,1,16);w=t*t*(3-2*t);a[78:94,:1600]=np.rint(b[78:94,:1600]*(1-w[:,None,None])+a[78:94,:1600]*w[:,None,None]).astype('uint8')
Image.fromarray(a).save(p/'study-edge-material.png');Image.fromarray(a).crop((1216,0,1984,1440)).save(p/'edge-material-join.png');(p/'edge-material-study.json').write_text(json.dumps(dict(source_band=[1600,0,96,1440],generated_band=[1088,0,512,1440],gaussian_profile_sigma=64,lab_mean_source=sm.tolist(),lab_mean_generated=gm.tolist(),lab_gain=gain.tolist(),native_resample=[534,480,1600,1440]),indent=2)+'\n')
