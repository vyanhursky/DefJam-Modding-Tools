"""Assemble candidate side outpaints around unchanged Faithful scene cores; never adopt AI core pixels."""
from pathlib import Path
from PIL import Image,ImageFilter,ImageDraw
import numpy as np,json,csv,hashlib
from defjam_tools.color_trial import rgb_to_lab,lab_to_rgb
p=Path('logs/ui-restoration-20261017/pilot-v1/wide-backgrounds-v1-20261020');corpus=Path('/Users/vlad/Library/Application Support/DefJamPR19-20/data/hd-work/setup-lanczos/b9aa783f1d66d41be59fb97ba25fb86e1e9f73d8ee041263b0ff5df85ceb26f0');rows={x['id']:x for x in csv.DictReader(Path('logs/ui-restoration-20261017/all-menu-texture-aliases.csv').open())};groups=json.loads((p/'groups.json').read_text());receipt=[];widths={'4x3':1920,'16x10':2304,'16x9':2560,'21x9':3360,'32x9':5120}
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
def smooth(a,sigma=12):
 lo=a.min(0);span=np.maximum(a.max(0)-lo,1e-6);v=np.round((a-lo)/span*255).clip(0,255).astype('uint8');im=Image.fromarray(np.repeat(v[:,None,:],3,axis=1)).filter(ImageFilter.GaussianBlur(sigma));return np.array(im)[:,1]/255*span+lo
for g in groups:
 key=g['key'];core=Image.new('RGBA',(1920,1440));original=Image.new('RGBA',(1920,1440));parts=g['parts']
 if key=='cribOptions':parts=[x for x in parts if x['id']!='1c2de449c28536a5491ef5828f81d171544917f2238a18c8a1474ea8685edbae']
 for part in parts:
  box=part['crop'];xy=tuple(v*3 for v in part['xy'][:2]);size=((box[2]-box[0])*3,(box[3]-box[1])*3)
  for mode,dest,scale in [('faithful',core,4),('original',original,1)]:
   tile=Image.open(corpus/rows[part['id']][mode]).convert('RGBA').crop(tuple(v*scale for v in box)).resize(size,Image.Resampling.LANCZOS if mode=='faithful' else Image.Resampling.NEAREST);dest.paste(tile,xy)
 core.save(p/f'{key}-core-hd.png');original.save(p/f'{key}-core-original-hd.png');master=Image.new('RGBA',(5120,1440));master.paste(core,(1600,0));checks=[]
 for side in g['sides']:
  rawfile=p/f'{key}-{side}-raw.png';raw=Image.open(rawfile).convert('RGB');assert abs(raw.width/raw.height-790/480)/(790/480)<.025,(key,raw.size)
  native=raw.resize((790,480),Image.Resampling.LANCZOS);a=np.array(native);nl=rgb_to_lab(a);target=np.array(Image.open(p/f'{key}-{side}-target.png').convert('RGB'));tl=rgb_to_lab(target);cx=slice(534,790) if side=='left' else slice(0,256);sx=slice(0,534) if side=='left' else slice(256,790)
  # Fixed-context difference supplies a bounded, source-derived white-balance/exposure correction.
  delta=smooth((tl[:,cx]-nl[:,cx]).mean(1));delta=np.clip(delta,[-8,-6,-6],[8,6,6]);ext=nl[:,sx].copy();ext+=delta[:,None,:]
  rgb,_=lab_to_rgb(ext);sideim=Image.fromarray(rgb).resize((1602,1440),Image.Resampling.LANCZOS);master.paste(sideim,(-2,0) if side=='left' else (3520,0))
  checks.append(dict(side=side,raw_size=list(raw.size),raw_sha256=sha(rawfile),context_mean_Lab_correction=np.median(delta,axis=0).tolist(),core_pixels_adopted=0))
 # Exact source core is last: AI never alters 4:3, alpha, text or existing scene detail.
 master.paste(core,(1600,0));master.save(p/f'{key}-wide-v1.png')
 stages=[]
 for aspect,w in widths.items():
  left=(5120-w)//2;draft=master.crop((left,0,left+w,1440));draft.save(p/f'{key}-{aspect}-draft.png')
  assert np.array_equal(np.array(draft)[:,(w-1920)//2:(w+1920)//2],np.array(core)),(key,aspect)
  for mode,img in [('faithful',core),('original',original)]:
   base=Image.new('RGBA',(w,1440));base.paste(img,((w-1920)//2,0));base.save(p/f'{key}-{aspect}-{mode}.png')
  stages.append(dict(aspect=aspect,width=w,center_exact=True))
 for side,x in [('left',1600),('right',3520)]:master.crop((x-384,0,x+384,1440)).save(p/f'{key}-{side}-join.png')
 receipt.append(dict(key=key,label=g['label'],source_ids=[x['id'] for x in parts],status='UNAPPROVED_ARTWORK; OFFLINE_GEOMETRY_ONLY',master=f'{key}-wide-v1.png',master_sha256=sha(p/f'{key}-wide-v1.png'),source_core_sha256=sha(p/f'{key}-core-hd.png'),sides=checks,stages=stages))
board=Image.new('RGB',(1400,1150),'#222');d=ImageDraw.Draw(board)
for i,g in enumerate(groups):
 im=Image.open(p/f'{g["key"]}-wide-v1.png');im.thumbnail((680,190));x=i%2*700;y=i//2*280;board.paste(im,(x,y+30),im);d.text((x,y),g['label'],fill='white')
board.save(p/'draft-overview.png');(p/'assembly-receipt.json').write_text(json.dumps(dict(schema=1,status='draft; not approved or installed',new_builtin_calls=13,historical_builtin_calls=160,processor_sha256=sha(Path(__file__)),source_center_exact_all_35=True,scenes=receipt),indent=2)+'\n');print('7 scenes,35 aspect previews,35 exact cores; UNAPPROVED/uninstalled')
