"""Alpha-only technical derivatives; keep liked built-in draft RGB exact.

No resizing or geometric mapping. Registered original coverage must match the target canvas.
Registered original alpha is capped by existing alpha so clear padding cannot be filled.
Original source alpha remains authoritative
for later game-shape registration. These are unapproved raw-canvas art auditions.
"""
from pathlib import Path
from PIL import Image, ImageDraw
import numpy as np, json, hashlib
p=Path(__file__).resolve().parent;b=p.parent/'branding-v1'
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
jobs=json.loads((p/'generations.json').read_text());records=[];rows=[]
for j in jobs:
 label=j['label'];old=Image.open(b/(label+'-raw.png')).convert('RGBA');edit=Image.open(p/(label+'-edit.png')).convert('RGBA')
 assert old.size==edit.size,(label,old.size,edit.size)
 # User liked existing RGB. Do not adopt incidental AI recoloring/retexturing.
 x=np.array(old);e=np.array(Image.open(p/(label+'-registered-alpha.png')).convert('L'));coverage=np.minimum(x[:,:,3],e)
 out=old.copy();out.putalpha(Image.fromarray(coverage));out.save(p/(label+'-repaired.png'))
 out.getchannel('A').convert('RGB').save(p/(label+'-repaired-alpha.png'))
 y=np.array(out)
 assert np.array_equal(x[:,:,:3],y[:,:,:3]);assert np.array_equal(np.minimum(x[:,:,3],e),y[:,:,3]);assert np.all(y[:,:,3]<=x[:,:,3])
 comps={}
 for bgname,color in [('light',(210,210,210)),('dark',(35,35,35)),('checker',None)]:
  if color is not None:bg=Image.new('RGBA',out.size,color+(255,))
  else:
   yy,xx=np.indices((out.height,out.width));v=np.where((xx//28+yy//28)%2,170,105).astype('uint8');bg=Image.fromarray(np.dstack([v,v,v,np.full_like(v,255)]),'RGBA')
  bg.alpha_composite(out);bg.convert('RGB').save(p/(label+'-repaired-'+bgname+'.jpg'));comps[bgname]=bg
 # Compare old and repaired in precisely the same canvas at the same scale.
 canvas=Image.new('RGB',(1600,440),(24,24,24));d=ImageDraw.Draw(canvas);d.text((20,12),label+' | previous generated draft / alpha repair (same RGB)',fill='white')
 for idx,im in enumerate([old,out]):
  preview=comps['checker'].copy()
  if idx==0:
   yy,xx=np.indices((out.height,out.width));v=np.where((xx//28+yy//28)%2,170,105).astype('uint8');preview=Image.fromarray(np.dstack([v,v,v,np.full_like(v,255)]),'RGBA');preview.alpha_composite(im)
  preview.thumbnail((780,390),Image.Resampling.LANCZOS);canvas.paste(preview.convert('RGB'),(idx*800+(800-preview.width)//2,40+(390-preview.height)//2))
 canvas.save(p/(label+'-before-after.jpg'));rows.append(canvas)
 records.append(dict(label=label,size=list(out.size),old_sha256=sha(b/(label+'-raw.png')),edit_sha256=sha(p/(label+'-edit.png')),registered_alpha_sha256=sha(p/(label+'-registered-alpha.png')),displacement_sha256=sha(p/(label+'-registration.npz')),output_sha256=sha(p/(label+'-repaired.png')),rgb_equals_previous_raw=True,alpha_equals_minimum_of_previous_and_registered_source=True,alpha_never_increased=True,alpha_changed_pixels=int(np.sum(x[:,:,3]!=y[:,:,3])),fully_clear_pixels=int(np.sum(y[:,:,3]==0)),partially_covered_pixels=int(np.sum((y[:,:,3]>0)&(y[:,:,3]<250))),opaque_material_pixels=int(np.sum(y[:,:,3]>=250)),alpha_range=[int(y[:,:,3].min()),int(y[:,:,3].max())]))
contact=Image.new('RGB',(1600,len(rows)*440),(24,24,24))
for i,row in enumerate(rows):contact.paste(row,(0,i*440))
contact.save(p/'before-after-contact.jpg')
(p/'assembly-receipt.json').write_text(json.dumps(dict(recipe='previous raw RGB + min(previous alpha, locally registered original alpha); no RGB/canvas resize; retry alpha rejected as incomplete',records=records),indent=2)+'\n')
print(json.dumps(records,indent=2))
