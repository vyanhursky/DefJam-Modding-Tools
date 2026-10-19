"""Shared source-registered panorama; native alpha preserved, wide vignette moved."""
from pathlib import Path
from PIL import Image,ImageFilter
import numpy as np,json,hashlib
from defjam_tools.color_trial import rgb_to_lab,lab_to_rgb
p=Path(__file__).resolve().parent;r=p.parent;sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();core=np.array(Image.open(p/'wall-interior.png').convert('RGB'));world=np.zeros((1440,5256,3),dtype='uint8');world[:,1656:3513]=core
params={}
def prof(v):
 k=np.exp(-np.arange(-192,193,dtype=float)**2/(2*64**2));k/=k.sum();return np.stack([np.convolve(np.pad(v[:,c],(192,192),mode='edge'),k,'valid') for c in range(v.shape[1])],1)
for side,width,crop,srcband,genband in [('left',2040,(0,0,1656,1440),core[:,:192],slice(-384,None)),('right',2127,(384,0,2127,1440),core[:,-192:],slice(0,384))]:
 raw=Image.open(p/f'{side}-raw.png').convert('RGB');assert abs(raw.width/raw.height-width/1440)<.009;im=raw.resize((width,1440),Image.Resampling.LANCZOS);im.save(p/f'{side}-normalized.png');im=im.crop(crop);im=im.resize((round(im.width/3),480),Image.Resampling.LANCZOS).resize(im.size,Image.Resampling.LANCZOS);g=rgb_to_lab(np.array(im));s=rgb_to_lab(srcband);gb=g[:,genband];sm=prof(s.mean(1));gm=prof(gb.mean(1));sv=np.maximum(prof((s*s).mean(1))-sm*sm,.01);gv=np.maximum(prof((gb*gb).mean(1))-gm*gm,.01);gain=np.clip(np.sqrt(sv/gv),.6,1.4);out=(g-gm[:,None,:])*gain[:,None,:]+sm[:,None,:];rgb,_=lab_to_rgb(out)
 # Last24px blend only a small color residual into fixed edge; no source strip copied.
 edge=-1 if side=='left' else 0;target=core[:,0 if side=='left' else -1].astype(float);delta=target-rgb[:,edge].astype(float)
 for i in range(24):
  x=-1-i if side=='left' else i;rgb[:,x]=np.rint(rgb[:,x].astype(float)+delta*(1-i/24)**2).clip(0,255).astype('uint8')
 if side=='left':world[:,:1656]=rgb
 else:world[:,3513:]=rgb
 params[side]=dict(native_density=True,source_band_width=192,generated_band_width=384,profile_sigma=64,gain_clip=[.6,1.4],additive_edge_pixels=24)
Image.fromarray(world).save(p/'rewards-world-before-bridges.png')
for side,edge in [('left',1656),('right',3513)]:
 raw=Image.open(p/f'{side}-bridge-raw.png').convert('RGB');assert abs(raw.width/raw.height-512/1440)<.006;im=raw.resize((512,1440),Image.Resampling.LANCZOS);im.save(p/f'{side}-bridge-normalized.png');x0=edge-256 if side=='left' else edge;im=im.crop((0,0,256,1440) if side=='left' else (256,0,512,1440));im=im.resize((86,480),Image.Resampling.LANCZOS).resize((256,1440),Image.Resampling.LANCZOS);g=rgb_to_lab(np.array(im));old=world[:,x0:x0+256].copy();ref=rgb_to_lab(old);g+=prof(ref.mean(1)-g.mean(1))[:,None,:];new,_=lab_to_rgb(g);i=-1 if side=='left' else 0;target=core[:,0 if side=='left' else -1].astype(float);delta=target-new[:,i].astype(float)
 for j in range(16):
  col=-1-j if side=='left' else j;new[:,col]=np.rint(new[:,col].astype(float)+delta*(1-j/16)**2).clip(0,255).astype('uint8')
 t=np.clip(np.arange(256)/64,0,1);weight=t*t*(3-2*t)
 if side=='right':weight=weight[::-1]
 world[:,x0:x0+256]=np.rint(old*(1-weight[None,:,None])+new*weight[None,:,None]).astype('uint8')
 params[side]['bridge']=dict(domain=[x0,0,256,1440],native_density=True,source_half_discarded=True,row_color_sigma=64,outer_blend=64,edge_condition=16)
assert np.array_equal(world[:,1656:3513],core);master=Image.fromarray(world);master.save(p/'rewards-shared-world-v1.png')
source=Image.open(p/'wall-source.png').convert('RGBA').crop((0,0,699,480)).resize((2097,1440),Image.Resampling.BILINEAR);rest=Image.open(p/'wall-restrained.png').crop((0,0,2796,1920)).resize((2097,1440),Image.Resampling.LANCZOS)
sizes={'4x3':1920,'16x10':2304,'16x9':2560,'21x9':3360,'32x9':5120};layouts={'buyrewards':87,'unlockchar':151,'unlockven':151};rects={}
def overblack(im):bg=Image.new('RGBA',im.size,'black');bg.alpha_composite(im);return bg.convert('RGB')
for scene,offset in layouts.items():
 original=overblack(source.crop((offset,0,offset+1920,1440)));native=overblack(rest.crop((offset,0,offset+1920,1440)));original.save(p/f'{scene}-original-center.png');native.save(p/f'{scene}-restored-center.png');centerx=1536+offset;rects[scene]={}
 for ratio,w in sizes.items():
  ox=(w-1920)//2;reference=Image.new('RGB',(w,1440));reference.paste(original,(ox,0));reference.save(p/f'{scene}-{ratio}-original.png')
  x=centerx-ox
  if ratio=='4x3':draft=native
  else:
   arr=np.array(master.crop((x,0,x+w,1440))).astype(float);n=96;t=np.linspace(0,1,n);f=.204+.796*(t*t*(3-2*t));arr[:,:n]*=f[None,:,None];arr[:,-n:]*=f[None,::-1,None];draft=Image.fromarray(np.rint(arr).clip(0,255).astype('uint8'))
  draft.save(p/f'{scene}-{ratio}-draft.png');rects[scene][ratio]=[x,0,w,1440]
 # Surface comparisons cross geometry/trusted-core joins, not relocated native vignette.
 for side,edge in [('left',1656),('right',3513)]:master.crop((edge-384,0,edge+384,1440)).save(p/f'{scene}-{side}-join.png')
for side,x0,x1 in [('left',0,1656),('right',3513,5256)]:
 im=Image.new('RGBA',(5256,1440));im.paste(master.crop((x0,0,x1,1440)),(x0,0));im.save(p/f'rewards-{side}-extension.png')
# RGB/alpha/channel inspections retain original alpha, not black replacement.
Image.open(p/'wall-source.png').getchannel('A').resize((2796,2048),Image.Resampling.LANCZOS).save(p/'wall-faithful-alpha.png');alpha_before=np.array(Image.open(p/'wall-faithful.png'))[:,:,3];alpha_after=np.array(Image.open(p/'wall-restrained.png'))[:,:,3];assert np.array_equal(alpha_before,alpha_after)
(p/'wide-receipt.json').write_text(json.dumps(dict(world_size=[5256,1440],world_origin_native=-512,common_trusted_native=[40,0,619,480],core_exact=True,layouts_native=dict(buyrewards_crop=29,unlockchar_crop=50.4,unlockven_crop=50.4),unlock_rounding_native_px=-.0666667,crops=rects,material=params,coverage='4:3 keeps original baked/alpha vignette; widescreen replaces only peripheral native edge-fade areas with new coverage and moves96pxvignette to outside. Full4:3RGBAcenter equality is not claimed for wide studies. Trusted619x480interior RGB is exact.',separate_source_shaped_alpha_exact=True),indent=2)+'\n')
calls=[]
j=json.loads((p/'restoration-job.json').read_text());j.update(label='restoration',raw='restoration-raw.png',adoption='Source-aligned tiny L highpass only');calls.append(j)
j=json.loads((p/'side-jobs-first.json').read_text())[0];j.update(raw='left-rejected-full-reference-raw.png',adoption='Rejected: repeated full original instead of target extension');calls.append(j)
for j in json.loads((p/'side-jobs.json').read_text()):j.update(raw=j['label']+'-raw.png',adoption='Generated side only; native density/Lab material normalization/24pxedge conditioning');calls.append(j)
for j in json.loads((p/'bridge-jobs.json').read_text()):j.update(raw=j['label']+'-raw.png',adoption='Generated256px side only; native half discarded,source palette retained,64pxouterblend');calls.append(j)
for j in calls:j['raw_sha256']=sha(p/j['raw']);j['raw_size']=list(Image.open(p/j['raw']).size);j['inputs']=[dict(path=f,sha256=sha(Path(f))) for f in j['referenced_image_paths']]
(p/'generations.json').write_text(json.dumps(dict(tool='built-in image_gen',new_calls=6,pilot_total_calls=92,calls=calls),indent=2)+'\n')
prev=json.loads((p/'before-hashes.json').read_text());assert all(sha(r/f)==v for f,v in prev.items())
for approval in ['battle-fighter-approval-20261019.json','battle-setup-approval-20261019.json']:
 a=json.loads((r/approval).read_text());assert all(sha(r/f['path'])==f['sha256'] for f in a['files'])
(p/'verification.json').write_text(json.dumps(dict(prior_pngs_unchanged=len(prev),approved_battle_files_exact=52,shared_source_ids=2,screen_layouts=3,distinct_compositions=2,aspect_previews=15,trusted_interior_rgb_exact=True,source_shaped_alpha_exact=True,native4x3_vignette_retained=True,wide_vignette_relocated=True,full_wide_native_center_rgba_exact=False,new_builtin_calls=6,pilot_total_calls=92),indent=2)+'\n');print((p/'verification.json').read_text())
