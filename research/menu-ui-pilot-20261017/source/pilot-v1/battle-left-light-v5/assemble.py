"""Lighting-only left repair from v3. Entire pre-v4 right and source center exact."""
from pathlib import Path
from PIL import Image,ImageFilter
import numpy as np,json,hashlib
p=Path(__file__).resolve().parent;r=p.parent;sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
before=np.array(Image.open(r/'battle-left-v3/cmtype-wide-v3.png').convert('RGB'));a=before.copy();raw=Image.open(p/'raw.png').convert('RGB');assert abs(raw.width/raw.height-2)<.008;raw=raw.resize((1440,720),Image.Resampling.LANCZOS);raw.save(p/'normalized.png');base=Image.open(p/'lighting-target.png').convert('RGB')
def lum(im):return np.asarray(im,dtype=float)@np.array([.2126,.7152,.0722])
def blur(im,n):return lum(im.filter(ImageFilter.GaussianBlur(n)))
def smooth(t):t=np.clip(t,0,1);return t*t*(3-2*t)
h,w=720,960;xx=np.arange(w);yy=np.arange(h);orig=blur(base,32);proposal=blur(raw,32);guide=np.clip((proposal[:,:w]+2)/(orig[:,:w]+2),.55,1.15)
# Lighting profiles on genuine adjacent brick bands avoid adopting model material.
source=lum(Image.fromarray(before[:h,1600:1664]).filter(ImageFilter.GaussianBlur(16))).mean(1)
generated=lum(Image.fromarray(before[:h,1536:1600]).filter(ImageFilter.GaussianBlur(16))).mean(1)*guide[:,-64:].mean(1)
edge_gain=np.clip((source+2)/(generated+2),.55,1.4)
distance=959-xx;edge_weight=np.exp(-distance/320);gain=guide*(1+(edge_gain[:,None]-1)*edge_weight[None,:])
weight=smooth(xx/160)[None,:]*(1-smooth((yy-480)/240))[:,None];gain=1+(gain-1)*weight
a[:h,640:1600]=np.rint(before[:h,640:1600].astype(float)*gain[:,:,None]).clip(0,255).astype('uint8')
assert np.array_equal(a[:,1600:],before[:,1600:]);assert np.array_equal(a[:,:640],before[:,:640]);assert np.array_equal(a[720:],before[720:]);master=Image.fromarray(a);master.save(p/'cmtype-wide-v5.png')
for ratio,width in {'4x3':1920,'16x10':2304,'16x9':2560,'21x9':3360,'32x9':5120}.items():
 x=(5120-width)//2;im=master.crop((x,0,x+width,1440));im.save(p/f'cmtype-{ratio}-v5.png');assert np.array_equal(np.array(im)[:,(width-1920)//2:(width+1920)//2],before[:,1600:3520])
for side,edge in [('left',1600),('right',3520)]:master.crop((edge-384,0,edge+384,1440)).save(p/f'cmtype-{side}-join.png')
for side,x0,x1 in [('left',0,1600),('right',3520,5120)]:
 im=Image.new('RGBA',(5120,1440));im.paste(master.crop((x0,0,x1,1440)),(x0,0));im.save(p/f'cmtype-{side}-extension-v5.png')
master.crop((1120,0,2080,640)).save(p/'left-light-current.png');master.crop((640,0,2080,720)).save(p/'full-left-light-proof.png')
j=json.loads((p/'job.json').read_text());j.update(tool='built-in image_gen',raw_path='raw.png',raw_sha256=sha(p/'raw.png'),input_sha256=sha(p/'lighting-target.png'),new_calls=1,pilot_total_calls=86,adoption='Low-frequency illumination only; model texture/geometry discarded. V3 base restores complete pre-v4 right.');(p/'generations.json').write_text(json.dumps(j,indent=2)+'\n');(p/'prompt.txt').write_text(j['prompt']+'\n')
(p/'assembly-receipt.json').write_text(json.dumps(dict(base='battle-left-v3/cmtype-wide-v3.png',domain=[640,0,960,720],raw_guide_sigma=32,raw_guide_gain_clip=[.55,1.15],source_edge_band=[1600,1664],generated_edge_band=[1536,1600],edge_sigma=16,edge_gain_clip=[.55,1.4],edge_decay=320,horizontal_onset=[640,800],vertical_fade=[480,720],lighting='same scalar gain on R/G/B; source cool channel ratios preserved to rounding',original_center_and_entire_pre_v4_right_exact=True,below720_and_left_of640_exact=True,model_texture_or_geometry_adopted=False,master_sha256=sha(p/'cmtype-wide-v5.png'),processor_sha256=sha(Path(__file__))),indent=2)+'\n')
prev=json.loads((p/'before-hashes.json').read_text());assert all(sha(r/f)==v for f,v in prev.items());pins=json.loads((r/'battle-fighter-approval-20261019.json').read_text());assert all(sha(r/f['path'])==f['sha256'] for f in pins['files']);(p/'verification.json').write_text(json.dumps(dict(prior_pngs_unchanged=len(prev),approved_fighter_files_exact=len(pins['files']),original_center_exact=True,all5aspectcenters_exact=True,entire_pre_v4_right_exact=True,below720_and_left_of640_exact=True,new_builtin_calls=1,pilot_total_calls=86,changed_pixels=int(np.any(a!=before,2).sum())),indent=2)+'\n');print((p/'verification.json').read_text())
