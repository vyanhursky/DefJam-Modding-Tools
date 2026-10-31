"""Transfer broad illumination only onto v3 RGB; retain all geometry/detail."""
from pathlib import Path
from PIL import Image,ImageFilter
import numpy as np,json,hashlib
p=Path(__file__).resolve().parent;r=p.parent;sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
before=np.array(Image.open(r/'battle-left-v3/cmtype-wide-v3.png').convert('RGB'));a=before.copy();base=Image.open(p/'lighting-target.png').convert('RGB');raw=Image.open(p/'raw.png').convert('RGB');assert abs(raw.width/raw.height-1600/720)<.008;raw=raw.resize((1600,720),Image.Resampling.LANCZOS);raw.save(p/'normalized.png')
# Luminance-only edit preserves native cool RGB balance; no generated texture copied.
def lum(im):return np.asarray(im,dtype=float)@np.array([.2126,.7152,.0722])
def blur(im,sigma):return lum(im.filter(ImageFilter.GaussianBlur(sigma)))
orig=blur(base,32);proposed=blur(raw,32);proposal_gain=np.clip((proposed+2)/(orig+2),.85,1.15)
h,w=640,1600;yy=np.arange(h);xx=np.arange(w);smooth=lambda t:np.clip(t,0,1)**2*(3-2*np.clip(t,0,1))
vertical=1-smooth((yy-256)/384);horizontal=np.exp(-xx/480)*(1-smooth((xx-1120)/480));gain=np.ones((h,w));gain[:,:1120]+=(proposal_gain[:h,480:]-1)*(1-smooth((xx[:1120]-896)/224))[None,:]
# Reconcile source-edge shadow field, not source texture. Source24px vs generated24px
# adjacent bands: Gaussian12 row smoothing; exponential480px rollout.
source=lum(Image.fromarray(before[:h,3496:3520]).filter(ImageFilter.GaussianBlur(12))).mean(1)
new=lum(Image.fromarray(before[:h,3520:3544]).filter(ImageFilter.GaussianBlur(12))).mean(1)*gain[:,0]
edge_gain=np.clip((source+2)/(new+2),.55,1.5)
gain*=1+(edge_gain[:,None]-1)*horizontal[None,:];gain=1+(gain-1)*vertical[:,None]
a[:h,3520:]=np.rint(before[:h,3520:].astype(float)*gain[:,:,None]).clip(0,255).astype('uint8')
# The old extension also has a broad extra ceiling highlight farther beyond the join.
# Carry the native beam's row illumination across it; preserve its textured variation.
beam_source=lum(Image.fromarray(before[:256,3360:3520]).filter(ImageFilter.GaussianBlur(12))).mean(1)
beam_field=blur(Image.fromarray(a[:256,3520:]),48)
beam_gain=np.clip((beam_source[:,None]+2)/(beam_field+2),.6,1.4)
beam_weight=(1-smooth((np.arange(256)-128)/96))[:,None]*smooth(xx/96)[None,:]
a[:256,3520:]=np.rint(a[:256,3520:].astype(float)*(1+(beam_gain-1)*beam_weight)[:,:,None]).clip(0,255).astype('uint8')
assert np.array_equal(a[:,:3520],before[:,:3520]);assert np.array_equal(a[640:],before[640:]);master=Image.fromarray(a);master.save(p/'cmtype-wide-v4.png')
for ratio,width in {'4x3':1920,'16x10':2304,'16x9':2560,'21x9':3360,'32x9':5120}.items():
 x=(5120-width)//2;im=master.crop((x,0,x+width,1440));im.save(p/f'cmtype-{ratio}-v4.png');assert np.array_equal(np.array(im)[:,(width-1920)//2:(width+1920)//2],before[:,1600:3520])
for side,edge in [('left',1600),('right',3520)]:master.crop((edge-384,0,edge+384,1440)).save(p/f'cmtype-{side}-join.png')
for side,x0,x1 in [('left',0,1600),('right',3520,5120)]:
 im=Image.new('RGBA',(5120,1440));im.paste(master.crop((x0,0,x1,1440)),(x0,0));im.save(p/f'cmtype-{side}-extension-v4.png')
master.crop((3040,0,4000,640)).save(p/'right-light-current.png');master.crop((3040,0,5120,720)).save(p/'full-right-light-proof.png')
j=json.loads((p/'job.json').read_text());j.update(tool='built-in image_gen',raw_path='raw.png',raw_sha256=sha(p/'raw.png'),input_sha256=sha(p/'lighting-target.png'),new_calls=1,pilot_total_calls=85,adoption='Only low-frequency luminance guide; no generated detail or source RGB adopted');(p/'generations.json').write_text(json.dumps(j,indent=2)+'\n');(p/'prompt.txt').write_text(j['prompt']+'\n')
(p/'assembly-receipt.json').write_text(json.dumps(dict(domain=[3520,0,1600,640],beam_source_band=[3360,3520],beam_field_sigma=48,beam_vertical_fade=[128,224],beam_horizontal_onset=[0,96],beam_gain_clip=[.6,1.4],raw_guide_sigma=32,raw_guide_gain_clip=[.85,1.15],source_edge_bands=[3496,3520,3544],edge_sigma=12,edge_gain_clip=[.55,1.5],horizontal_decay=480,outer_fade=[1120,1600],vertical_fade=[256,640],lighting='multiplicative scalar luminance applied equally to R/G/B',geometry_and_texture_from='v3 only',source_center_and_left_exact=True,right_below640_exact=True,master_sha256=sha(p/'cmtype-wide-v4.png'),processor_sha256=sha(Path(__file__))),indent=2)+'\n')
prev=json.loads((p/'before-hashes.json').read_text());assert all(sha(r/f)==v for f,v in prev.items());pins=json.loads((r/'battle-fighter-approval-20261019.json').read_text());assert all(sha(r/f['path'])==f['sha256'] for f in pins['files']);(p/'verification.json').write_text(json.dumps(dict(prior_pngs_unchanged=len(prev),approved_fighter_files_exact=len(pins['files']),left_and_original_center_exact=True,all5aspectcenters_exact=True,right_below640_exact=True,new_builtin_calls=1,pilot_total_calls=85,changed_pixels=int(np.any(a!=before,axis=2).sum())),indent=2)+'\n');print((p/'verification.json').read_text())
