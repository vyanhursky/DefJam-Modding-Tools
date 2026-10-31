"""Bounded menu-logo/emblem surface restoration; originals govern glyphs/alpha.

AI raws are texture proposals only. Align their visible bounds to baseline for
fine detail sampling, NEVER use generated geometry/alpha as runtime mapping.
Keep faithful RGBA at alpha transitions, strong source edges, padding and joins.
Split candidates onto exact original stored tile canvases; never import/select.
"""
from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image,ImageFilter,ImageDraw,ImageOps
from defjam_tools.color_trial import rgb_to_lab,lab_to_rgb,box_blur
p=Path(__file__).resolve().parent
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
assemblies=json.loads((p/'assembled-references.json').read_text())
configs=[dict(label='title-logo',active=[508,88],parts=[])]+assemblies
records=[];tiles=[]
for cfg in configs:
 label=cfg['label'];base=Image.open(p/(label+'-faithful.png')).convert('RGBA');original=np.array(base);rgb=original[:,:,:3];alpha=original[:,:,3];h,w=alpha.shape
 rawp=p/(label+'-raw.png');raw=Image.open(rawp).convert('RGBA');raw_arr=np.array(raw)
 def bounds(a):return Image.fromarray((a>=64).astype('uint8')*255).getbbox()
 srcbox=bounds(raw_arr[:,:,3]);destbox=bounds(alpha);assert srcbox and destbox
 # Registration applies to texture residual only, not to generated silhouette.
 crop=raw.crop(srcbox).resize((destbox[2]-destbox[0],destbox[3]-destbox[1]),Image.Resampling.LANCZOS)
 field=Image.new('RGBA',base.size,(0,0,0,0));field.paste(crop,destbox[:2]);field_arr=np.array(field)
 lab=rgb_to_lab(rgb);proposal=rgb_to_lab(field_arr[:,:,:3])[:,:,0];light=lab[:,:,0]
 detail=.35*((proposal-box_blur(proposal,6))-(light-box_blur(light,6)))
 detail=np.clip(detail,-2,2)
 held=box_blur((alpha==255).astype(float),4)<.999999
 # Hold strong glyph/stroke/scuff edges so bbox alignment cannot rewrite them.
 gx=np.abs(np.diff(light,axis=1,prepend=light[:,:1]));gy=np.abs(np.diff(light,axis=0,prepend=light[:1]))
 strong=np.maximum(gx,gy)>3.0;held|=box_blur(strong.astype(float),4)>0
 held[:8]=True;held[-8:]=True;held[:,:8]=True;held[:,-8:]=True
 active=cfg['active'];held[int(active[1]*4):]=True;held[:,int(active[0]*4):]=True
 if cfg['parts']:
  for part in cfg['parts']:
   x,y=map(int,part['assembled_origin'])
   if x>0:held[:,max(0,(x-2)*4):(x+2)*4]=True
   if y>0:held[max(0,(y-2)*4):(y+2)*4]=True
 held|=(field_arr[:,:,3]<200)
 allowed=box_blur((~held).astype(float),3)*(~held)
 outlab=lab.copy();outlab[:,:,0]+=detail*allowed
 assert np.array_equal(lab[:,:,1:],outlab[:,:,1:])
 new,clipped=lab_to_rgb(outlab);new[held|clipped]=rgb[held|clipped]
 result=np.dstack([new,alpha]);assert np.array_equal(result[:,:,3],alpha) and np.array_equal(result[held],original[held])
 dest=p/(label+'-restrained.png');Image.fromarray(result).save(dest)
 Image.fromarray(held.astype('uint8')*255).save(p/(label+'-protected.png'))
 Image.fromarray(field_arr).save(p/(label+'-registered-proposal.png'))
 delta=rgb_to_lab(new)-lab;visible=alpha>32
 row=dict(label=label,size=base.size,raw_size=raw.size,raw_sha256=sha(rawp),baseline_sha256=sha(p/(label+'-faithful.png')),output_sha256=sha(dest),raw_alpha_bbox=srcbox,baseline_alpha_bbox=destbox,normalization='Alpha>=64 bounding-box registration for surface residual ONLY; generated geometry/alpha rejected',max_detail_L=2.,strength=.35,alpha_exact=True,protected_exact=True,visible_changed_pixels=int(np.any(result!=original,axis=2)[visible].sum()),median_Lab=np.median(delta[visible],axis=0).tolist(),max_abs_Lab=np.abs(delta[visible]).max(axis=0).tolist())
 records.append(row)
 # Exact source-shaped split, preserving stored unused texels from faithful tile.
 for part in cfg['parts']:
  n=part['image'];tilepath=p/(f'door-{n}-faithful.png');tile=np.array(Image.open(tilepath).convert('RGBA'));before=tile.copy();x,y=map(int,part['assembled_origin']);uv=part['nominal_sample_uv'];tw,th=int(uv[2]*4),int(uv[3]*4)
  tile[:th,:tw]=result[y*4:y*4+th,x*4:x*4+tw]
  assert np.array_equal(tile[:,:,3],before[:,:,3]);assert np.array_equal(tile[th:],before[th:]);assert np.array_equal(tile[:,tw:],before[:,tw:])
  target=p/(f'door-{n}-restrained.png');Image.fromarray(tile).save(target);tiles.append(dict(label=label,name=n,source_id=part['source_id'],size=[tile.shape[1],tile.shape[0]],path=target.name,sha256=sha(target),alpha_exact=True,unused_padding_exact=True))
 print(label,'alpha/glyph edges/padding/seams held;',row['visible_changed_pixels'],'fine-detail pixels',flush=True)
(p/'restoration-receipt.json').write_text(json.dumps(dict(schema=1,processor_sha256=sha(Path(__file__)),status='Unapproved restrained artwork; not imported/installed',description='Source spatial Lab chroma, broad luminance and strong RGB edges preserved; bounded fine L detail only; complete faithful alpha exact. No source keying.',records=records,tiles=tiles),indent=2)+'\n')
# Dedicated accurate-alpha PNG composites for visual QA / browser download.
for cfg in configs:
 for version in ['source','faithful','restrained','raw']:
  f=p/(cfg['label']+'-'+version+'.png');im=Image.open(f).convert('RGBA')
  im.getchannel('A').convert('RGB').save(p/(cfg['label']+'-'+version+'-alpha.png'))
  for bgname,color in [('dark',(40,40,40,255)),('light',(232,232,232,255))]:
   bg=Image.new('RGBA',im.size,color);bg.alpha_composite(im);bg.convert('RGB').save(p/(cfg['label']+'-'+version+'-'+bgname+'.png'))
# Original/candidate at the SAME display footprint, not an invented game screen.
canvas=Image.new('RGB',(1400,1520),(32,32,32));draw=ImageDraw.Draw(canvas)
for i,cfg in enumerate(configs):
 y=30+i*160;draw.text((20,y-20),cfg['label']+' - original / restrained',fill='white')
 for j,v in enumerate(['source','restrained']):
  im=Image.open(p/(cfg['label']+'-'+v+'-dark.png'));thumb=ImageOps.contain(im,(640,135));canvas.paste(thumb,(20+j*700,y+(135-thumb.height)//2))
canvas.save(p/'original-restored-contact.jpg')
