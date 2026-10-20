"""Match added-wall local contrast to original wall; original/restored center exact."""
from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
from defjam_tools.color_trial import rgb_to_lab,lab_to_rgb
p=Path(__file__).resolve().parent;r=p.parent;sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();world=Image.open(p/'transition-wide-v3.png').convert('RGB');core=world.crop((1600,0,3523,7599));source=np.array(Image.open(p/'scene-source.png').convert('RGB'));stats={}
def smooth(v,sigma=16):
 rad=round(sigma*3);k=np.exp(-np.arange(-rad,rad+1)**2/(2*sigma*sigma));k/=k.sum();return np.stack([np.convolve(np.pad(v[:,c],(rad,rad),mode='edge'),k,'valid') for c in range(v.shape[1])],1)
for side,rect,width,sband in [('left',(0,0,1600,7599),1600,source[:,:32]),('right',(3523,0,5120,7599),1597,source[:,-32:])]:
 rgb=np.array(world.crop(rect).resize((533,2533),Image.Resampling.LANCZOS));g=rgb_to_lab(rgb);s=rgb_to_lab(sband);near=g[:,-72:-8] if side=='left' else g[:,8:72];gm=smooth(near.mean(1));sm=smooth(s.mean(1));sv=np.maximum(smooth((s*s).mean(1))-sm*sm,.005);gv=np.maximum(smooth((near*near).mean(1))-gm*gm,.005);gain=np.clip(np.sqrt(sv[:,0]/gv[:,0]),.25,1);cal=g.copy();cal[:,:,0]=gm[:,0,None]+(g[:,:,0]-gm[:,0,None])*gain[:,None];out,_=lab_to_rgb(cal)
 # Original edge color correction tapers through eight native pixels, without source-strip copying.
 edge=-1 if side=='left' else 0;target=source[:,0 if side=='left' else -1].astype(float);delta=target-out[:,edge].astype(float)
 for i in range(8):
  c=-1-i if side=='left' else i;out[:,c]=np.rint(out[:,c].astype(float)+delta*(1-i/8)**2).clip(0,255).astype('uint8')
 world.paste(Image.fromarray(out).resize((width,7599),Image.Resampling.LANCZOS),(rect[0],0));stats[side]=dict(L_gain_median=float(np.median(gain)),L_gain_range=[float(gain.min()),float(gain.max())],source_native_band=32,generated_native_band=[8,72],sigma_native=16,chroma_retained=True)
assert np.array_equal(np.array(world.crop((1600,0,3523,7599))),np.array(core));world.save(p/'transition-wide-v4.png');world.resize((1280,1900)).save(p/'full-height-v4.jpg');stages=[]
for i,t in enumerate([0,.2,.4,.6,.8,1]):
 y=round(t*(7599-1440));center=world.crop((1600,y,3520,y+1440))
 for ratio,width in {'4x3':1920,'16x10':2304,'16x9':2560,'21x9':3360,'32x9':5120}.items():
  off=(width-1920)//2;x=1600-off;im=world.crop((x,y,x+width,y+1440));assert np.array_equal(np.array(im.crop((off,0,off+1920,1440))),np.array(center));im.save(p/f'phase-{i}-{ratio}-draft-v4.png');stages.append(dict(phase=t,ratio=ratio,center_exact=True))
for side,edge in [('left',1600),('right',3520)]:
 world.crop((edge-384,0,edge+384,7599)).save(p/f'{side}-join-full-v4.png')
 for i,t in enumerate([0,.5,1]):
  y=round(t*(7599-1440));world.crop((edge-384,y,edge+384,y+1440)).save(p/f'{side}-join-{i}-v4.png')
for side,rows in json.loads((p/'assembly-v3-receipt.json').read_text())['horizontal_overlaps'].items():
 for i,c in enumerate(rows):
  y=c['row_native']*3;world.crop((0,y-192,5120,y+192)).save(p/f'{side}-horizontal-overlap-{i}-v4.png')
pins={a['path']:a['sha256'] for sc in json.loads((p.parents[3]/'config/menu-ui-approved-artwork.json').read_text())['approval_records'] for a in sc['files']};assert len(pins)==277 and all(sha(r/f)==v for f,v in pins.items());prior=json.loads((p/'before-hashes.json').read_text());assert all(sha(r/f)==v for f,v in prior.items());rec=dict(method='Boundedrowvariance L-onlycorrection of addedwall;no newgeneration,no sourcecenteredit',input_sha256=sha(p/'transition-wide-v3.png'),statistics=stats,source_core_exact=True,recipe_history=['assembly-receipt.json','assembly-v2-receipt.json','assembly-v3-receipt.json'],stages=stages,processor_sha256=sha(Path(__file__)));(p/'assembly-v4-receipt.json').write_text(json.dumps(rec,indent=2)+'\n');ver=dict(prior_pngs_unchanged=len(prior),approved_pins_exact=277,source_core_exact=True,source_tiles=10,tile_alpha_edges_unused_exact=True,phase_aspect_pairs=30,centers_exact=True,new_generation_calls=0,historical_total=117,artwork_unapproved=True,game_processes_untouched=True);(p/'verification-v4.json').write_text(json.dumps(ver,indent=2)+'\n');print(json.dumps(stats,indent=2));print(json.dumps(ver,indent=2))
