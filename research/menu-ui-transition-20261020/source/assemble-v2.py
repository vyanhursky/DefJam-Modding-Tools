"""Source-material retry sides, narrow low-error overlap transitions; fixed source center."""
from pathlib import Path
from PIL import Image,ImageFilter
import numpy as np,json,hashlib
from defjam_tools.color_trial import rgb_to_lab,lab_to_rgb
p=Path(__file__).resolve().parent;r=p.parent;sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();source=np.array(Image.open(p/'scene-source.png').convert('RGB'));world=Image.new('RGB',(5120,7599));core=Image.open(p/'scene-restored-3x.png').convert('RGB');world.paste(core,(1600,0));jobs=json.loads((p/'retry-jobs.json').read_text());parameters={};cutoffs={}
def smooth(v,sigma=16):
 rad=round(sigma*3);k=np.exp(-np.arange(-rad,rad+1)**2/(2*sigma*sigma));k/=k.sum();return np.stack([np.convolve(np.pad(v[:,c],(rad,rad),mode='edge'),k,'valid') for c in range(v.shape[1])],1)
for side,box,width,band in [('left',(0,0,533,1100),1600,source[:,:48]),('right',(1174,0,1707,1100),1597,source[:,-48:])]:
 combined=np.zeros((2533,533,3),np.uint8);written=0;cuts=[]
 for j in jobs:
  label,y=j['label'],j['y'];raw=Image.open(p/(label+'-retry-raw.png')).convert('RGB');err=abs(raw.width/raw.height-1707/1100)/(1707/1100);assert err<(.08 if label=='upper' else .01),(label,err);cropbox=None
  if label=='upper' and err>=.01:
   cw=raw.height*1707/1100;cx=(raw.width-cw)/2;cropbox=[cx,0,cx+cw,raw.height];norm=raw.resize((1707,1100),Image.Resampling.LANCZOS,box=tuple(cropbox))  # Uniform cover/crop; pure side wall only, no stair geometry adopted.
  else:norm=raw.resize((1707,1100),Image.Resampling.LANCZOS)
  norm.save(p/(label+'-retry-normalized.png'));gen=norm.crop(box).filter(ImageFilter.GaussianBlur(.9));g=rgb_to_lab(np.array(gen));s=rgb_to_lab(band[y:y+1100]);near=g[:,-96:] if side=='left' else g[:,:96];gm=smooth(near.mean(1));sm=smooth(s.mean(1));gs=np.sqrt(np.maximum(smooth((near*near).mean(1))-gm*gm,.01));ss=np.sqrt(np.maximum(smooth((s*s).mean(1))-sm*sm,.01));gain=np.clip(ss/gs,.7,1.3);cal=(g-gm[:,None,:])*gain[:,None,:];cal[:,:,1:]*=.15;cal+=sm[:,None,:];rgb,_=lab_to_rgb(cal);edge=-1 if side=='left' else 0;target=source[y:y+1100,0 if side=='left' else -1].astype(float);delta=target-rgb[:,edge].astype(float)
  for i in range(8):
   col=-1-i if side=='left' else i;rgb[:,col]=np.rint(rgb[:,col].astype(float)+delta*(1-i/8)**2).clip(0,255).astype('uint8')
  if written:
   overlap=written-y;cost=((combined[y:written].astype(float)-rgb[:overlap].astype(float))**2).mean((1,2));cost=np.convolve(np.pad(cost,(8,8),mode='edge'),np.ones(17)/17,'valid');cut=32+int(cost[32:overlap-32].argmin());a=max(0,cut-16);b=min(overlap,cut+16);old=combined[y+a:y+b].copy().astype(float);t=np.linspace(0,1,b-a);weight=t*t*(3-2*t);combined[y+b:y+1100]=rgb[b:];combined[y+a:y+b]=np.rint(old*(1-weight[:,None,None])+rgb[a:b]*weight[:,None,None]).astype('uint8');cuts.append(dict(label=label,overlap_native=overlap,chosen_row_native=y+cut,blend_native=[y+a,y+b],minimum_mean_squared_rgb=float(cost[cut])))
  else:combined[y:y+1100]=rgb
  written=y+1100
  parameters[label]=dict(raw_size=list(raw.size),aspect_error=err,uniform_material_crop_box=cropbox)
 assert written==2533;im=Image.fromarray(combined).resize((width,7599),Image.Resampling.LANCZOS);im.save(p/f'{side}-calibrated-v2.png');world.paste(im,(0 if side=='left' else 3523,0));cutoffs[side]=cuts
assert np.array_equal(np.array(world.crop((1600,0,3523,7599))),np.array(core));world.save(p/'transition-wide-v2.png');original=Image.open(p/'scene-source.png').resize((1923,7599),Image.Resampling.BILINEAR).convert('RGB');ref=Image.new('RGB',world.size);ref.paste(original,(1600,0));ref.save(p/'original-wide-reference.png');stages=[]
for i,t in enumerate([0,.2,.4,.6,.8,1]):
 y=round(t*(7599-1440));center=world.crop((1600,y,3520,y+1440))
 for ratio,width in {'4x3':1920,'16x10':2304,'16x9':2560,'21x9':3360,'32x9':5120}.items():
  off=(width-1920)//2;x=1600-off;im=world.crop((x,y,x+width,y+1440));assert np.array_equal(np.array(im.crop((off,0,off+1920,1440))),np.array(center));im.save(p/f'phase-{i}-{ratio}-draft-v2.png');stages.append(dict(phase=t,ratio=ratio,crop=[x,y,width,1440],center_exact=True))
for side,edge in [('left',1600),('right',3520)]:
 world.crop((edge-384,0,edge+384,7599)).save(p/f'{side}-join-full-v2.png')
 for i,t in enumerate([0,.5,1]):
  y=round(t*(7599-1440));world.crop((edge-384,y,edge+384,y+1440)).save(p/f'{side}-join-{i}-v2.png')
 for i,c in enumerate(cutoffs[side]):
  y=c['chosen_row_native']*3;world.crop((0,y-192,5120,y+192)).save(p/f'{side}-horizontal-overlap-{i}-v2.png')
world.resize((1280,1900)).save(p/'full-height-v2.jpg');old=json.loads((p/'generations.json').read_text());old['calls'][0]['adoption']='Rejected wide sides: coarse brick material and sharpness mismatch. Center detail-only restoration retained;geometry/colors source protected.'
rejected=dict(jobs[0]);rejected.update(raw='upper-rejected-aspect-raw.png',raw_sha256=sha(p/'upper-rejected-aspect-raw.png'),adoption='Rejected for7.51%aspect/framingdrift;notused');newupper=json.loads((p/'upper-framing-retry-job.json').read_text());jobs[0].update(newupper)
for j in jobs:
 j.update(raw=j['label']+'-retry-raw.png',raw_sha256=sha(p/(j['label']+'-retry-raw.png')),inputs=[dict(path=f,sha256=sha(Path(f))) for f in j['referenced_image_paths']],adoption='Side pixels only; source material/color/focus matching; center discarded; explicit low-error horizontal overlaps.')
(p/'generations-v2.json').write_text(json.dumps(dict(tool='built-in image_gen',new_calls=5,pilot_total_calls=111,calls=old['calls']+[rejected]+jobs),indent=2)+'\n');pins={f['path']:f['sha256'] for sc in json.loads((p.parents[3]/'config/menu-ui-approved-artwork.json').read_text())['approval_records'] for f in sc['files']};assert len(pins)==277 and all(sha(r/f)==v for f,v in pins.items());before=json.loads((p/'before-hashes.json').read_text());assert all(sha(r/f)==v for f,v in before.items());receipt=dict(wide_size=list(world.size),source_core_exact=True,source_protected_rectangle=[1600,0,3523,7599],inputs=parameters,horizontal_overlaps=cutoffs,normalization='Middle/lowernormalized1707x1100withaspecterror<1%;upper7.45%aspectdrift uses uniform cover/center crop of pure wall material only. Generated center/structures discarded; no per-axis stretch.',color='Labrowmean16native/48pxsourceband/96pxgeneratedband,gain.7..1.3,chroma residual.15,Gaussian.9native,8pxadditiveedgecondition',horizontal_recipe='Minimum17-row-smoothedMSEinside32pxoverlapguards,32nativepxsmoothstepblend;no repeatedsource strips',stages=stages,source_tiles_receipt='assembly-receipt.json',processor_sha256=sha(Path(__file__)),runtime_coverage='Artworkstudyonly;nativebitmap9geometryexceptionandlivepanvalidationstillpending');(p/'assembly-v2-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');ver=dict(approved_conditional_pins_exact=277,prior_pngs_unchanged=len(before),source_center_exact=True,phase_aspect_pairs=30,centers_exact=True,source_tile_protections='10alpha/UV/tileguards verified byv1assembly;allremainunchanged',new_builtin_calls=5,historical_calls=111,artwork_unapproved=True,game_processes_untouched=True);(p/'verification-v2.json').write_text(json.dumps(ver,indent=2)+'\n');print(json.dumps(ver,indent=2));print(json.dumps(cutoffs,indent=2))
