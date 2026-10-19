"""Course-guide retry + generated-only row registration at the brick join."""
from pathlib import Path
from PIL import Image,ImageFilter
import json,hashlib,shutil,importlib.util,numpy as np
p=Path(__file__).resolve().parent;sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();spec=importlib.util.spec_from_file_location('seams',p.parent/'seam-v2/assemble-bridges.py');seams=importlib.util.module_from_spec(spec);spec.loader.exec_module(seams)
j=json.loads((p/'course-retry-result.json').read_text());name=j['label'];shutil.copy2(j['path'],p/(name+'-raw.png'));raw=Image.open(p/(name+'-raw.png')).convert('RGB');assert abs(raw.width/raw.height-1536/1440)<.006;im=raw.resize((1536,1440),Image.Resampling.LANCZOS);im.save(p/(name+'-normalized.png'));j['raw_size']=list(raw.size);j['raw_sha256']=sha(p/(name+'-raw.png'));j['inputs']=[dict(path=f,sha256=sha(Path(f))) for f in j['referenced_image_paths']];j['adoption']='Generatedmiddle512only;26courseguide heights,local row registration,2px softness;source center exact.';(p/(name+'-prompt.txt')).write_text(j['prompt']+'\n')
g=json.loads((p/'generations.json').read_text());g['calls']=[x for x in g['calls'] if x['label']!=name];g['calls'].append(j);g['new_calls']=len(g['calls']);g['pilot_total_calls']=57+len(g['calls']);(p/'generations.json').write_text(json.dumps(g,indent=2)+'\n')
f=p/'cmtype-wide-draft.png';old=Image.open(f).convert('RGB');history=p/'cmtype-wide-before-course-retry.png'
if not history.exists():shutil.copy2(f,history)
a=np.array(old);gen=np.array(im.filter(ImageFilter.GaussianBlur(2)).crop((512,0,1024,1440))).astype(float)
# Register neighboring generated mortar valleys to source-measured guides.
profile=gen[:,416:496].mean((1,2));profile=np.convolve(profile,np.ones(5)/5,'same');source_ys=[0,78]+[y*3 for y in j['course_y_native']]+[1439];generated_ys=[0,78]
for y in source_ys[2:-1]:
 lo=max(generated_ys[-1]+8,y-18);hi=min(1430,y+19);z=lo+int(np.argmin(profile[lo:hi]));generated_ys.append(z)
generated_ys.append(1439);assert all(b>a for a,b in zip(generated_ys,generated_ys[1:]));mapping=np.interp(np.arange(1440),source_ys,generated_ys)
registered=np.empty_like(gen);ys=np.arange(1440)
for x in range(512):
 weight=(x/511)**2;sample=ys+(mapping-ys)*weight;lo=np.floor(sample).astype(int).clip(0,1439);hi=(lo+1).clip(0,1439);frac=(sample-lo)[:,None];registered[:,x]=gen[lo,x]*(1-frac)+gen[hi,x]*frac
gen=registered;x0=1088;x1=1600;fixed=gen.copy();fixed[:,0]=a[:,x0-1];fixed[:,-1]=a[:,x1];t=np.linspace(0,1,512)[:,None]
for y in [0,-1]:fixed[y]=gen[y]+(fixed[y,0]-gen[y,0])*(1-t)+(fixed[y,-1]-gen[y,-1])*t
out,res=seams.boundary_match(gen,fixed);a[:,x0:x1]=np.rint(out).clip(0,255).astype('uint8');assert np.array_equal(a[:,1600:3520],np.array(old)[:,1600:3520]);master=Image.fromarray(a);master.save(f)
for side,edge in [('left',1600),('right',3520)]:master.crop((edge-384,0,edge+384,1440)).save(p/('cmtype-'+side+'-join.png'))
for ratio,w in {'4x3':1920,'16x10':2304,'16x9':2560,'21x9':3360,'32x9':5120}.items():x=(5120-w)//2;master.crop((x,0,x+w,1440)).save(p/('cmtype-'+ratio+'-draft.png'))
layer=Image.new('RGBA',(5120,1440));layer.paste(master.crop((0,0,1600,1440)),(0,0));layer.save(p/'cmtype-left-extension.png')
(p/'course-retry-receipt.json').write_text(json.dumps(dict(domain=[1088,0,512,1440],source_course_y=source_ys,generated_course_y=generated_ys,registration='Row resampling only on generated512;bounded18px mortar-valley fit,eased quadratically to retained outer.',gaussian_radius=2,harmonic_residual=res,source_center_exact=True,processor_sha256=sha(Path(__file__))),indent=2)+'\n')
contact=Image.new('RGB',(1280,1440))
for i,label in enumerate(['cmtype','chooseF2','chooseF3','chooseF4']):contact.paste(Image.open(p/(label+'-wide-draft.png')).resize((1280,360),Image.Resampling.LANCZOS),(0,i*360))
contact.save(p/'wide-contact-final.png');print('Source-guided brick retry:22newcalls/79pilot total;centerexact')
