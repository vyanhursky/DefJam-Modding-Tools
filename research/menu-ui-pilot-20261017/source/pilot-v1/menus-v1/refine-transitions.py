"""Technical source-supported transition proofs, no protected center edits.

A narrow real-material support patch continues source sampling softness into
new scenery. It contains only brick/door material (no paper/signs). The support
fades on the generated side; all source and approved imagery remains exact.
"""
from pathlib import Path
from PIL import Image,ImageFilter
import numpy as np,json,hashlib
p=Path(__file__).resolve().parent;records=[]
for label in ['options','jukebox']:
 f=p/(label+'-wide-draft.png');im=Image.open(f).convert('RGB');a=np.array(im).astype(float);out=a.copy();right=3776 if label=='options' else 3520
 for side,edge in [('left',1600),('right',right)]:
  span=512;support=48;x0,x1=(edge-span,edge) if side=='left' else (edge,edge+span)
  gen=a[:,x0:x1];soft=np.array(Image.fromarray(gen.astype('uint8')).filter(ImageFilter.GaussianBlur(1.8))).astype(float)
  distance=np.arange(span-1,-1,-1) if side=='left' else np.arange(span)
  # Back-and-forth within32native columns gives a short material support,
  # not a duplicated full brick/poster/door. Weight vanishes at384HD pixels.
  pos=np.minimum(distance,support-1)
  source_x=edge+pos if side=='left' else edge-1-pos
  borrowed=a[:,source_x];fade=384 if label=='options' and side=='right' else 192
  w=np.clip(1-distance/fade,0,1)**2
  filtered=gen+(soft-gen)*np.exp(-distance[None,:,None]/180)
  out[:,x0:x1]=filtered*(1-w[None,:,None])+borrowed*w[None,:,None]
  records.append(dict(label=label,side=side,edge=edge,generated_domain=[x0,0,span,1440],support_width=support,source_patch_bounds=[edge,edge+support] if side=='left' else [edge-support,edge],fade=fade,gaussian_radius=1.8,source_patch='material only, no graphics; at most48HD columns of single reflected support, then edge hold; quadratic generated-side fade; no repeated patch cycles'))
 out=np.rint(out).clip(0,255).astype('uint8');assert np.array_equal(out[:,1600:right],a[:,1600:right].astype('uint8'))
 Image.fromarray(out).save(p/(label+'-transition-proof.png'))
 for side,edge in [('left',1600),('right',right)]:Image.fromarray(out).crop((edge-384,0,edge+384,1440)).save(p/(label+'-'+side+'-transition-proof.png'))
(p/'transition-receipt.json').write_text(json.dumps(records,indent=2)+'\n')
