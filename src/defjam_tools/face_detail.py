"""Assemble an owner-authorized imagegen face patch without recoloring the atlas.

This is post-generation technical assembly, not a face generator. It keeps
source low-frequency color/shading, parent pixels outside the edit box, material
alpha, held eye/mouth tiles and verified UV seam cores. Likeness still requires
human review; pixel invariants do not establish anatomical fidelity.
"""
import numpy as np
from PIL import Image
from .color_trial import rgb_to_lab, lab_to_rgb, box_blur

VERSION = 1


def merge(reference, parent, generated, box, held_boxes=(), guard=None,
          strength=.55, radius=12, edge=24):
    if reference.size != parent.size or reference.mode != 'RGBA' or parent.mode != 'RGBA':
        raise ValueError('Use equal-size RGBA reference and parent atlases')
    if not 0 < strength <= 1 or not isinstance(radius, int) or radius < 1 or edge < 1:
        raise ValueError('Invalid detail assembly parameters')
    x0,y0,x1,y1=box; width,height=x1-x0,y1-y0
    if min(x0,y0)<0 or x1>parent.width or y1>parent.height or min(width,height)<=2*edge:
        raise ValueError('Invalid face patch box')
    if generated.width*height != generated.height*width:
        raise ValueError('Generated face patch aspect ratio changed')
    ref=np.asarray(reference); prior=np.asarray(parent)
    if not np.array_equal(ref[...,3],prior[...,3]):
        raise ValueError('Parent material alpha differs from reference')
    target=rgb_to_lab(ref[y0:y1,x0:x1,:3])
    raw=rgb_to_lab(np.asarray(generated.convert('RGB').resize((width,height),Image.Resampling.LANCZOS)))
    # Match broad source hue/shading locally; retain generated fine detail.
    drift=raw-target
    for _ in range(3): drift=box_blur(drift,radius)
    corrected,_=lab_to_rgb(raw-drift)
    yy,xx=np.mgrid[:height,:width]
    distance=np.minimum.reduce([xx,yy,width-1-xx,height-1-yy])
    weight=np.clip(distance/edge,0,1)*strength
    if guard is not None:
        if guard.shape != (parent.height,parent.width) or not np.isfinite(guard).all() or np.any((guard<0)|(guard>1)):
            raise ValueError('Invalid verified seam guard')
        weight*=1-guard[y0:y1,x0:x1]
    for a,b,c,d in held_boxes:
        if min(a,b)<0 or c>width or d>height or c<=a or d<=b:
            raise ValueError('Held tile is outside the face patch')
        weight[b:d,a:c]=0
    out=prior.copy()
    out[y0:y1,x0:x1,:3]=np.rint(prior[y0:y1,x0:x1,:3]*(1-weight[...,None])+corrected*weight[...,None]).astype(np.uint8)
    outside=np.ones(prior.shape[:2],dtype=bool);outside[y0:y1,x0:x1]=False
    checks={'alpha_exact':bool(np.array_equal(out[...,3],prior[...,3])),
            'outside_patch_exact':bool(np.array_equal(out[outside],prior[outside])),
            'held_pixels_exact':bool(np.array_equal(out[y0:y1,x0:x1][weight==0],prior[y0:y1,x0:x1][weight==0]))}
    if not all(checks.values()):raise ValueError('Face assembly invariant failed')
    report=dict(version=VERSION,box=list(box),held_boxes=[list(b) for b in held_boxes],
                strength=strength,radius=radius,blur_passes=3,edge=edge,
                generated_size=list(generated.size),checks=checks,
                edited_pixels=int(np.count_nonzero(np.any(out!=prior,axis=-1))),
                likeness_review_required=True)
    return Image.fromarray(out),report
