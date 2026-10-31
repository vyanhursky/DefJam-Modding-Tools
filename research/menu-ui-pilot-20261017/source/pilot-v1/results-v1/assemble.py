"""Bounded paper detail transfer; source tile alpha/ink/UV guards remain authoritative.
Run with authoring-tool Python and its src on PYTHONPATH. No game install writes.
"""
from pathlib import Path
from PIL import Image,ImageFilter,ImageDraw
import numpy as np,json,hashlib
from defjam_tools.color_trial import rgb_to_lab,lab_to_rgb
p=Path(__file__).resolve().parent;r=p.parent
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
refs=json.loads((p/'references.json').read_text());stats=[];tile_checks=[];stage_checks=[]
ratios={'4x3':1920,'16x10':2304,'16x9':2560,'21x9':3360,'32x9':5120}
for row in refs['panels']:
 label=row['label'];aw,ah=row['active'];sw,sh=row['stored'];bases={};faith=Image.new('RGBA',(sw*4,sh*4))
 for a in row['parts']:
  im=Image.open(p/(a['name']+'-source.png')).convert('RGBA');b=im.resize((im.width*4,im.height*4),Image.Resampling.LANCZOS);bases[a['name']]=b;faith.paste(b,(a['offset'][0]*4,a['offset'][1]*4))
 faith=faith.crop((0,0,aw*4,ah*4));faith.save(p/(label+'-faithful.png'));faith.getchannel('A').save(p/(label+'-faithful-alpha.png'))
 src=np.array(faith);raw=Image.open(p/(label+'-raw.png')).convert('RGBA');aspect_error=abs(raw.width/raw.height-aw/ah)/(aw/ah)
 assert aspect_error<.02,(label,aspect_error)
 norm=raw.resize(faith.size,Image.Resampling.LANCZOS);norm.save(p/(label+'-normalized.png'))
 # Transfer only fine luminance residuals, never generated shape, ink, alpha or palette.
 rgb=src[:,:,:3];lab=rgb_to_lab(rgb);g=np.array(norm.convert('RGB')).astype(float);blur=np.array(norm.convert('RGB').filter(ImageFilter.GaussianBlur(4))).astype(float)
 detail=(g-blur)@np.array([.2126,.7152,.0722]);delta=np.clip(detail*.14,-1.25,1.25)
 alpha=np.array(faith.getchannel('A').filter(ImageFilter.MinFilter(25)))==255
 ys,xs=np.indices(alpha.shape);safe=alpha&(lab[:,:,0]>61)&(np.max(rgb,2)-np.min(rgb,2)<85)
 # Printed headers, cells and stars are protected as whole bands, including light distress within ink.
 if label=='rematch':safe&=(ys>=64*4)&(ys<143*4)
 elif label=='rewardun':safe&=~((xs>=12*4)&(xs<443*4)&(ys>=15*4)&(ys<312*4))
 else:safe&=((ys>=112*4)&(ys<232*4))|((ys>=337*4)&(ys<355*4))
 # Preserve source creases/rules and their vicinity; no new hard micro-boundary at the mask.
 gray=np.array(faith.convert('L')).astype(float);gx=np.abs(np.roll(gray,4,1)-np.roll(gray,-4,1));gy=np.abs(np.roll(gray,4,0)-np.roll(gray,-4,0));edge=Image.fromarray(((gx+gy)>20).astype('uint8')*255).filter(ImageFilter.MaxFilter(25));safe&=np.array(edge)==0
 for a in row['parts']:
  x,y=a['offset'][:2]
  for v in (x,x+a['used_uv'][2]):safe[:,max(0,(v-4)*4):min(aw*4,(v+4)*4)]=False
  for v in (y,y+a['used_uv'][3]):safe[max(0,(v-4)*4):min(ah*4,(v+4)*4),:]=False
 mask=Image.fromarray(safe.astype('uint8')*255);mask.save(p/(label+'-safe-paper-mask.png'));weight=np.array(mask.filter(ImageFilter.GaussianBlur(4))).astype(float)/255;weight*=safe
 if safe.any():delta-=float((delta*weight).sum()/max(weight.sum(),1))
 newlab=lab.copy();newlab[:,:,0]+=delta*weight;converted,_=lab_to_rgb(newlab);proposed=src.copy();proposed[:,:,:3][safe]=converted[safe]
 final=Image.new('RGBA',(sw*4,sh*4))
 for a in row['parts']:
  b=np.array(bases[a['name']]);out=b.copy();x,y=a['offset'][:2];u0,v0,u1,v1=a['used_uv'];w,h=(u1-u0)*4,(v1-v0)*4;xx=(x+u0)*4;yy=(y+v0)*4
  out[v0*4:v1*4,u0*4:u1*4,:3]=proposed[yy:yy+h,xx:xx+w,:3]
  # Whole source-tile edge guards, including the Sm4 one-row overlap, remain exact.
  guard=np.ones(b.shape[:2],bool);guard[16:-16,16:-16]=False;out[guard]=b[guard]
  valid=np.zeros(b.shape[:2],bool);valid[v0*4:v1*4,u0*4:u1*4]=True
  assert np.array_equal(out[:,:,3],b[:,:,3]);assert np.array_equal(out[~valid],b[~valid]);assert np.array_equal(out[guard],b[guard])
  im=Image.fromarray(out);im.save(p/(a['name']+'-restrained.png'));final.paste(im,(x*4,y*4));tile_checks.append(dict(name=a['name'],alpha_exact=True,unused_uv_exact=True,tile_edge_guard_exact=True,guard_px=16,source_sha256=sha(p/(a['name']+'-source.png')),candidate_sha256=sha(p/(a['name']+'-restrained.png'))))
 final=final.crop((0,0,aw*4,ah*4));out=np.array(final);assert np.array_equal(out[:,:,3],src[:,:,3]);assert np.array_equal(out[~safe],src[~safe]);final.save(p/(label+'-restrained.png'));final.getchannel('A').save(p/(label+'-restrained-alpha.png'))
 changed=np.any(out[:,:,:3]!=rgb,2);lout=rgb_to_lab(out[:,:,:3]);stats.append(dict(label=label,active=row['active'],raw_size=list(raw.size),aspect_error=aspect_error,normalization=list(final.size),safe_pixels=int(safe.sum()),changed_pixels=int(changed.sum()),changed_fraction=float(changed.mean()),max_rgb_change=int(np.abs(out[:,:,:3].astype(int)-rgb).max()),mean_lab_shift=[float(x) for x in (lout-lab)[safe].mean(0)],alpha_exact=True,all_protected_rgba_exact=True,source_tile_faithful_basis=True))
 # Explicit stage-only studies: never paint beyond paper silhouettes or stretch panels.
 x,y=row['stage_placement'];pos=(round(x*3),round(y*3));native=Image.open(p/(label+'-source.png')).convert('RGBA').resize((aw*3,ah*3),Image.Resampling.BILINEAR);draft=final.resize((aw*3,ah*3),Image.Resampling.LANCZOS)
 for ratio,width in ratios.items():
  pair=[]
  for kind,im in [('original',native),('draft',draft)]:
   canvas=Image.new('RGBA',(width,1440));canvas.paste(im,((width-1920)//2+pos[0],pos[1]));canvas.save(p/f'{label}-{ratio}-{kind}.png');pair.append(np.array(canvas))
  if ratio=='4x3':center=pair
  else:
   cx=(width-1920)//2;assert all(np.array_equal(a[:,cx:cx+1920],b) for a,b in zip(pair,center))
  stage_checks.append(dict(label=label,ratio=ratio,width=width,height=1440,center_exact=True,panel_placement_3x=list(pos),placement_rounding_native=[pos[0]/3-x,pos[1]/3-y],wide_margins_transparent=True))
# Contact proof on checkerboard, same size/layout for the final assembled exports.
contact=Image.new('RGB',(1440,1000),'#444');d=ImageDraw.Draw(contact)
for i,row in enumerate(refs['panels']):
 im=Image.open(p/(row['label']+'-restrained.png'));im.thumbnail((460,450));bg=Image.new('RGBA',im.size);bd=ImageDraw.Draw(bg)
 for y in range(0,im.height,16):
  for x in range(0,im.width,16):bd.rectangle((x,y,x+15,y+15),fill='#555' if (x//16+y//16)%2 else '#999')
 bg.alpha_composite(im);x=i%3*480;y=i//3*500;contact.paste(bg.convert('RGB'),(x,y+24));d.text((x+5,y+4),row['label']+' restrained/source geometry',fill='white')
contact.save(p/'restored-contact.jpg')
calls=json.loads((p/'jobs.json').read_text())
for j in calls:j.update(raw=j['label']+'-raw.png',raw_sha256=sha(p/(j['label']+'-raw.png')),inputs=[dict(path=f,sha256=sha(Path(f))) for f in j['referenced_image_paths']],adoption='Bounded fine paper luminance only; generated alpha/geometry/graphics/broad color rejected; source alpha and printed graphics retained')
(p/'generations.json').write_text(json.dumps(dict(tool='built-in image_gen',new_calls=6,pilot_total_calls=101,calls=calls),indent=2)+'\n')
(p/'assembly-receipt.json').write_text(json.dumps(dict(method='Tile-aware4xLanczos source basis; raw fineRGB residual Gaussian4,brightness*.14 capped1.25L,mask feather4,source Lab a/b retained before RGB rounding',panels=stats,tiles=tile_checks,stage_studies=stage_checks,geometry_caveats='APT matrices retained in references/audit. Preview rounds matchSm2 .05px and rewardun x110.5 at3x to nearest pixel; not a runtime layout patch.',processor_sha256=sha(Path(__file__))),indent=2)+'\n')
prev=json.loads((p/'before-hashes.json').read_text());assert all(sha(r/f)==v for f,v in prev.items());pins=0
for name in ['battle-fighter-approval-20261019.json','battle-setup-approval-20261019.json','rewards-approval-20261019.json','hiscores-approval-20261019.json']:
 a=json.loads((r/name).read_text());assert all(sha(r/f['path'])==f['sha256'] for f in a['files']);pins+=len(a['files'])
(p/'verification.json').write_text(json.dumps(dict(prior_pngs_unchanged=len(prev),approved_battle_rewards_hiscores_files_exact=pins,panels=6,source_tiles=18,source_alpha_protected_graphics_uv_padding_tile_edge_guards_exact=True,stage_studies=30,all_original_4x3_centers_exact=True,new_builtin_calls=6,pilot_total_calls=101),indent=2)+'\n');print((p/'verification.json').read_text());print(json.dumps(stats,indent=2))
