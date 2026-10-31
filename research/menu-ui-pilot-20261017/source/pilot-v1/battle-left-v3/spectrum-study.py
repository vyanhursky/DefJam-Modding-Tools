"""Match native material frequency/tonal statistics without copying texture strips."""
from pathlib import Path
from PIL import Image,ImageFilter
import numpy as np,json
from defjam_tools.color_trial import rgb_to_lab,lab_to_rgb
p=Path(__file__).resolve().parent;r=p.parent;im=Image.open(p/'normalized.png').convert('RGB');base=Image.open(r/'battle-setup-v2/cmtype-wide-v2.png').convert('RGB');src=Image.open(r/'battle-v1/cmtype-source.png').convert('RGB').crop((0,26,69,448));source=rgb_to_lab(np.array(src));gen=rgb_to_lab(np.array(im.crop((0,78,1600,1344)).resize((534,422),Image.Resampling.LANCZOS)))
# Source and proposal use the same native texel density. Pool isotropic PSD,
# retaining generated phase and low-frequency design/brick arrangement.
def spectral_profile(a):
 h,w=a.shape;a=a-a.mean();win=np.hanning(h)[:,None]*np.hanning(w)[None,:];f=np.fft.fft2(a*win);fy=np.fft.fftfreq(h)[:,None];fx=np.fft.fftfreq(w)[None,:];rad=np.sqrt(fy*fy+fx*fx);bins=np.minimum((rad*128).astype(int),90);v=np.abs(f)**2/(np.sum(win**2));return np.bincount(bins.ravel(),weights=v.ravel(),minlength=91)/np.maximum(np.bincount(bins.ravel(),minlength=91),1)
s=source[:,:,0];g=gen[:,:,0];sp=spectral_profile(s);gp=spectral_profile(g);ratio=np.sqrt(np.maximum(sp,.001)/np.maximum(gp,.001));ratio=np.clip(ratio,.2,3);ratio=np.convolve(np.pad(ratio,(2,2),mode='edge'),np.ones(5)/5,'valid');h,w=g.shape;rad=np.sqrt(np.fft.fftfreq(h)[:,None]**2+np.fft.fftfreq(w)[None,:]**2);gain=np.interp(rad*128,np.arange(91),ratio);gate=np.clip((rad-1/32)/(1/12-1/32),0,1);gate=gate*gate*(3-2*gate);gain=1+(gain-1)*gate
f=np.fft.fft2(g-g.mean());matched=np.fft.ifft2(f*gain).real;matched*=s.std()/max(matched.std(),.01);matched+=s.mean();out=gen.copy();out[:,:,0]=matched
for c in [1,2]:out[:,:,c]=(gen[:,:,c]-gen[:,:,c].mean())*min(1.25,source[:,:,c].std()/max(gen[:,:,c].std(),.1))+source[:,:,c].mean()
rgb,_=lab_to_rgb(out);up=Image.fromarray(rgb).resize((1600,1266),Image.Resampling.LANCZOS);a=np.array(base);a[78:1344,:1600]=np.array(up)
# Continue final generated bottom rows with same global Lab color response.
bottom=rgb_to_lab(np.array(im.crop((0,1344,1600,1440))));bottom[:,:,0]=(bottom[:,:,0]-g.mean())*(s.std()/max(g.std(),.1))+s.mean()
for c in [1,2]:bottom[:,:,c]=(bottom[:,:,c]-gen[:,:,c].mean())*min(1.25,source[:,:,c].std()/max(gen[:,:,c].std(),.1))+source[:,:,c].mean()
b,_=lab_to_rgb(bottom);a[1344:,:1600]=b
# Additive8px seam feather to source edge, not source image repetition.
basea=np.array(base);delta=basea[:,1600].astype(float)-a[:,1599].astype(float)
for i in range(8):a[78:,1599-i]=np.rint(a[78:,1599-i]+delta[78:]*(1-i/8)**2).clip(0,255).astype('uint8')
Image.fromarray(a).save(p/'study-spectrum.png');Image.fromarray(a).crop((1216,0,1984,1440)).save(p/'spectrum-join.png');(p/'spectrum-study.json').write_text(json.dumps(dict(radial_amplitude_ratio=ratio.tolist(),native_source_size=list(src.size),native_generated_size=[534,422],source_L_mean=float(s.mean()),source_L_std=float(s.std()),generated_L_mean=float(g.mean()),generated_L_std=float(g.std())),indent=2)+'\n')
