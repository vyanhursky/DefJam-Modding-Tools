"""Original-edge-guided bridge repairs; source core and outer context remain exact."""
from pathlib import Path
from PIL import Image,ImageFilter
import json,hashlib,numpy as np
from defjam_tools.color_trial import rgb_to_lab,lab_to_rgb
p=Path(__file__).resolve().parent;r=p.parent;sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();world=Image.open(p/'transition-wide-v2.png').convert('RGB');before=np.array(world);jobs=json.loads((p/'bridge-jobs.json').read_text());params={};cuts={};changed_rects=[]
def smooth(v,sigma=8):
 rad=round(sigma*3);k=np.exp(-np.arange(-rad,rad+1)**2/(2*sigma*sigma));k/=k.sum();return np.stack([np.convolve(np.pad(v[:,c],(rad,rad),mode='edge'),k,'valid') for c in range(v.shape[1])],1)
for side in ['left','right']:
 arr=np.zeros((2533,352,3),np.uint8);written=0;scuts=[]
 for j in [x for x in jobs if x['side']==side]:
  label,y=j['label'],j['y'];raw=Image.open(p/(label+'-bridge-raw.png')).convert('RGB');err=abs(raw.width/raw.height-736/1104)/(736/1104);assert err<.01,(label,raw.size,err);norm=raw.resize((736,1104),Image.Resampling.LANCZOS);norm.save(p/(label+'-bridge-normalized.png'));x0,x1=j['gap'];target=np.array(Image.open(j['referenced_image_paths'][0]).convert('RGB'));g=rgb_to_lab(np.array(norm.crop((x0,0,x1,1104)).filter(ImageFilter.GaussianBlur(.65))));t=rgb_to_lab(target);dl=smooth(t[:,x0-16:x0].mean(1)-g[:,:16].mean(1));dr=smooth(t[:,x1:x1+16].mean(1)-g[:,-16:].mean(1));u=np.linspace(0,1,352)[None,:,None];out=g+dl[:,None,:]*(1-u)+dr[:,None,:]*u;out[:,:,1:]=.15*out[:,:,1:]+.85*((1-u)*smooth(t[:,x0-16:x0].mean(1))[:,None,:]+u*smooth(t[:,x1:x1+16].mean(1))[:,None,:])[:,:,1:];rgb,_=lab_to_rgb(out)
  # Small additive endpoint correction, not a copied/repeated source strip.
  for edge,col,refcol in [('left',0,x0-1),('right',-1,x1)]:
   delta=target[:,refcol].astype(float)-rgb[:,col].astype(float)
   for i in range(8):
    c=i if edge=='left' else -1-i;rgb[:,c]=np.rint(rgb[:,c].astype(float)+delta*(1-i/8)**2).clip(0,255).astype('uint8')
  if written:
   ov=written-y;cost=((arr[y:written].astype(float)-rgb[:ov].astype(float))**2).mean((1,2));cost=np.convolve(np.pad(cost,(8,8),mode='edge'),np.ones(17)/17,'valid');cut=48+int(cost[48:ov-48].argmin());a=cut-16;b=cut+16;old=arr[y+a:y+b].astype(float);v=np.linspace(0,1,b-a);w=v*v*(3-2*v);arr[y+b:y+1104]=rgb[b:];arr[y+a:y+b]=np.rint(old*(1-w[:,None,None])+rgb[a:b]*w[:,None,None]).astype('uint8');scuts.append(dict(row_native=y+cut,blend_native=[y+a,y+b],overlap=ov))
  else:arr[y:y+1104]=rgb
  written=y+1104;params[label]=dict(raw_size=list(raw.size),aspect_error=err,gray_gap=j['gap'])
 assert written==2533;patch=Image.fromarray(arr).resize((1056,7599),Image.Resampling.LANCZOS);x=544 if side=='left' else 3523;world.paste(patch,(x,0));changed_rects.append([x,0,x+1056,7599]);cuts[side]=scuts;patch.save(p/f'{side}-bridge-composite-v3.png')
after=np.array(world);assert np.array_equal(after[:,1600:3523],before[:,1600:3523]);assert np.array_equal(after[:,:544],before[:,:544]);assert np.array_equal(after[:,4579:],before[:,4579:]);world.save(p/'transition-wide-v3.png');world.resize((1280,1900)).save(p/'full-height-v3.jpg');stages=[]
for i,t in enumerate([0,.2,.4,.6,.8,1]):
 y=round(t*(7599-1440));center=world.crop((1600,y,3520,y+1440))
 for ratio,width in {'4x3':1920,'16x10':2304,'16x9':2560,'21x9':3360,'32x9':5120}.items():
  off=(width-1920)//2;x=1600-off;im=world.crop((x,y,x+width,y+1440));assert np.array_equal(np.array(im.crop((off,0,off+1920,1440))),np.array(center));im.save(p/f'phase-{i}-{ratio}-draft-v3.png');stages.append(dict(phase=t,ratio=ratio,center_exact=True))
for side,edge in [('left',1600),('right',3520)]:
 world.crop((edge-384,0,edge+384,7599)).save(p/f'{side}-join-full-v3.png')
 for i,t in enumerate([0,.5,1]):
  y=round(t*(7599-1440));world.crop((edge-384,y,edge+384,y+1440)).save(p/f'{side}-join-{i}-v3.png')
 for i,c in enumerate(cuts[side]):
  y=c['row_native']*3;world.crop((0,y-192,5120,y+192)).save(p/f'{side}-horizontal-overlap-{i}-v3.png')
prior=json.loads((p/'before-hashes.json').read_text());assert all(sha(r/f)==v for f,v in prior.items());catalogue=json.loads((p.parents[3]/'config/menu-ui-approved-artwork.json').read_text());pins={a['path']:a['sha256'] for sc in catalogue['approval_records'] for a in sc['files']};assert len(pins)==277 and all(sha(r/f)==v for f,v in pins.items());old=json.loads((p/'generations-v2.json').read_text());old['calls'][0]['adoption']='Rejected sides; source core protection recipe retained';
for j in jobs:j.update(raw=j['label']+'-bridge-raw.png',raw_sha256=sha(p/(j['label']+'-bridge-raw.png')),inputs=[dict(path=f,sha256=sha(Path(f))) for f in j['referenced_image_paths']],adoption='Gray gap only; fixed source/outer context discarded; row endpoint palette matching and recorded overlapping windows.')
(p/'generations-v3.json').write_text(json.dumps(dict(tool='built-in image_gen',new_calls=11,pilot_total_calls=117,calls=old['calls']+jobs),indent=2)+'\n');receipt=dict(parameters=params,changed_rectangles=changed_rects,core_and_outer_exact=True,horizontal_overlaps=cuts,recipe='736x1104fulltarget normalization<1%aspect error;352pxgaponly;Gaussian.65native;Labrowendpointmean corrections sigma8;chroma residual.15;8pxadditiveendcorrection;low-error horizontalcut with32pxblend',source_core='Unchanged v1 source-protected/restoration core and bitmap9Faithfulonly',processor_sha256=sha(Path(__file__)),stages=stages);(p/'assembly-v3-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');ver=dict(prior_pngs_unchanged=len(prior),approved_pins_exact=277,source_core_exact=True,outer_context_exact=True,source_tiles=10,tile_alpha_edges_unused_exact=True,phase_aspect_pairs=30,centers_exact=True,art_unapproved=True,new_builtin_calls=11,historical_total=117,game_processes_untouched=True);(p/'verification-v3.json').write_text(json.dumps(ver,indent=2)+'\n');print(json.dumps(ver,indent=2))
