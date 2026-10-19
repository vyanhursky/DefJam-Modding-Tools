"""Generated-only surface/ceiling repair; no source-center or fighter changes."""
from pathlib import Path
from PIL import Image,ImageFilter
import numpy as np,json,hashlib,shutil,importlib.util
p=Path(__file__).resolve().parent;r=p.parent;old=r/'battle-v1';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();spec=importlib.util.spec_from_file_location('seams',r/'seam-v2/assemble-bridges.py');seams=importlib.util.module_from_spec(spec);spec.loader.exec_module(seams)
g=json.loads((p/'generations.json').read_text());gap=json.loads((p/'gap-result.json').read_text());g['calls']=[j for j in g['calls'] if j['label']!='left-gap']+[gap]
for j in g['calls']:
 f=p/(j['label']+'-raw.png');shutil.copy2(j['path'],f);j['raw_size']=list(Image.open(f).size);j['raw_sha256']=sha(f);j['inputs']=[dict(path=f,sha256=sha(Path(f))) for f in j['referenced_image_paths']];j['adoption']='rejected:retained vertical face smears from filled target' if j['label']=='left-material' else 'generated region only; source context restored exactly';(p/(j['label']+'-prompt.txt')).write_text(j['prompt']+'\n')
g['new_calls']=len(g['calls']);g['pilot_total_calls']=79+len(g['calls']);(p/'generations.json').write_text(json.dumps(g,indent=2)+'\n')
base=Image.open(old/'cmtype-wide-draft.png').convert('RGB');a=np.array(base);before=a.copy();allowed=np.zeros(a.shape[:2],bool)
# Adopt clean-gap material without any vertical row remapping. No copied source
# support/reflection/edge hold; those were known causes of false material bands.
raw=Image.open(p/'left-gap-raw.png').convert('RGB');assert abs(raw.width/raw.height-1536/1440)<.006;im=raw.resize((1536,1440),Image.Resampling.LANCZOS);im.save(p/'left-gap-normalized.png');gen=np.array(im.filter(ImageFilter.GaussianBlur(1)).crop((512,78,1024,1440))).astype(float);x0,x1=1088,1600;y0,y1=78,1440;fixed=gen.copy();fixed[:,0]=before[y0:y1,x0-1];fixed[:,-1]=before[y0:y1,x1];t=np.linspace(0,1,512)[:,None]
for y in [0,-1]:fixed[y]=gen[y]+(fixed[y,0]-gen[y,0])*(1-t)+(fixed[y,-1]-gen[y,-1])*t
out,res=seams.boundary_match(gen,fixed);a[y0:y1,x0:x1]=np.rint(out).clip(0,255).astype('uint8');allowed[y0:y1,x0:x1]=True
# Ceiling line only; retain good right wall beyond256high byte-for-byte.
raw=Image.open(p/'right-ceiling-raw.png').convert('RGB');assert abs(raw.width/raw.height-2080/720)<.008;im=raw.resize((2080,720),Image.Resampling.LANCZOS);im.save(p/'right-ceiling-normalized.png');proposal=np.array(im).astype(float);gen=proposal[:256,480:2080].copy();
# Source/proposal vertical-gradient fit over y70..170 measured +1px.
# Shift generated beam up1px, smoothly remove the shift below192px.
ys=np.arange(256);weight=np.ones(256);weight[160:]=1-np.linspace(0,1,96);sample=ys+weight;lo=np.floor(sample).astype(int);frac=(sample-lo)[:,None,None];gen=proposal[lo,480:2080]*(1-frac)+proposal[lo+1,480:2080]*frac;height,width=gen.shape[:2];fixed=gen.copy();fixed[:,0]=before[:256,3519];fixed[-1]=before[255,3520:5120]
# End edge retained for smooth transition into unchanged lower wall; rightmost
# outer boundary has no neighboring scene and remains proposal's own boundary.
t=np.linspace(0,1,width)[:,None]
fixed[0]=gen[0]+(fixed[0,0]-gen[0,0])*(1-t)+(fixed[0,-1]-gen[0,-1])*t
out,rr=seams.boundary_match(gen,fixed);fade=np.ones(256);tt=np.linspace(0,1,64);fade[192:]=1-tt*tt*(3-2*tt);a[:256,3520:5120]=np.rint(before[:256,3520:5120]*(1-fade[:,None,None])+out*fade[:,None,None]).clip(0,255).astype('uint8');allowed[:256,3520:5120]=True
assert np.array_equal(a[:,1600:3520],before[:,1600:3520]);assert np.array_equal(a[~allowed],before[~allowed]);master=Image.fromarray(a);master.save(p/'cmtype-wide-v2.png')
for side,edge in [('left',1600),('right',3520)]:
 master.crop((edge-384,0,edge+384,1440)).save(p/('cmtype-'+side+'-join.png'));base.crop((edge-384,0,edge+384,1440)).save(p/('cmtype-'+side+'-before.png'))
for ratio,w in {'4x3':1920,'16x10':2304,'16x9':2560,'21x9':3360,'32x9':5120}.items():
 x=(5120-w)//2;im=master.crop((x,0,x+w,1440));im.save(p/('cmtype-'+ratio+'-v2.png'));assert np.array_equal(np.array(im)[:,(w-1920)//2:(w+1920)//2],before[:,1600:3520])
for side,x0,x1 in [('left',0,1600),('right',3520,5120)]:
 im=Image.new('RGBA',(5120,1440));im.paste(master.crop((x0,0,x1,1440)),(x0,0));im.save(p/('cmtype-'+side+'-extension-v2.png'))
# Keep explicit focused texture and ceiling comparisons for surface/line review.
master.crop((1088,0,1856,1440)).save(p/'left-material-proof.png');master.crop((3040,0,4160,384)).save(p/'right-ceiling-proof.png');base.crop((3040,0,4160,384)).save(p/'right-ceiling-before.png')
(p/'assembly-receipt.json').write_text(json.dumps(dict(left_domain=[1088,78,512,1362],left_material_gaussian=1,left_vertical_remap=False,right_domain=[3520,0,1600,256],right_bottom_fade=[192,256],right_ceiling_source_profile_alignment_pixels=1,harmonic_residuals=[res,rr],source_center_exact=True,right_wall_below256_exact=True,unrequested_pixels_exact=True,changed_rgb_pixels=int(np.any(a!=before,2).sum()),processor_sha256=sha(Path(__file__)),master_sha256=sha(p/'cmtype-wide-v2.png')),indent=2)+'\n')
prev=json.loads((p/'before-hashes.json').read_text());assert all(sha(r/f)==h for f,h in prev.items());approval=json.loads((r/'battle-fighter-approval-20261019.json').read_text());assert all(sha(r/f['path'])==f['sha256'] for f in approval['files']);(p/'verification.json').write_text(json.dumps(dict(previous_pngs_unchanged=len(prev),approved_fighter_files_exact=len(approval['files']),center_exact=True,all5aspectcenters_exact=True,right_below256_exact=True,unrequested_pixels_exact=True,new_builtin_calls=3,pilot_total_calls=82),indent=2)+'\n');print('3calls/82total;39approvedpins/'+str(len(prev))+'priorPNGs exact;5centers/rightwall/unrequestedpixels exact')
