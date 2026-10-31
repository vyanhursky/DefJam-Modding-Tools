"""Source-protected High Scores master with normalized native-context sidewalls."""
from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
from defjam_tools.color_trial import rgb_to_lab,lab_to_rgb
p=Path(__file__).resolve().parent;r=p.parent;sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();core=np.array(Image.open(p/'hiscores-center.png').convert('RGB'));world=np.zeros((1440,5120,3),dtype='uint8');world[:,1600:3520]=core;params={}
def prof(v):
 k=np.exp(-np.arange(-192,193,dtype=float)**2/(2*64**2));k/=k.sum();return np.stack([np.convolve(np.pad(v[:,c],(192,192),mode='edge'),k,'valid') for c in range(v.shape[1])],1)
for side,crop,srcband,genband in [('left',(0,0,1600,1440),core[:,:144],slice(-384,None)),('right',(144,0,1744,1440),core[:,-144:],slice(0,384))]:
 raw=Image.open(p/f'{side}-raw.png').convert('RGB');assert abs(raw.width/raw.height-1744/1440)<.008;im=raw.resize((1744,1440),Image.Resampling.LANCZOS);im.save(p/f'{side}-normalized.png');im=im.crop(crop);im=im.resize((534,480),Image.Resampling.LANCZOS).resize((1600,1440),Image.Resampling.LANCZOS);g=rgb_to_lab(np.array(im));s=rgb_to_lab(srcband);gb=g[:,genband];sm=prof(s.mean(1));gm=prof(gb.mean(1));sv=np.maximum(prof((s*s).mean(1))-sm*sm,.01);gv=np.maximum(prof((gb*gb).mean(1))-gm*gm,.01);gain=np.clip(np.sqrt(sv/gv),.6,1.4);out=(g-gm[:,None,:])*gain[:,None,:]+sm[:,None,:];rgb,_=lab_to_rgb(out)
 edge=-1 if side=='left' else 0;target=core[:,0 if side=='left' else -1].astype(float);delta=target-rgb[:,edge].astype(float)
 for i in range(16):
  col=-1-i if side=='left' else i;rgb[:,col]=np.rint(rgb[:,col].astype(float)+delta*(1-i/16)**2).clip(0,255).astype('uint8')
 if side=='left':world[:,:1600]=rgb
 else:world[:,3520:]=rgb
 params[side]=dict(native_density=[534,480,1600,1440],source_band=144,generated_band=384,profile_sigma=64,gain_clip=[.6,1.4],edge_condition=16)
assert np.array_equal(world[:,1600:3520],core);master=Image.fromarray(world);master.save(p/'hiscores-wide-v1.png');orig=Image.open(p/'hiscores-original-layout.png').convert('RGB')
for ratio,w in {'4x3':1920,'16x10':2304,'16x9':2560,'21x9':3360,'32x9':5120}.items():
 x=(5120-w)//2;draft=master.crop((x,0,x+w,1440));draft.save(p/f'hiscores-{ratio}-draft.png');reference=Image.new('RGB',(w,1440));reference.paste(orig,((w-1920)//2,0));reference.save(p/f'hiscores-{ratio}-original.png');assert np.array_equal(np.array(draft)[:,(w-1920)//2:(w+1920)//2],core)
for side,edge in [('left',1600),('right',3520)]:master.crop((edge-384,0,edge+384,1440)).save(p/f'hiscores-{side}-join.png')
for side,x0,x1 in [('left',0,1600),('right',3520,5120)]:
 im=Image.new('RGBA',(5120,1440));im.paste(master.crop((x0,0,x1,1440)),(x0,0));im.save(p/f'hiscores-{side}-extension.png')
faith=np.array(Image.open(p/'hiscores-faithful.png'));rest=np.array(Image.open(p/'hiscores-restrained.png'));assert np.array_equal(rest[:,:,3],faith[:,:,3]);assert np.array_equal(rest[1920:],faith[1920:]);assert np.array_equal(rest[344:1760,192:2352],faith[344:1760,192:2352]);assert np.array_equal(rest[:,2032:2064],faith[:,2032:2064]);calls=[json.loads((p/'restoration-job.json').read_text())]+json.loads((p/'side-jobs.json').read_text())
for j in calls:
 j['raw']=j['label']+'-raw.png';j['raw_sha256']=sha(p/j['raw']);j['raw_size']=list(Image.open(p/j['raw']).size);j['inputs']=[dict(path=f,sha256=sha(Path(f))) for f in j['referenced_image_paths']];j['adoption']='Tiny safe wall detail; all generated board pixels discarded' if j['label']=='restoration' else 'Generatedsideonly,sourcecalibrated;fixedcontextdiscarded'
(p/'generations.json').write_text(json.dumps(dict(tool='built-in image_gen',new_calls=3,pilot_total_calls=95,calls=calls),indent=2)+'\n');(p/'wide-receipt.json').write_text(json.dumps(dict(size=[5120,1440],center=[1600,0,1920,1440],all5centers_exact=True,material=params,source_board_rules_exact=True,source_alpha_padding_seam_exact=True,processor_sha256=sha(Path(__file__)),master_sha256=sha(p/'hiscores-wide-v1.png')),indent=2)+'\n');prev=json.loads((p/'before-hashes.json').read_text());assert all(sha(r/f)==v for f,v in prev.items());pins=0
for approval in ['battle-fighter-approval-20261019.json','battle-setup-approval-20261019.json','rewards-approval-20261019.json']:
 a=json.loads((r/approval).read_text());assert all(sha(r/f['path'])==f['sha256'] for f in a['files']);pins+=len(a['files'])
(p/'verification.json').write_text(json.dumps(dict(prior_pngs_unchanged=len(prev),approved_battle_rewards_files_exact=pins,entire_score_board_exact=True,source_alpha_padding_seam_exact=True,all5native_centers_exact=True,new_builtin_calls=3,pilot_total_calls=95),indent=2)+'\n');print((p/'verification.json').read_text())
