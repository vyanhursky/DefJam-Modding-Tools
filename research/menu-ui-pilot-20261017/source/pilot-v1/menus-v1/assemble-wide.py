"""Source-fixed widescreen assemblies; independent scene additions, five crops."""
from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,importlib.util
p=Path(__file__).resolve().parent;sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();spec=importlib.util.spec_from_file_location('seams',p.parent/'seam-v2/assemble-bridges.py');seams=importlib.util.module_from_spec(spec);spec.loader.exec_module(seams);seams.check_solver();records=[]
ratios={'4x3':1920,'16x10':2304,'16x9':2560,'21x9':3360,'32x9':5120}
for label in ['options','jukebox']:
 known=Image.open(p/(label+'-known.png' if label=='options' else label+'-center.png')).convert('RGB');a=np.zeros((1440,5120,3),dtype='uint8');a[:,1600:1600+known.width]=np.array(known);edge_right=1600+known.width
 for side in ['left','right']:
  x0,x1,join=(0,2320,1600) if side=='left' else (edge_right-720,5120,720)
  raw=Image.open(p/(label+'-'+side+'-raw.png')).convert('RGB');target_size=(x1-x0,1440);assert abs(raw.width/raw.height-target_size[0]/target_size[1])<.005,'Reject canvas aspect/crop drift'
  normalized=raw.resize(target_size,Image.Resampling.LANCZOS);normalized.save(p/(label+'-'+side+'-normalized.png'));n=np.array(normalized)
  if side=='left':a[:,:1600]=n[:,:join]
  else:a[:,edge_right:]=n[:,join:]
  records.append(dict(label=label,side=side,kind='full-height generated side',raw_size=list(raw.size),target_size=list(target_size),raw_sha256=sha(p/(label+'-'+side+'-raw.png')),crop=[x0,0,x1,1440],join=join,normalization='uniform full-canvas resolution normalization with pixel-rounded dimensions; aspect and fixed-context architectural landmarks inspected; no inactive padding'))
 old=a.copy()
 for side,edge in [('left',1600),('right',edge_right)]:
  width=384;x0,x1=(edge-width,edge) if side=='left' else (edge,edge+width)
  gen=old[:,x0:x1].astype(float);fixed=gen.copy()
  if side=='left':fixed[:,-1]=np.clip(2*old[:,edge].astype(float)-old[:,edge+1],0,255)
  else:fixed[:,0]=np.clip(2*old[:,edge-1].astype(float)-old[:,edge-2],0,255)
  t=np.linspace(0,1,width)[:,None]
  for y in [0,-1]:fixed[y]=gen[y]+(fixed[y,0]-gen[y,0])*(1-t)+(fixed[y,-1]-gen[y,-1])*t
  out,res=seams.boundary_match(gen,fixed);a[:,x0:x1]=np.rint(out).clip(0,255).astype('uint8')
  records.append(dict(label=label,side=side,domain=[x0,0,width,1440],harmonic_residual=res,kind='one-sided harmonic boundary reconciliation',known_edge=edge))
 assert np.array_equal(a[:,1600:1600+known.width],np.array(known));assert np.array_equal(a[:,1600:3520],np.array(Image.open(p/(label+'-center.png')).convert('RGB')))
 Image.fromarray(a).save(p/(label+'-wide-draft.png'))
 # Keep generated additions separate from source-shaped moving layers.
 left=Image.new('RGBA',(5120,1440),(0,0,0,0));left.paste(Image.fromarray(a[:,:1600]).convert('RGBA'),(0,0));left.save(p/(label+'-left-extension-layer.png'))
 right=Image.new('RGBA',(5120,1440),(0,0,0,0));right.paste(Image.fromarray(a[:,3520:]).convert('RGBA'),(3520,0));right.save(p/(label+'-right-extension-layer.png'))
 for side,edge in [('left',1600),('right',edge_right)]:Image.fromarray(a).crop((edge-384,0,edge+384,1440)).save(p/(label+'-'+side+'-join.png'))
 # Native reference enlargements share the nominal layer geometry. Wide black
 # margins show absence of original scenic data, not a proposed pillarbox mod.
 native=Image.open(p/(label+'-original-layout.png')).convert('RGB')
 for ratio,w in ratios.items():
  x=(5120-w)//2;out=Image.fromarray(a).crop((x,0,x+w,1440));out.save(p/(label+'-'+ratio+'-draft.png'));reference=Image.new('RGB',(w,1440));reference.paste(native,((w-1920)//2,0));reference.save(p/(label+'-'+ratio+'-original.png'));assert np.array_equal(np.array(out)[:,(w-1920)//2:(w+1920)//2],a[:,1600:3520])
(p/'wide-receipt.json').write_text(json.dumps(dict(records=records,center_checks='10/10 exact',known_source_context_exact=True,outputs='2studies x5aspects',status='unapproved texture-layout studies; no UI/lighting/game render claim',processor_sha256=sha(Path(__file__)),boundary_processor_sha256=sha(p.parent/'seam-v2/assemble-bridges.py')),indent=2)+'\n');print('2studies x5ratios,10exact centers; known source contexts exact')
