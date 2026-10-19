from pathlib import Path
from PIL import Image,ImageFilter
import numpy as np,json,hashlib,importlib.util
p=Path(__file__).resolve().parent;root=p.parent;sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();spec=importlib.util.spec_from_file_location('seams',root/'seam-v2/assemble-bridges.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
old=np.array(Image.open(root/'menus-seams-v2/options-wide-v2.png').convert('RGB'));raw=np.array(Image.open(p/'door-normalized.png').convert('RGB'));out=old.copy();out[:,3520:]=raw[:,720:];Image.fromarray(out).save(p/'options-hard-assembly.png')
# Only192 generated pixels receive residual boundary/grain matching. The narrow
# reference-proportioned door is already laid out; this does not repair geometry.
x0,x1=3520,3712;im=Image.fromarray(out);gen=out[:,x0:x1].astype(float);soft=np.array(im.filter(ImageFilter.GaussianBlur(2)))[:,x0:x1].astype(float);weight=np.linspace(1,0,192);gen+=(soft-gen)*weight[None,:,None];fixed=gen.copy();fixed[:,0]=np.clip(2*out[:,x0-1].astype(float)-out[:,x0-2],0,255);fixed[:,-1]=np.clip(2*out[:,x1].astype(float)-out[:,x1+1],0,255);u=np.linspace(0,1,192)[:,None]
for y in [0,-1]:fixed[y]=gen[y]+(fixed[y,0]-gen[y,0])*(1-u)+(fixed[y,-1]-gen[y,-1])*u
matched,res=m.boundary_match(gen,fixed);out[:,x0:x1]=np.rint(matched).clip(0,255).astype('uint8');assert np.array_equal(old[:,:3520],out[:,:3520]);Image.fromarray(out).save(p/'options-wide-v3.png');Image.fromarray(out).crop((3100,0,5120,1440)).save(p/'options-door-complete.png')
for side,edge in [('left',1600),('right',3520)]:
 Image.fromarray(out).crop((edge-384,0,edge+384,1440)).save(p/('options-'+side+'-join.png'));Image.fromarray(old).crop((edge-384,0,edge+384,1440)).save(p/('options-'+side+'-before.png'))
for r,w in [('4x3',1920),('16x10',2304),('16x9',2560),('21x9',3360),('32x9',5120)]:x=(5120-w)//2;Image.fromarray(out).crop((x,0,x+w,1440)).save(p/('options-'+r+'-v3.png'))
(p/'assembly-receipt.json').write_text(json.dumps(dict(allowed=[3520,0,1600,1440],source_center_and_accepted_left='exact',boundary_match=[3520,0,192,1440],softness_radius=2,residual=res,door_reference_frame=[570,265,730,1110],door_normalized_jamb_x_approx=1280,note='Reference doorway supplied at natural scale; no horizontal stretch applied. New width and surface require owner art review.',processor_sha256=sha(Path(__file__)),master_sha256=sha(p/'options-wide-v3.png')),indent=2)+'\n')
