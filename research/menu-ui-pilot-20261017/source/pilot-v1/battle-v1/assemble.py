"""Assemble generated sides around exact source-shaped centers; match grain/color.

No original scene pixels modified. Render proposals are normalized uniformly.
Generated-only boundary correction and support retain material continuity.
"""
from pathlib import Path
from PIL import Image,ImageFilter,ImageDraw
import json,hashlib,shutil,importlib.util,numpy as np
p=Path(__file__).resolve().parent;sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
spec=importlib.util.spec_from_file_location('seams',p.parent/'seam-v2/assemble-bridges.py');seams=importlib.util.module_from_spec(spec);spec.loader.exec_module(seams)
jobs=json.loads((p/'outpaint-results.json').read_text());retry=json.loads((p/'brick-retry-result.json').read_text());jobs.append(retry);records=[]
for j in jobs:
 name=j['label'];shutil.copy2(j['path'],p/(name+'-raw.png'));raw=Image.open(p/(name+'-raw.png'));j['raw_size']=list(raw.size);j['raw_sha256']=sha(p/(name+'-raw.png'));j['inputs']=[dict(path=f,sha256=sha(Path(f))) for f in j['referenced_image_paths']];j['adoption']='rejected duplicated corner/plaster beyond brick slab' if name=='cmtype-left' else 'generated side only; original context discarded'
 (p/(name+'-prompt.txt')).write_text(j['prompt']+'\n')
basejobs=json.loads((p/'generations.json').read_text())['calls'];(p/'generations.json').write_text(json.dumps(dict(tool='built-in image_gen',pilot_previous_calls=57,new_calls=len(basejobs)+len(jobs),calls=basejobs+jobs),indent=2)+'\n')
ratios={'4x3':1920,'16x10':2304,'16x9':2560,'21x9':3360,'32x9':5120}
def rms(im):
 a=np.array(im).astype(float);b=np.array(im.filter(ImageFilter.GaussianBlur(3))).astype(float);return float(np.sqrt(np.mean((a-b)**2)))
for label in ['cmtype','chooseF2','chooseF3','chooseF4']:
 center=Image.open(p/(label+'-center.png')).convert('RGB');a=np.zeros((1440,5120,3),dtype='uint8');a[:,1600:3520]=np.array(center)
 for side in ['left','right']:
  j=next(j for j in jobs if j['menu']==label and j['side']==side and (j['label']=='cmtype-left-brick-retry' if label=='cmtype' and side=='left' else True));name=j['label'];left=side=='left';targetwidth=1840 if name=='cmtype-left-brick-retry' else 2320;raw=Image.open(p/(name+'-raw.png')).convert('RGB');assert abs(raw.width/raw.height-targetwidth/1440)<.006,(name,raw.size);im=raw.resize((targetwidth,1440),Image.Resampling.LANCZOS);im.save(p/(name+'-normalized.png'))
  ctx=(1600,0,1696,1440) if left else (624,0,720,1440);sourcectx=center.crop((0,0,96,1440) if left else (1824,0,1920,1440));proposalctx=im.crop(ctx);reference_rms=rms(sourcectx)
  radius=min([0,1,1.5,2,3,4,6],key=lambda rad:abs(rms(proposalctx if rad==0 else proposalctx.filter(ImageFilter.GaussianBlur(rad)))-reference_rms));soft=im if radius==0 else im.filter(ImageFilter.GaussianBlur(radius));x0=0 if left else 720;gen=np.array(soft.crop((x0,0,x0+1600,1440))).astype(float)
  # Color/grain discrepancy in generated context does not authorize source grade.
  ref=np.array(sourcectx.filter(ImageFilter.GaussianBlur(24))).astype(float).mean(1);prop=np.array(soft.crop(ctx).filter(ImageFilter.GaussianBlur(24))).astype(float).mean(1);delta=ref-prop
  # Low-frequency correction on generated side only; maintain zero boundary jump
  # while easing correction away from original into outer scenery.
  distance=np.arange(1599,-1,-1) if left else np.arange(1600);weight=np.exp(-distance/900);gen=np.clip(gen+delta[:,None,:]*weight[None,:,None],0,255)
  # 48px original-material support; one reflection only, fading fully by192px.
  src=np.array(center).astype(float);pos=np.minimum(distance,47);borrowed=src[:,pos] if left else src[:,1919-pos];w=np.clip(1-distance/192,0,1)**2;gen=gen*(1-w[None,:,None])+borrowed*w[None,:,None]
  edge=1600 if left else 3520;span=384;band=gen[:,-span:] if left else gen[:,:span];fixed=band.copy()
  if left:fixed[:,-1]=np.clip(2*src[:,0]-src[:,1],0,255)
  else:fixed[:,0]=np.clip(2*src[:,-1]-src[:,-2],0,255)
  t=np.linspace(0,1,span)[:,None]
  for y in [0,-1]:fixed[y]=band[y]+(fixed[y,0]-band[y,0])*(1-t)+(fixed[y,-1]-band[y,-1])*t
  matched,res=seams.boundary_match(band,fixed)
  if left:gen[:,-span:]=matched;a[:,:1600]=np.rint(gen).clip(0,255).astype('uint8')
  else:gen[:,:span]=matched;a[:,3520:]=np.rint(gen).clip(0,255).astype('uint8')
  records.append(dict(menu=label,side=side,adopted=name,raw_size=list(raw.size),normalized=[targetwidth,1440],reference_rms=reference_rms,gaussian_radius=radius,color_correction='generated-only low-frequency row RGB delta; exp falloff900px',support='single48px reflection/edge hold,192px quadratic fade on generated side only',harmonic_band=384,harmonic_residual=res))
 assert np.array_equal(a[:,1600:3520],np.array(center));master=Image.fromarray(a);master.save(p/(label+'-wide-draft.png'))
 for side,edge in [('left',1600),('right',3520)]:master.crop((edge-384,0,edge+384,1440)).save(p/(label+'-'+side+'-join.png'))
 for side,x0,x1 in [('left',0,1600),('right',3520,5120)]:
  layer=Image.new('RGBA',(5120,1440));layer.paste(master.crop((x0,0,x1,1440)),(x0,0));layer.save(p/(label+'-'+side+'-extension.png'))
 native=Image.open(p/(label+'-original-layout.png')).convert('RGB')
 for ratio,w in ratios.items():
  x=(5120-w)//2;out=master.crop((x,0,x+w,1440));out.save(p/(label+'-'+ratio+'-draft.png'));assert np.array_equal(np.array(out)[:,(w-1920)//2:(w+1920)//2],a[:,1600:3520]);reference=Image.new('RGB',(w,1440));reference.paste(native,((w-1920)//2,0));reference.save(p/(label+'-'+ratio+'-original.png'))
 for suffix in ['source','faithful','restrained','raw']:Image.open(p/(label+'-'+suffix+'.png')).convert('RGBA').getchannel('A').save(p/(label+'-'+suffix+'-alpha.png'))
(p/'wide-receipt.json').write_text(json.dumps(dict(records=records,centers_exact='20/20',status='Unapproved artwork; native UV/scissor,portraits,lighting and game captures pending',processor_sha256=sha(Path(__file__)),boundary_processor_sha256=sha(p.parent/'seam-v2/assemble-bridges.py')),indent=2)+'\n')
contact=Image.new('RGB',(1280,1440))
for i,label in enumerate(['cmtype','chooseF2','chooseF3','chooseF4']):
 im=Image.open(p/(label+'-wide-draft.png')).resize((1280,360),Image.Resampling.LANCZOS);contact.paste(im,(0,i*360))
contact.save(p/'wide-contact.png');print('4masters,20aspect drafts,8joinproofs,8extension layers')
