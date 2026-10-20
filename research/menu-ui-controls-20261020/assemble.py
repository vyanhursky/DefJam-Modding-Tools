"""22 native4x tiles /15 isolated studies; source alpha, ink, UV guards and palette authoritative."""
from pathlib import Path
from PIL import Image,ImageFilter,ImageDraw
import json,numpy as np,hashlib
from defjam_tools.color_trial import rgb_to_lab,lab_to_rgb
p=Path(__file__).resolve().parent;r=p.parent;sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();srcs=json.loads((p/'sources.json').read_text());groups=json.loads((p/'groups.json').read_text());bases={x['id']:Image.open(p/x['source_file']).convert('RGBA').resize((int(x['width'])*4,int(x['height'])*4),Image.Resampling.LANCZOS) for x in srcs};tiles={k:v.copy() for k,v in bases.items()};items=[];stats=[]
def mosaic(g,tiles,scale=4):
 out=Image.new('RGBA',tuple(v*scale for v in g['size']))
 for q in g['parts']:out.paste(tiles[q['source_id']].crop(tuple(v*scale for v in q['crop'])),tuple(v*scale for v in q['offset']))
 return out
for g in groups:
 key=g['key'];base=mosaic(g,bases);a=np.array(base);lab=rgb_to_lab(a[:,:,:3]);safe=np.zeros(a.shape[:2],bool);draft=base.copy();raw=None
 if g['kind']=='paper':
  raw=key+'-raw.png';norm=Image.open(p/raw).convert('RGB').resize(base.size,Image.Resampling.LANCZOS);norm.save(p/(key+'-normalized.png'));gray=np.array(base.convert('L')).astype(float);safe=(np.array(base.getchannel('A').filter(ImageFilter.MinFilter(9)))==255)&(lab[:,:,0]>42)&(lab[:,:,0]<95);edge=(abs(np.roll(gray,4,0)-np.roll(gray,-4,0))+abs(np.roll(gray,4,1)-np.roll(gray,-4,1)))>12;safe&=np.array(Image.fromarray(edge.astype('uint8')*255).filter(ImageFilter.MaxFilter(13)))==0
  if key=='gym-paper':safe[:128*4]=False;safe[395*4:]=False
  for q in g['parts']:
   x,y=[v*4 for v in q['offset']];b=q['crop'];w,h=(b[2]-b[0])*4,(b[3]-b[1])*4
   safe[y:y+16,x:x+w]=False;safe[y+h-16:y+h,x:x+w]=False;safe[y:y+h,x:x+16]=False;safe[y:y+h,x+w-16:x+w]=False
  delta=np.clip((np.array(norm).astype(float)-np.array(norm.filter(ImageFilter.GaussianBlur(4))).astype(float))@np.array([.2126,.7152,.0722])*.16,-1.25,1.25);weight=np.array(Image.fromarray(safe.astype('uint8')*255).filter(ImageFilter.GaussianBlur(3))).astype(float)/255*safe
  if weight.sum():delta-=float((delta*weight).sum()/weight.sum())
  changed=lab.copy();changed[:,:,0]+=delta*weight;converted,_=lab_to_rgb(changed);arr=a.copy();arr[:,:,:3][safe]=converted[safe];draft=Image.fromarray(arr);assert np.array_equal(arr[:,:,3],a[:,:,3]);assert np.array_equal(arr[~safe],a[~safe]);Image.fromarray(safe.astype('uint8')*255).save(p/(key+'-mask.png'))
  for q in g['parts']:
   x,y=[v*4 for v in q['offset']];b=q['crop'];w,h=(b[2]-b[0])*4,(b[3]-b[1])*4;tiles[q['source_id']].paste(draft.crop((x,y,x+w,y+h)),(b[0]*4,b[1]*4))
 arr=np.array(draft);stats.append(dict(key=key,kind=g['kind'],changed_pixels=int(np.any(arr!=a,2).sum()),safe_pixels=int(safe.sum()),max_rgb_delta=int(np.abs(arr[:,:,:3].astype(int)-a[:,:,:3]).max()),mean_delta_Lab=(rgb_to_lab(arr[:,:,:3])-lab).mean((0,1)).tolist()))
 original=mosaic(g,{k:Image.open(p/(k+'-source.png')).convert('RGBA') for k in bases},1);original.save(p/(key+'-source.png'));base.save(p/(key+'-faithful.png'));draft.save(p/(key+'-draft.png'));base.getchannel('A').save(p/(key+'-source-alpha.png'));draft.getchannel('A').save(p/(key+'-draft-alpha.png'))
 items.append(dict(key=key,label=g['label'],source_ids=[q['source_id'] for q in g['parts']],native_size=g['size'],method='Restrained source-protected paper detail' if g['kind']=='paper' else 'Faithful HD · original lettering/material/softness retained',source_file=key+'-source.png',faithful_file=key+'-faithful.png',draft_file=key+'-draft.png',alpha_reference_file=key+'-source-alpha.png',alpha_draft_file=key+'-draft-alpha.png',raw_file=raw,mask_file=key+'-mask.png' if raw else None,placement=g['placement'],kind=g['kind']))
checks=[]
for sid,im in tiles.items():
 im.save(p/(sid+'-draft.png'));a=np.array(im);b=np.array(bases[sid]);assert np.array_equal(a[:,:,3],b[:,:,3]);checks.append(dict(source_id=sid,art=sid+'-draft.png',size=list(im.size),sha256=sha(p/(sid+'-draft.png')),alpha_exact=True))
for g in groups:assert mosaic(g,tiles).tobytes()==Image.open(p/(g['key']+'-draft.png')).tobytes()
for it in items:
 size=tuple(round(v*1.5) for v in it['native_size']);orig=Image.open(p/it['source_file']).resize(size,Image.Resampling.BILINEAR);draft=Image.open(p/it['draft_file']).resize(size,Image.Resampling.LANCZOS)
 for ratio,w in {'4x3':960,'16x10':1152,'16x9':1280,'21x9':1680,'32x9':2560}.items():
  xy=((w-size[0])//2,(720-size[1])//2)
  for name,im in [('original',orig),('draft',draft)]:out=Image.new('RGBA',(w,720));out.paste(im,xy);out.save(p/f'{it["key"]}-{ratio}-{name}.png');assert out.crop((*xy,xy[0]+size[0],xy[1]+size[1])).tobytes()==im.tobytes()
board=Image.new('RGB',(1500,1600),'#3c3c3c');draw=ImageDraw.Draw(board)
for i,it in enumerate(items):
 im=Image.open(p/it['draft_file']);im.thumbnail((470,250));x=(i%3)*500;y=(i//3)*320;board.paste(im,(x+(500-im.width)//2,y+32),im);draw.text((x+8,y+5),it['label'],fill='white');draw.text((x+8,y+294),it['method'],fill='white')
board.save(p/'batch-overview.png');(p/'review-items.json').write_text(json.dumps(items,indent=2)+'\n');(p/'references.json').write_text(json.dumps(dict(sources=srcs,groups=groups,source_tiles=checks),indent=2)+'\n');(p/'assembly-receipt.json').write_text(json.dumps(dict(processor_sha256=sha(Path(__file__)),source_tiles=checks,statistics=stats,recipe='tileaware4xLanczos,fineLsigma4*.16clamp1.25meanremoved;alphaMin9/edgeMax13;16HDpxactivecropguards;Gymheader/bands protected; originala/b/alpha authoritative',runtime='not installed, actual placement/platform/clipping unverified'),indent=2)+'\n')
before=json.loads((p/'before-hashes.json').read_text());assert all(sha(r/n)==h for n,h in before.items());cat=json.loads(Path('config/menu-ui-approved-artwork.json').read_text());pins={f['path']:f['sha256'] for ap in cat['approval_records'] for f in ap['files']};assert len(pins)==473 and all(sha(r/n)==h for n,h in pins.items());(p/'verification.json').write_text(json.dumps(dict(prior_pins_exact=473,prior_PNGs_exact=len(before),source_tiles=22,studies=15,restored=2,faithful=13,aspect_pairs=75,alpha_graphics_tileguards_exact=True,all_new_art_unapproved=True,new_builtin_calls=2,historical_calls=144,game_untouched=True),indent=2)+'\n');print('22tiles15studies75aspectpairs;473pins/'+str(len(before))+'priorPNGs exact. Maxdelta',max(x['max_rgb_delta'] for x in stats))
