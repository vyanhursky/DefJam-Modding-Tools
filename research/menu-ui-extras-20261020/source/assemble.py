"""Source-protected Extras paper restoration; no game files/installed packs are changed."""
from pathlib import Path
from PIL import Image,ImageFilter,ImageDraw
import numpy as np,json,hashlib
from defjam_tools.color_trial import rgb_to_lab,lab_to_rgb
p=Path(__file__).resolve().parent;r=p.parent;sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();refs=json.loads((p/'references.json').read_text());stats=[];tile_checks=[];stage_checks=[]
placements={'list-paper':(329.6,59.05),'note-37':(145.6,81.5),'note-42':(133.45,107.85),'note-48':(146.45,105.4),'note-52':(158.95,103.9),'ribbon-58':(328.6,63.05)};ratios={'4x3':1920,'16x10':2304,'16x9':2560,'21x9':3360,'32x9':5120}
for row in refs['panels']:
 label=row['label'];aw,ah=row['active'];sw,sh=row['stored'];bases={};faith=Image.new('RGBA',(sw*4,sh*4))
 for a in row['parts']:
  im=Image.open(p/f'image-{a["image"]}-source.png').convert('RGBA');b=im.resize((im.width*4,im.height*4),Image.Resampling.LANCZOS);bases[a['image']]=b;faith.paste(b,tuple(v*4 for v in a['offset']))
 faith=faith.crop((0,0,aw*4,ah*4));faith.save(p/(label+'-faithful.png'));faith.getchannel('A').save(p/(label+'-faithful-alpha.png'));src=np.array(faith);rgb=src[:,:,:3];lab=rgb_to_lab(rgb);proposed=src.copy();safe=np.zeros(src.shape[:2],bool);aspect_error=None;raw_size=None
 if label!='ribbon-58':
  raw=Image.open(p/(label+'-raw.png')).convert('RGBA');raw_size=list(raw.size);aspect_error=abs(raw.width/raw.height-aw/ah)/(aw/ah);assert aspect_error<.05,(label,aspect_error)  # Proposal is detail-only; its silhouette, folds and marks are not adopted.
  norm=raw.resize(faith.size,Image.Resampling.LANCZOS);norm.save(p/(label+'-normalized.png'));g=np.array(norm.convert('RGB')).astype(float);blur=np.array(norm.convert('RGB').filter(ImageFilter.GaussianBlur(4))).astype(float);detail=(g-blur)@np.array([.2126,.7152,.0722]);delta=np.clip(detail*.14,-1.25,1.25)
  alpha=np.array(faith.getchannel('A').filter(ImageFilter.MinFilter(25)))==255;ys,xs=np.indices(alpha.shape);safe=alpha&(lab[:,:,0]>(25 if label=='list-paper' else 55))&(np.max(rgb,2)-np.min(rgb,2)<85)
  # Green storage filler is never adopted as painted material; exact source alpha remains authoritative.
  safe&=~((rgb[:,:,1].astype(int)-rgb[:,:,0]>25)&(rgb[:,:,1].astype(int)-rgb[:,:,2]>25))
  gray=np.array(faith.convert('L')).astype(float);edge=(np.abs(np.roll(gray,4,1)-np.roll(gray,-4,1))+np.abs(np.roll(gray,4,0)-np.roll(gray,-4,0)))>17;protected=np.array(Image.fromarray(edge.astype('uint8')*255).filter(ImageFilter.MaxFilter(25)))>0;safe&=~protected
  if label=='note-37':safe&=ys<126*4  # Whole arrow band, including white distress and clear surroundings, exact.
  if label=='note-48':safe&=~((ys>=140*4)&(ys<185*4))  # Whole red-underlining band exact.
  if label=='list-paper':
   safe&=~((xs<12*4)|(xs>=140*4)|(ys<37*4)|(ys>=332*4))  # Borders/header/ribbon and outer paper frame exact.
  for a in row['parts']:
   x,y=a['offset'];u0,v0,u1,v1=a['used_uv']
   for v in [x+u0,x+u1]:safe[:,max(0,(v-4)*4):min(aw*4,(v+4)*4)]=False
   for v in [y+v0,y+v1]:safe[max(0,(v-4)*4):min(ah*4,(v+4)*4),:]=False
  mask=Image.fromarray(safe.astype('uint8')*255);weight=np.array(mask.filter(ImageFilter.GaussianBlur(4))).astype(float)/255*safe
  if weight.sum():delta-=float((delta*weight).sum()/weight.sum())
  outlab=lab.copy();outlab[:,:,0]+=delta*weight;converted,_=lab_to_rgb(outlab);proposed[:,:,:3][safe]=converted[safe]
 Image.fromarray(safe.astype('uint8')*255).save(p/(label+'-safe-mask.png'));final=Image.new('RGBA',(sw*4,sh*4))
 for a in row['parts']:
  b=np.array(bases[a['image']]);out=b.copy();x,y=a['offset'];u0,v0,u1,v1=a['used_uv'];xx=(x+u0)*4;yy=(y+v0)*4;w=(u1-u0)*4;h=(v1-v0)*4
  out[v0*4:v1*4,u0*4:u1*4,:3]=proposed[yy:yy+h,xx:xx+w,:3];guard=np.ones(b.shape[:2],bool);guard[16:-16,16:-16]=False;out[guard]=b[guard];valid=np.zeros(b.shape[:2],bool);valid[v0*4:v1*4,u0*4:u1*4]=True
  assert np.array_equal(out[:,:,3],b[:,:,3]);assert np.array_equal(out[~valid],b[~valid]);assert np.array_equal(out[guard],b[guard]);im=Image.fromarray(out);file=p/f'image-{a["image"]}-restrained.png';im.save(file);final.paste(im,(x*4,y*4));tile_checks.append(dict(image=a['image'],source_id=a['source_id'],alpha_exact=True,unused_uv_exact=True,edge_guards_exact=True,sha256=sha(file)))
 final=final.crop((0,0,aw*4,ah*4));out=np.array(final);assert np.array_equal(out[:,:,3],src[:,:,3]);assert np.array_equal(out[~safe],src[~safe]);final.save(p/(label+'-restrained.png'));final.getchannel('A').save(p/(label+'-restrained-alpha.png'));delta_lab=rgb_to_lab(out[:,:,:3])-lab;changed=np.any(out[:,:,:3]!=rgb,2);stats.append(dict(label=label,raw_size=raw_size,aspect_error=aspect_error,safe_pixels=int(safe.sum()),changed_pixels=int(changed.sum()),changed_fraction=float(changed.mean()),max_rgb_delta=int(np.abs(out[:,:,:3].astype(int)-rgb).max()),mean_safe_Lab=delta_lab[safe].mean(0).tolist() if safe.any() else [0,0,0],source_alpha_exact=True,protected_pixels_exact=True,ribbon_policy='Faithful HD only,no AI adoption' if label=='ribbon-58' else None))
 # Isolated panels at observed static APT placements; not a flattened live screen or animation preview.
 x,y=placements[label];pos=(round(x*3),round(y*3));native=Image.open(p/(label+'-source.png')).resize((aw*3,ah*3),Image.Resampling.BILINEAR);draft=final.resize((aw*3,ah*3),Image.Resampling.LANCZOS)
 for ratio,width in ratios.items():
  pair=[]
  for kind,im in [('original',native),('draft',draft)]:
   canvas=Image.new('RGBA',(width,1440));canvas.paste(im,((width-1920)//2+pos[0],pos[1]));canvas.save(p/f'{label}-{ratio}-{kind}.png');pair.append(np.array(canvas))
  if ratio=='4x3':centers=pair
  else:
   cx=(width-1920)//2;assert all(np.array_equal(a[:,cx:cx+1920],b) for a,b in zip(pair,centers))
  stage_checks.append(dict(label=label,ratio=ratio,center_exact=True,placement_native=[x,y],placement_3x=list(pos),rounding_native=[pos[0]/3-x,pos[1]/3-y]))
contact=Image.new('RGB',(1440,1000),'#333');d=ImageDraw.Draw(contact)
for i,row in enumerate(refs['panels']):
 im=Image.open(p/(row['label']+'-restrained.png'));im.thumbnail((450,450));bg=Image.new('RGBA',im.size,'#888');bg.alpha_composite(im);x=i%3*480;y=i//3*500;contact.paste(bg.convert('RGB'),(x,y+25));d.text((x+3,y+4),row['label']+' source-protected draft',fill='white')
contact.save(p/'restored-contact.jpg');jobs=json.loads((p/'jobs.json').read_text())
for j in jobs:j.update(raw=j['label']+'-raw.png',raw_sha256=sha(p/(j['label']+'-raw.png')),inputs=[dict(path=f,sha256=sha(Path(f))) for f in j['referenced_image_paths']],adoption='Tiny fine brightness only; original alpha/geometry/broadlight/chroma/arrow/line/rules/padding stayauthoritative')
(p/'generations.json').write_text(json.dumps(dict(tool='built-in image_gen',new_calls=5,pilot_total_calls=106,calls=jobs),indent=2)+'\n');(p/'assembly-receipt.json').write_text(json.dumps(dict(panels=stats,tiles=tile_checks,stages=stage_checks,parameters='4x tile-awareLanczos;Gaussian4 fineL*.14,clip1.25,meanremoved;sourceLab a/b;alphaMin25;gradientguard25;UV/tileguard16outputpx;safeedgefeather4',geometry='Static source APT placements,rounded at3x;exact matrices in extras-metadata.json. Live visibility/state/text/animation omitted.',processor_sha256=sha(Path(__file__))),indent=2)+'\n')
before=json.loads((p/'before-hashes.json').read_text());assert all(sha(r/f)==v for f,v in before.items());catalogue=json.loads((Path(__file__).resolve().parents[4]/'config/menu-ui-approved-artwork.json').read_text());pins={a['path']:a['sha256'] for sc in catalogue['approval_records'] for a in sc['files']};assert all(sha(r/f)==v for f,v in pins.items());ver=dict(prior_pngs_unchanged=len(before),approved_conditional_file_pins_exact=len(pins),source_tiles=9,logical_panels=6,new_builtin_calls=5,pilot_total_calls=106,alphas_protected_graphics_uv_padding_edges_exact=True,isolated_stage_pairs=30,centers_exact=True,all_new_art_unapproved=True);(p/'verification.json').write_text(json.dumps(ver,indent=2)+'\n');print(json.dumps(ver,indent=2));print(json.dumps(stats,indent=2))
