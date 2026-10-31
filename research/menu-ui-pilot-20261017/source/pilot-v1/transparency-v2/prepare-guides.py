"""Technical alpha references only; no source/raw/accepted artwork is edited."""
from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
p=Path(__file__).resolve().parent;b=p.parent/'branding-v1';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
labels=['title-logo']+['emblem-'+s for s in ['story','battle','options','jukebox','extras','high-scores','rewards','credits']];records=[]
for label in labels:
 source=Image.open(b/(label+'-faithful.png')).convert('RGBA');raw=Image.open(b/(label+'-raw.png')).convert('RGBA');a=np.array(raw)
 srcbox=source.getchannel('A').point(lambda x:255 if x>=64 else 0).getbbox()
 # Bright physical material bounds exclude the unwanted raw matte/glow; this
 # guide registration is semantic reference only, not final/runtime geometry.
 mask=(a[:,:,3]>=64)&(a[:,:,:3].min(axis=2)>130)
 dstbox=Image.fromarray(mask.astype('uint8')*255).getbbox();assert srcbox and dstbox
 crop=source.crop(srcbox).resize((dstbox[2]-dstbox[0],dstbox[3]-dstbox[1]),Image.Resampling.LANCZOS)
 guide=Image.new('RGBA',raw.size,(0,0,0,0));guide.paste(crop,dstbox[:2]);guide.save(p/(label+'-mapped-source.png'))
 guide.getchannel('A').convert('RGB').save(p/(label+'-coverage-guide.png'))
 bg=Image.new('RGBA',raw.size,(255,0,255,255));bg.alpha_composite(guide);bg.convert('RGB').save(p/(label+'-magenta-reference.png'))
 records.append(dict(label=label,raw_size=list(raw.size),source_alpha_bbox=srcbox,raw_material_bbox=dstbox,source_sha256=sha(b/(label+'-faithful.png')),raw_sha256=sha(b/(label+'-raw.png')),guide_sha256=sha(p/(label+'-coverage-guide.png')),note='Reference alignment only. Grayscale coverage must retain partial transparency; no global black/green key.'))
(p/'guide-receipt.json').write_text(json.dumps(records,indent=2)+'\n');print('9graded-alpha guides prepared; raw RGB and source alpha untouched')
