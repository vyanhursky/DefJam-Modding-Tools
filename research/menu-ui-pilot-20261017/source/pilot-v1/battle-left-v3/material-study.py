from pathlib import Path
from PIL import Image,ImageFilter,ImageDraw
import numpy as np,json
from defjam_tools.color_trial import rgb_to_lab,lab_to_rgb
p=Path(__file__).resolve().parent;r=p.parent;base=Image.open(r/'battle-setup-v2/cmtype-wide-v2.png').convert('RGB');source=base.crop((1600,0,1808,1440));im=Image.open(p/'normalized.png').convert('RGB');gen=im.crop((0,0,1600,1440));ref=np.array(source);ctx=np.array(im.crop((1600,0,1808,1440)));srcL=rgb_to_lab(ref);ctxL=rgb_to_lab(ctx);mask=np.s_[78:1344,:,:];sm=srcL[mask].mean((0,1));cm=ctxL[mask].mean((0,1));gain=np.clip(srcL[mask].std((0,1))/np.maximum(ctxL[mask].std((0,1)),.1),.5,2)
variants=[]
for label,native in [('native-sampled',True),('raw-sampling',False)]:
 x=gen
 if native:x=x.resize((534,480),Image.Resampling.LANCZOS).resize((1600,1440),Image.Resampling.LANCZOS)
 a=rgb_to_lab(np.array(x));a=(a-cm)*gain+sm;rgb,_=lab_to_rgb(a);out=np.array(base);out[78:,:1600]=rgb[78:]
 # Tiny native filtering support only:8HDpix generated crossfade,never sourcecopies.
 blend=8
 for i in range(blend):
  w=((i+1)/blend)**2;out[:,1600-blend+i]=np.rint(out[:,1600-blend+i]*(1-w)+np.array(base)[:,1600]*w).astype('uint8')
 out[:78]=np.array(base)[:78];Image.fromarray(out).save(p/('study-'+label+'.png'));variants.append((label,Image.fromarray(out).crop((1216,0,1984,1440))))
contact=Image.new('RGB',(2304,1440));contact.paste(base.crop((1216,0,1984,1440)),(0,0))
for i,(label,im) in enumerate(variants):contact.paste(im,((i+1)*768,0))
contact.save(p/'material-study.png');(p/'context-transfer-study.json').write_text(json.dumps(dict(original_mean=sm.tolist(),rendered_context_mean=cm.tolist(),gain=gain.tolist()),indent=2)+'\n')
