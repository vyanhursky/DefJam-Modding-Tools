"""Source-protected batch: three card papers, four stickers, six Faithful icons and three soft effects.

Only bounded fine brightness can enter source-safe paper. Always retain true tile
alpha, graphics, joins/padding. Isolated aspect previews are NOT native placement.
"""
from pathlib import Path
from PIL import Image,ImageFilter,ImageDraw
import numpy as np,json,hashlib
from defjam_tools.color_trial import rgb_to_lab,lab_to_rgb
p=Path(__file__).resolve().parent;r=p.parent;repo=p.parents[3];sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();srcs=json.loads((p/'sources.json').read_text());stickers=json.loads((p/'sticker-groups.json').read_text());byid={a['id']:a for a in srcs};bykey={a['key']:a for a in srcs};bases={a['key']:Image.open(p/a['source_file']).convert('RGBA').resize(tuple(v*4 for v in a['source_size']),Image.Resampling.LANCZOS) for a in srcs};drafts={k:v.copy() for k,v in bases.items()};stats=[];items=[]
def paper(base,rawfile,kind,keep_center=None):
 raw=Image.open(rawfile).convert('RGBA');err=abs(raw.width/raw.height-base.width/base.height)/(base.width/base.height);assert err<.02,(rawfile,err)
 gen=raw.resize(base.size,Image.Resampling.LANCZOS);a=np.array(base);rgb=a[:,:,:3];lab=rgb_to_lab(rgb);gray=np.array(base.convert('L')).astype(float);ys,xs=np.indices(a.shape[:2]);safe=(np.array(base.getchannel('A').filter(ImageFilter.MinFilter(9)))==255)&(lab[:,:,0]>12)&(lab[:,:,0]<98)
 edge=(abs(np.roll(gray,4,0)-np.roll(gray,-4,0))+abs(np.roll(gray,4,1)-np.roll(gray,-4,1)))>12;safe&=np.array(Image.fromarray(edge.astype('uint8')*255).filter(ImageFilter.MaxFilter(13)))==0
 if kind=='sticker':
  red=(rgb[:,:,0].astype(float)>rgb[:,:,1]*1.6)&(rgb[:,:,0].astype(float)>rgb[:,:,2]*1.6)&(rgb[:,:,1]<110)&(rgb[:,:,2]<110);safe&=np.array(Image.fromarray(red.astype('uint8')*255).filter(ImageFilter.MinFilter(9)))==255
 else:
  safe&=np.max(rgb,2)-np.min(rgb,2)<35
  if keep_center:
   x0,y0,x1,y1=keep_center;safe[(ys>=y0*4)&(ys<y1*4)&(xs>=x0*4)&(xs<x1*4)]=False
 safe[:16]=False;safe[-16:]=False;safe[:,:16]=False;safe[:,-16:]=False
 # Sticker bitmaps have a real tile join at native128. Never alter that guard.
 if kind=='sticker' and base.width>512:safe[:,496:528]=False
 g=np.array(gen.convert('RGB')).astype(float);blur=np.array(gen.convert('RGB').filter(ImageFilter.GaussianBlur(4))).astype(float);strength,limit=(.07,.45) if kind=='sticker' else (.18,1.4);delta=np.clip((g-blur)@np.array([.2126,.7152,.0722])*strength,-limit,limit);weight=np.array(Image.fromarray(safe.astype('uint8')*255).filter(ImageFilter.GaussianBlur(3))).astype(float)/255*safe
 if weight.sum():delta-=float((delta*weight).sum()/weight.sum())
 mod=lab.copy();mod[:,:,0]+=delta*weight;converted,_=lab_to_rgb(mod);out=a.copy();out[:,:,:3][safe]=converted[safe];assert np.array_equal(out[~safe],a[~safe]);assert np.array_equal(out[:,:,3],a[:,:,3]);diff=rgb_to_lab(out[:,:,:3])-lab
 return Image.fromarray(out),Image.fromarray(safe.astype('uint8')*255),dict(raw_size=list(raw.size),aspect_error=err,changed_pixels=int(np.any(out[:,:,:3]!=rgb,2).sum()),safe_pixels=int(safe.sum()),max_rgb_delta=int(abs(out[:,:,:3].astype(int)-rgb).max()),mean_safe_delta_Lab=diff[safe].mean(0).tolist() if safe.any() else [0,0,0],alpha_exact=True,protected_graphics_exact=True)
cardconfigs=[('venue-wear','67f3756e5540','Venue · right worn paper overlay',[34,32,208,196]),('venue-frame','c2599d14439c','Venue · left blank photo frame',[36,36,210,184]),('venue-card3','8b094269e171','Venue · third paper card',[32,35,211,178])]
for key,prefix,label,center in cardconfigs:
 a=next(x for x in srcs if x['id'].startswith(prefix));base=bases[a['key']];draft,mask,st=paper(base,p/(key+'-raw.png'),'card',center);drafts[a['key']]=draft;mask.save(p/(key+'-mask.png'));stats.append(dict(key=key,source_ids=[a['id']],**st));items.append(dict(key=key,label=label,source_ids=[a['id']],native_size=a['source_size'],method='Restrained source-protected paper detail',source_file=a['source_file'],faithful_file=key+'-faithful.png',draft_file=key+'-draft.png',raw_file=key+'-raw.png',mask_file=key+'-mask.png',placement='Isolated centered review only; animated native card and live photo remain separate.'));base.save(p/(key+'-faithful.png'));draft.save(p/(key+'-draft.png'))
for g in stickers:
 key=g['key'];w,h=g['native_size'];base=Image.new('RGBA',(w*4,h*4))
 for part in g['parts']:base.paste(bases[part['key']].crop((0,0,part['width']*4,h*4)),(part['x']*4,0))
 raw=Image.open(p/(key+'-raw.png')).convert('RGBA');err=abs(raw.width/raw.height-2)/2;assert err<.02;norm=raw.resize((1024,512),Image.Resampling.LANCZOS).crop(g['edit_crop']);tmp=p/(key+'-raw-crop.png');norm.save(tmp);draft,mask,st=paper(base,tmp,'sticker');st['raw_full_size']=list(raw.size);st['edit_crop']=g['edit_crop'];st['full_aspect_error']=err
 for part in g['parts']:
  b=np.array(bases[part['key']]);out=b.copy();segment=np.array(draft)[:,part['x']*4:(part['x']+part['width'])*4];out[:h*4,:part['width']*4]=segment;guard=np.ones(out.shape[:2],bool);guard[16:-16,16:-16]=False;out[guard]=b[guard];assert np.array_equal(out[:,:,3],b[:,:,3]);assert np.array_equal(out[h*4:],b[h*4:]);assert np.array_equal(out[:,part['width']*4:],b[:,part['width']*4:]);drafts[part['key']]=Image.fromarray(out)
 # Review mosaic MUST be reconstructed from actual full-tile candidates after guards.
 actual=Image.new('RGBA',base.size)
 for part in g['parts']:actual.paste(drafts[part['key']].crop((0,0,part['width']*4,h*4)),(part['x']*4,0))
 a=np.array(actual);b=np.array(base);assert np.array_equal(a[:,:,3],b[:,:,3]);assert np.array_equal(a[~(np.array(mask)>0)],b[~(np.array(mask)>0)]);st['changed_pixels_after_tile_guards']=int(np.any(a[:,:,:3]!=b[:,:,:3],2).sum());base.save(p/(key+'-faithful.png'));actual.save(p/(key+'-draft.png'));mask.save(p/(key+'-mask.png'));stats.append(dict(key=key,source_ids=[x['source_id'] for x in g['parts']],**st));items.append(dict(key=key,label='Start · '+g['label'],source_ids=[x['source_id'] for x in g['parts']],native_size=g['native_size'],method='Restrained red-paper detail · lettering exact',source_file=key+'-source.png',faithful_file=key+'-faithful.png',draft_file=key+'-draft.png',raw_file=key+'-raw.png',mask_file=key+'-mask.png',shape=g['shape'],local_overhang_x=g['local_overhang_x'],placement='Isolated centered review only; actual platform/language transforms remain native.'))
for a in srcs:
 if '/support/' in a['source']:key='support-'+a['name'].strip();label={'11':'shield / crest','14':'fist','17':'lightning fist','20':'menu / screen','23':'record / deck','26':'warning triangle'}[a['name'].strip()];label='Support · '+label;method='Faithful HD · original ink paths and partial coverage retained';placement='Source library has no paired APT/object; centered review is illustrative.'
 elif a['name'].strip() in ['145','152']:key='venue-shadow-'+a['name'].strip();label='Venue · '+('right' if a['name'].strip()=='145' else 'left')+' shadow mask';method='Faithful HD · original black RGB and soft alpha retained';placement='Separate animated shadow, never scenery or an opaque fill.'
 elif a['name'].strip()=='16':key='title-radial';label='Title · radial effect';method='Faithful HD · original soft effect retained';placement='Native effect shape spans640×480; no new wide effect registration.'
 else:continue
 base=bases[a['key']];base.save(p/(key+'-faithful.png'));base.save(p/(key+'-draft.png'));items.append(dict(key=key,label=label,source_ids=[a['id']],native_size=a['source_size'],method=method,source_file=a['source_file'],faithful_file=key+'-faithful.png',draft_file=key+'-draft.png',placement=placement))
checks=[]
for a in srcs:
 key=a['key'];base=np.array(bases[key]);out=np.array(drafts[key]);assert np.array_equal(out[:,:,3],base[:,:,3]);guard=np.ones(out.shape[:2],bool);guard[16:-16,16:-16]=False;assert np.array_equal(out[guard],base[guard]);f=p/(key+'-draft.png');drafts[key].save(f);checks.append(dict(source_id=a['id'],source_file=a['source_file'],draft=f.name,native_size=a['source_size'],scale=4,alpha_exact=True,edge_guard_exact=True,sha256=sha(f)))
# Do not stretch isolated graphics as the viewport widens; retain native authored pixel size.
ratios={'4x3':960,'16x10':1152,'16x9':1280,'21x9':1680,'32x9':2560};placements=[]
for item in items:
 key=item['key'];orig=Image.open(p/item['source_file']).convert('RGBA');draft=Image.open(p/item['draft_file']).convert('RGBA');faith=Image.open(p/item['faithful_file']).convert('RGBA');faith.getchannel('A').save(p/(key+'-source-alpha.png'));draft.getchannel('A').save(p/(key+'-draft-alpha.png'));size=tuple(round(v*1.5) for v in item['native_size']);orig=orig.resize(size,Image.Resampling.BILINEAR);draft=draft.resize(size,Image.Resampling.LANCZOS)
 for ratio,width in ratios.items():
  xy=((width-size[0])//2,(720-size[1])//2);o=Image.new('RGBA',(width,720));d=Image.new('RGBA',o.size);o.paste(orig,xy);d.paste(draft,xy);o.save(p/f'{key}-{ratio}-original.png');d.save(p/f'{key}-{ratio}-draft.png');assert np.array_equal(np.array(d)[xy[1]:xy[1]+size[1],xy[0]:xy[0]+size[0]],np.array(draft));placements.append(dict(key=key,ratio=ratio,device_or_graphic_size_exact=True,isolated_center_exact=True,not_runtime_placement=True))
 item['alpha_reference_file']=key+'-source-alpha.png';item['alpha_draft_file']=key+'-draft-alpha.png'
assert len(items)==16;assert len(checks)==19;assert len({i for it in items for i in it['source_ids']})==19
(p/'review-items.json').write_text(json.dumps(items,indent=2)+'\n');(p/'references.json').write_text(json.dumps(dict(sources=srcs,sticker_groups=stickers,source_tiles=checks,items=items,placement_policy='All16isolatedcenteredstudiesaregeometry-neutralreviewonly,notgamecaptures. ExactAPT/movieplacementisinaudit;supporthasnopairedbounds.',scope='17originalshortlistIDsplus2provenvenuecard/shadowcompanions;all19newcandidatesUNAPPROVED.'),indent=2)+'\n');cat=json.loads((repo/'config/menu-ui-approved-artwork.json').read_text());pins={x['path']:x['sha256'] for s in cat['approval_records'] for x in s['files']};assert len(pins)==343 and all(sha(r/n)==h for n,h in pins.items());before=json.loads((p/'before-hashes.json').read_text());assert all(sha(r/n)==h for n,h in before.items())
(p/'assembly-receipt.json').write_text(json.dumps(dict(processor_sha256=sha(Path(__file__)),restored_items=7,faithful_only_items=9,restoration_statistics=stats,source_tiles=checks,aspect_studies=placements,recipe='Tileaware4xLanczos;sourceLabchroma/broadlight,Gaussian4finebrightness:paper*.18clip1.4/sticker*.07clip.45meanremoved;alphaerosion9/edgeexclusion13;16HDpx tileguards;explicitcardinset/redpaperonlymasks;allglyphsandtruealphaexact.',rejected_proposals=['support-shield:inventeddotgrain','support-fist:inventedhalftone'],all_unapproved=True),indent=2)+'\n');(p/'verification.json').write_text(json.dumps(dict(approved_conditional_pins_exact=343,prior_pngs_exact=len(before),source_tiles=19,review_items=16,restored_items=7,faithful_only_items=9,alpha_graphics_tileguards_padding_exact=True,isolated_aspect_pairs=80,new_builtin_calls=9,historical_total=127,all_batch_art_unapproved=True,game_untouched=True),indent=2)+'\n');print('16items/19sources:7restrainedpapers+9Faithfulgraphics/effects;80aspectpairs,343pins and'+str(len(before))+'priorPNGs exact')
# Compact contact sheet on neutral gray; actual transparent PNGs stay separate.
board=Image.new('RGB',(1200,4*350),(65,65,65));draw=ImageDraw.Draw(board)
for i,item in enumerate(items):
 im=Image.open(p/item['draft_file']).convert('RGBA');im.thumbnail((280,280));x=(i%4)*300;y=(i//4)*350;board.paste(im,(x+(300-im.width)//2,y+35),im);draw.text((x+6,y+5),item['label'],fill='white');draw.text((x+6,y+320),('Restored paper' if item.get('raw_file') else 'Faithful HD'),fill='white')
board.save(p/'batch-overview.png')
