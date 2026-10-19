"""Generated-only eight-join repairs; retain all original centers exactly.

Reject source-support assembly: it created vertical bands. Preserve it as history.
Adopt middle512px from blank-gap AI bridge; reconcile boundary colors on generated
pixels only, with source-measured optical softness and no reflected source strips.
"""
from pathlib import Path
from PIL import Image,ImageFilter
import json,hashlib,shutil,importlib.util,numpy as np
p=Path(__file__).resolve().parent;sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();spec=importlib.util.spec_from_file_location('seams',p.parent/'seam-v2/assemble-bridges.py');seams=importlib.util.module_from_spec(spec);spec.loader.exec_module(seams)
jobs=json.loads((p/'bridge-results.json').read_text());records=[];g=json.loads((p/'generations.json').read_text());g['calls']=[j for j in g['calls'] if j['kind']!='boundary bridge']
def rms(im):
 a=np.array(im).astype(float);b=np.array(im.filter(ImageFilter.GaussianBlur(3))).astype(float);return float(np.sqrt(np.mean((a-b)**2)))
for j in jobs:
 name=j['label'];shutil.copy2(j['path'],p/(name+'-raw.png'));j['raw_size']=list(Image.open(p/(name+'-raw.png')).size);j['raw_sha256']=sha(p/(name+'-raw.png'));j['inputs']=[dict(path=f,sha256=sha(Path(f))) for f in j['referenced_image_paths']];j['adoption']='Only middle512 generated pixels; exact source+retained outer context restored; no source-support strip.';(p/(name+'-prompt.txt')).write_text(j['prompt']+'\n');g['calls'].append(j)
g['new_calls']=len(g['calls']);g['pilot_total_calls']=57+len(g['calls']);(p/'generations.json').write_text(json.dumps(g,indent=2)+'\n')
for label in ['cmtype','chooseF2','chooseF3','chooseF4']:
 old=Image.open(p/(label+'-wide-draft.png')).convert('RGB');history=p/(label+'-wide-before-bridges.png')
 if not history.exists():shutil.copy2(p/(label+'-wide-draft.png'),history)
 else:old=Image.open(history).convert('RGB')
 # Source-matched mild defocus over new sides; fixed4:3 stays untouched.
 a=np.array(old);soft=np.array(old.filter(ImageFilter.GaussianBlur(2)));a[:,:1600]=soft[:,:1600];a[:,3520:]=soft[:,3520:];allowed=np.zeros(a.shape[:2],bool)
 for j in [j for j in jobs if j['menu']==label]:
  left=j['side']=='left';raw=Image.open(p/(j['label']+'-raw.png')).convert('RGB');assert abs(raw.width/raw.height-1536/1440)<.006;im=raw.resize((1536,1440),Image.Resampling.LANCZOS);im.save(p/(j['label']+'-normalized.png'));target=Image.open(p/(j['label']+'-target.png')).convert('RGB');ctx=(1024,0,1120,1440) if left else (416,0,512,1440);ref=rms(target.crop(ctx));radius=min([1.5,2,3,4,6],key=lambda rad:abs(rms(im.filter(ImageFilter.GaussianBlur(rad)).crop(ctx))-ref));filtered=im.filter(ImageFilter.GaussianBlur(radius));gen=np.array(filtered.crop((512,0,1024,1440))).astype(float);x0=j['domain'][0];x1=x0+512;fixed=gen.copy();fixed[:,0]=np.clip(2*a[:,x0-1].astype(float)-a[:,x0-2],0,255);fixed[:,-1]=np.clip(2*a[:,x1].astype(float)-a[:,x1+1],0,255);t=np.linspace(0,1,512)[:,None]
  for y in [0,-1]:fixed[y]=gen[y]+(fixed[y,0]-gen[y,0])*(1-t)+(fixed[y,-1]-gen[y,-1])*t
  out,res=seams.boundary_match(gen,fixed);a[:,x0:x1]=np.rint(out).clip(0,255).astype('uint8');allowed[:,x0:x1]=True;records.append(dict(label=j['label'],domain=j['domain'],raw_size=list(raw.size),normalization='full-canvas uniform resample1536x1440',source_context_rms=ref,gaussian_radius=radius,outer_generated_gaussian_radius=2,harmonic_residual=res,source_original_exact=True))
 center=np.array(Image.open(p/(label+'-center.png')).convert('RGB'));assert np.array_equal(a[:,1600:3520],center);master=Image.fromarray(a);master.save(p/(label+'-wide-draft.png'))
 for side,edge in [('left',1600),('right',3520)]:master.crop((edge-384,0,edge+384,1440)).save(p/(label+'-'+side+'-join.png'))
 for side,x0,x1 in [('left',0,1600),('right',3520,5120)]:
  layer=Image.new('RGBA',(5120,1440));layer.paste(master.crop((x0,0,x1,1440)),(x0,0));layer.save(p/(label+'-'+side+'-extension.png'))
 for ratio,w in {'4x3':1920,'16x10':2304,'16x9':2560,'21x9':3360,'32x9':5120}.items():x=(5120-w)//2;master.crop((x,0,x+w,1440)).save(p/(label+'-'+ratio+'-draft.png'))
(p/'bridge-receipt.json').write_text(json.dumps(dict(records=records,rejected_initial_assembly='Original-material support produced vertical bands; replaced by blank-gap8AIbridges. No reflection/edge-hold strips adopted.',source_centers_exact=True,processor_sha256=sha(Path(__file__))),indent=2)+'\n')
w=json.loads((p/'wide-receipt.json').read_text());w['initial_assembly_only']=True;w['final_processor']='finish-bridges.py';w['final_receipt']='bridge-receipt.json';(p/'wide-receipt.json').write_text(json.dumps(w,indent=2)+'\n')
contact=Image.new('RGB',(1280,1440))
for i,label in enumerate(['cmtype','chooseF2','chooseF3','chooseF4']):contact.paste(Image.open(p/(label+'-wide-draft.png')).resize((1280,360),Image.Resampling.LANCZOS),(0,i*360))
contact.save(p/'wide-contact-final.png');print('8bridges assembled;4original centers exact;21new built-in calls/78pilot total')
