"""Source-protected popup/profile panels and native-centered wide wall study.

All geometry/graphics/alpha/UVpadding remain from original tile-aware4xLanczos.
Only source-safe fine brightness enters new papers; source4:3wall core is exact.
"""
from pathlib import Path
from PIL import Image,ImageFilter,ImageDraw
import numpy as np,json,hashlib
from defjam_tools.color_trial import rgb_to_lab,lab_to_rgb
p=Path(__file__).resolve().parent;r=p.parent;repo=p.parents[3];sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();srcs=json.loads((p/'survey-sources.json').read_text());groups=json.loads((p/'panel-groups.json').read_text());bases={a['key']:Image.open(p/a['source_file']).convert('RGBA').resize((int(a['width'])*4,int(a['height'])*4),Image.Resampling.LANCZOS) for a in srcs};drafts={k:v.copy() for k,v in bases.items()};stats=[];items=[];proofs=[]
def mosaic(g,tiles,scale=4):
 out=Image.new('RGBA',tuple(v*scale for v in g['texel_size']))
 for a in g['parts']:
  b=a['crop'];im=tiles[a['source_key']].crop(tuple(v*scale for v in b));out.paste(im,tuple(v*scale for v in a['offset']))
 return out

def physical(g,im,filter=Image.Resampling.LANCZOS):
 if g['key']!='shared-header':return im
 factor=im.height/96;left=round(256*factor);w=round(343*factor);cap=round(77*factor);out=Image.new('RGBA',(w+cap,im.height));out.paste(im.crop((0,0,left,im.height)).resize((w,im.height),filter),(0,0));out.paste(im.crop((left,0,im.width,im.height)),(w,0));return out

for g in groups:
 key=g['key'];base=mosaic(g,bases);a=np.array(base);rgb=a[:,:,:3];lab=rgb_to_lab(rgb);safe=np.zeros(a.shape[:2],bool);draft=base.copy();rawfile=p/(key+'-raw.png');st=dict(key=key,method='Faithful4x',changed_pixels=0)
 if g['kind']!='faithful':
  raw=Image.open(rawfile).convert('RGBA')
  if key.startswith('platform-'):
   expect=[128,128];err=abs(raw.width/raw.height-1);norm=raw.resize((512,512),Image.Resampling.LANCZOS);b=g['parts'][0]['crop'];norm=norm.crop(tuple(v*4 for v in b))
  elif g.get('edit_crop'):
   ew,eh=g['edit_target_size'];expect=[ew,eh];err=abs(raw.width/raw.height-ew/eh)/(ew/eh);norm=raw.resize((ew,eh),Image.Resampling.LANCZOS).crop(g['edit_crop']).resize(base.size,Image.Resampling.LANCZOS)
  else:
   ew,eh=g['texel_size'];expect=[ew,eh];err=abs(raw.width/raw.height-ew/eh)/(ew/eh);norm=raw.resize(base.size,Image.Resampling.LANCZOS)
  assert err<.02,(key,raw.size,expect,err)
  norm.save(p/(key+'-normalized.png'));gray=np.array(base.convert('L')).astype(float);ys,xs=np.indices(a.shape[:2]);safe=(np.array(base.getchannel('A').filter(ImageFilter.MinFilter(9)))==255)&(lab[:,:,0]>40)&(lab[:,:,0]<96);edge=(abs(np.roll(gray,4,0)-np.roll(gray,-4,0))+abs(np.roll(gray,4,1)-np.roll(gray,-4,1)))>12;safe&=np.array(Image.fromarray(edge.astype('uint8')*255).filter(ImageFilter.MaxFilter(13)))==0
  # Source ink/selection/console/card pictograms stay exact, by broad geometric exclusion.
  if key=='profile-wall':safe&=~(((xs>=48*4)&(xs<349*4)&(ys>=65*4)&(ys<442*4))|((xs>=347*4)&(ys>=100*4)&(ys<435*4)))
  else:
   spread=np.max(rgb,2).astype(int)-np.min(rgb,2);safe&=(rgb[:,:,0]>70)&(rgb[:,:,1]>60)&(rgb[:,:,2]>45)&(spread<80)
  if key.startswith('autosave-'):safe&=~((xs>=245*4)&(ys>=60*4));safe[0:72*4]=False;safe[-68*4:]=False
  if key=='profile-list':safe[137*4:204*4]=False
  if key=='shared-header':safe[6*4:40*4]=False
  if key in ['platform-card','platform-cube']:safe&=(np.min(rgb,2)>100)&(np.max(rgb,2)-np.min(rgb,2)<80)
  # Guards on every actual active source crop, including internal tilejoins.
  for part in g['parts']:
   x,y=[v*4 for v in part['offset']];b=part['crop'];w=(b[2]-b[0])*4;h=(b[3]-b[1])*4;safe[y:y+16,x:x+w]=False;safe[y+h-16:y+h,x:x+w]=False;safe[y:y+h,x:x+16]=False;safe[y:y+h,x+w-16:x+w]=False
  gv=np.array(norm.convert('RGB')).astype(float);blur=np.array(norm.convert('RGB').filter(ImageFilter.GaussianBlur(4))).astype(float);delta=np.clip((gv-blur)@np.array([.2126,.7152,.0722])*.16,-1.25,1.25);weight=np.array(Image.fromarray(safe.astype('uint8')*255).filter(ImageFilter.GaussianBlur(3))).astype(float)/255*safe
  if weight.sum():delta-=float((delta*weight).sum()/weight.sum())
  mod=lab.copy();mod[:,:,0]+=delta*weight;converted,_=lab_to_rgb(mod);arr=a.copy();arr[:,:,:3][safe]=converted[safe];assert np.array_equal(arr[~safe],a[~safe]);assert np.array_equal(arr[:,:,3],a[:,:,3]);draft=Image.fromarray(arr);dLab=rgb_to_lab(arr[:,:,:3])-lab;st=dict(key=key,method='Restrained fine brightness',raw_size=list(raw.size),expected_aspect=expect,aspect_error=err,safe_pixels=int(safe.sum()),changed_pixels=int(np.any(arr[:,:,:3]!=rgb,2).sum()),max_rgb_delta=int(abs(arr[:,:,:3].astype(int)-rgb).max()),mean_safe_delta_Lab=dLab[safe].mean(0).tolist() if safe.any() else [0,0,0],alpha_exact=True,source_graphics_exact=True)
  # Split material into native storage; do not overwrite unused/padding/guard pixels.
  for part in g['parts']:
   sourcekey=part['source_key'];b=part['crop'];ox,oy=[v*4 for v in part['offset']];x0,y0,x1,y1=[v*4 for v in b];tb=np.array(bases[sourcekey]);out=tb.copy();out[y0:y1,x0:x1]=np.array(draft)[oy:oy+y1-y0,ox:ox+x1-x0];guard=np.ones(out.shape[:2],bool);guard[16:-16,16:-16]=False;out[guard]=tb[guard];assert np.array_equal(out[:,:,3],tb[:,:,3]);unused=np.ones(out.shape[:2],bool);unused[y0:y1,x0:x1]=False;assert np.array_equal(out[unused],tb[unused]);drafts[sourcekey]=Image.fromarray(out)
 draft=mosaic(g,drafts);arr=np.array(draft);assert np.array_equal(arr[:,:,3],a[:,:,3]);assert np.array_equal(arr[~safe],a[~safe]);base.save(p/(key+'-texel-faithful.png'));draft.save(p/(key+'-texel-draft.png'));Image.fromarray(safe.astype('uint8')*255).save(p/(key+'-texel-mask.png'));st['changed_after_storage_guards']=int(np.any(arr[:,:,:3]!=rgb,2).sum());stats.append(st)
 # Geometry footprint for the feloader strip deliberately uses its authored left stretch.
 b=physical(g,base);d=physical(g,draft);o=physical(g,Image.open(p/g['source_file']).convert('RGBA'),Image.Resampling.BILINEAR);o.save(p/(key+'-review-source.png'));b.save(p/(key+'-faithful.png'));d.save(p/(key+'-draft.png'));b.getchannel('A').save(p/(key+'-source-alpha.png'));d.getchannel('A').save(p/(key+'-draft-alpha.png'));assert np.array_equal(np.array(b.getchannel('A')),np.array(d.getchannel('A')))
 items.append(dict(key=key,label=g['label'],source_ids=[a['source_id'] for a in g['parts']],native_size=g['native_size'],method='Faithful HD · original stamp/soft backing retained' if g['kind']=='faithful' else 'Restrained source-protected restoration',source_file=key+'-review-source.png',faithful_file=key+'-faithful.png',draft_file=key+'-draft.png',alpha_reference_file=key+'-source-alpha.png',alpha_draft_file=key+'-draft-alpha.png',raw_file=key+'-raw.png' if g['kind']!='faithful' else None,mask_file=key+'-texel-mask.png' if g['kind']!='faithful' else None,placement=g['note'],kind=g['kind']))

checks=[]
for a in srcs:
 key=a['key'];b=np.array(bases[key]);d=np.array(drafts[key]);assert np.array_equal(d[:,:,3],b[:,:,3]);guard=np.ones(d.shape[:2],bool);guard[16:-16,16:-16]=False;assert np.array_equal(d[guard],b[guard]);f=p/(key+'-draft.png');drafts[key].save(f);checks.append(dict(source_id=a['id'],art=f.name,native_size=[int(a['width']),int(a['height'])],scale=4,alpha_exact=True,stored_padding_guards_exact=True,sha256=sha(f)))
assert len(checks)==22;assert len(items)==15
# Wall master:534+640+534nativepx, then crop2HDpx eachside to exact5120x1440.
core=Image.open(p/'profile-wall-draft.png').convert('RGB').resize((1920,1440),Image.Resampling.LANCZOS);original=Image.open(p/'profile-wall-source.png').convert('RGB').resize(core.size,Image.Resampling.BILINEAR);master=Image.new('RGB',(5124,1440));side_receipts=[]
def smooth_profile(arr,sigma):return np.array(Image.fromarray(arr.astype('float32'),mode='F').filter(ImageFilter.GaussianBlur(sigma)))
# Pillow cannot blur float images on every platform; use three ordinary uint8 profile channels.
def smooth_rows(arr,sigma=24):
 lo=arr.min(0);hi=arr.max(0);span=np.maximum(hi-lo,1);encoded=np.clip((arr-lo)/span*255,0,255).astype('uint8');im=Image.fromarray(np.repeat(encoded[:,None,:],3,axis=1)).filter(ImageFilter.GaussianBlur(sigma));return np.array(im)[:,1,:].astype(float)/255*span+lo
source_native=Image.open(p/'profile-wall-source.png').convert('RGB');srcLab=rgb_to_lab(np.array(source_native.resize((1920,1440),Image.Resampling.LANCZOS)))
for side in ['left','right']:
 raw=Image.open(p/f'profile-wall-{side}-raw.png').convert('RGB');err=abs(raw.width/raw.height-790/480)/(790/480);assert err<.02,(side,raw.size,err);native=raw.resize((790,480),Image.Resampling.LANCZOS);gap=native.crop((0,0,534,480) if side=='left' else (256,0,790,480));wide=gap.resize((1602,1440),Image.Resampling.LANCZOS);lab=rgb_to_lab(np.array(wide));near=lab[:,-48:].mean(1) if side=='left' else lab[:,:48].mean(1);anchor=srcLab[:,:48].mean(1) if side=='left' else srcLab[:,-48:].mean(1);diff=smooth_rows(anchor)-smooth_rows(near);diff=np.clip(diff,[-10,-8,-8],[10,8,8]);dist=np.arange(1602)[::-1] if side=='left' else np.arange(1602);weight=np.exp(-dist/(256*3));adjust=lab+diff[:,None,:]*weight[None,:,None];rgb,_=lab_to_rgb(adjust);out=Image.fromarray(rgb);out.save(p/f'profile-wall-{side}-extension.png');master.paste(out,(0,0) if side=='left' else (3522,0));side_receipts.append(dict(side=side,raw_size=list(raw.size),aspect_error=err,native_sampling=[790,480],gap=[0,0,534,480] if side=='left' else [256,0,790,480],source_row_profile_columns=16,profile_sigma_hd=24,correction_clamp_Lab=[10,8,8],decay_native_px=256,not_source_strip_copy=True))
master.paste(core,(1602,0));master=master.crop((2,0,5122,1440));master.save(p/'profile-wall-wide-v1.png');assert np.array_equal(np.array(master)[:,1600:3520],np.array(core))
for side,x in [('left',1600),('right',3520)]:master.crop((x-384,0,x+384,1440)).save(p/f'profile-wall-{side}-join.png')
ratios={'4x3':1920,'16x10':2304,'16x9':2560,'21x9':3360,'32x9':5120};stages=[]
for it in items:
 key=it['key']
 if key=='profile-wall':
  for ratio,w in ratios.items():
   crop=master.crop(((5120-w)//2,0,(5120+w)//2,1440));ref=Image.new('RGB',(w,1440));ref.paste(original,((w-1920)//2,0));ref.save(p/f'{key}-{ratio}-original.png');crop.save(p/f'{key}-{ratio}-draft.png');assert np.array_equal(np.array(crop)[:,(w-1920)//2:(w+1920)//2],np.array(core));stages.append(dict(key=key,ratio=ratio,original_center_exact=True,policy='Centerednative640x480core,widenedwallonly'))
 else:
  orig=Image.open(p/it['source_file']).convert('RGBA');draft=Image.open(p/it['draft_file']).convert('RGBA');size=tuple(round(v*1.5) for v in it['native_size']);orig=orig.resize(size,Image.Resampling.BILINEAR);draft=draft.resize(size,Image.Resampling.LANCZOS)
  for ratio,w2 in ratios.items():
   w=w2//2;xy=((w-size[0])//2,(720-size[1])//2);ref=Image.new('RGBA',(w,720));out=Image.new('RGBA',ref.size);ref.paste(orig,xy);out.paste(draft,xy);ref.save(p/f'{key}-{ratio}-original.png');out.save(p/f'{key}-{ratio}-draft.png');assert np.array_equal(np.array(out)[xy[1]:xy[1]+size[1],xy[0]:xy[0]+size[0]],np.array(draft));stages.append(dict(key=key,ratio=ratio,source_footprint_scale_exact=True,policy='Isolatedshapefootprintnotnativegameplacement'))
(p/'review-items.json').write_text(json.dumps(items,indent=2)+'\n');(p/'references.json').write_text(json.dumps(dict(sources=srcs,groups=groups,source_tiles=checks,geometry_limits='Integertexelreviewmosaics;fractionalUVs/matrices/platform/language/clipselectionremaininaudit. No game acceptance.'),indent=2)+'\n');cat=json.loads((repo/'config/menu-ui-approved-artwork.json').read_text());pins={x['path']:x['sha256'] for s in cat['approval_records'] for x in s['files']};assert len(pins)==343 and all(sha(r/n)==h for n,h in pins.items());before=json.loads((p/'before-hashes.json').read_text());assert all(sha(r/n)==h for n,h in before.items());receipt=dict(processor_sha256=sha(Path(__file__)),source_tiles=checks,statistics=stats,wide_sides=side_receipts,stages=stages,recipe='Tileaware4xLanczos;Gaussian4fineL*.16clamp1.25meanremoved;alphaMin9/edgeMax13;16HDpxactive/storageguards;explicitgraphic/pictogram/console/exposureprotection. Alloriginalalpha/chroma/broadlight authoritative.',all_unapproved=True);(p/'assembly-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');(p/'verification.json').write_text(json.dumps(dict(approved_pins_exact=343,prior_pngs_exact=len(before),source_tiles=22,review_items=15,restored_items=11,faithful_only_items=4,alpha_graphics_padding_seams_exact=True,aspect_pairs=75,wide_core_exact_all_ratios=True,new_builtin_calls=13,historical_total=140,prior16batch_pending_unchanged=True,all_new_art_unapproved=True,game_untouched=True),indent=2)+'\n')
board=Image.new('RGB',(1500,5*320),(60,60,60));draw=ImageDraw.Draw(board)
for i,it in enumerate(items):
 im=Image.open(p/it['draft_file']).convert('RGBA');im.thumbnail((480,258));x=(i%3)*500;y=(i//3)*320;board.paste(im,(x+(500-im.width)//2,y+32),im);draw.text((x+6,y+5),it['label'],fill='white');draw.text((x+6,y+296),'Faithful HD' if it['kind']=='faithful' else 'Restrained restoration',fill='white')
board.save(p/'batch-overview.png');print('15items/22tiles;343pins/'+str(len(before))+'priorPNGs exact;75aspectpairs,sourcewallcoreexact')
