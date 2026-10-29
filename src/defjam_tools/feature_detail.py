"""Restore a named logo/prop crop under an audited material mask.

Keep the parent outside scope and its alpha exact. Source low-frequency Lab
color controls the result while generated fine detail remains. Mask feathering
works at an atlas edge too; it never imposes a second rectangular crop-edge
hold that could silently exclude a cropped chest emblem. No art approval.
"""
import numpy as np
from PIL import Image, ImageFilter
from .color_trial import rgb_to_lab, lab_to_rgb, box_blur

VERSION=1


def restore(reference,parent,generated,box,mask,source_size=512,radius_source=8,
            feather_source=1.5,strength=1.):
    if (reference.mode!='RGBA' or parent.mode!='RGBA' or reference.size!=parent.size
            or reference.width!=reference.height or not isinstance(source_size,int)
            or source_size<8 or reference.width%source_size):
        raise ValueError('Use equal square RGBA atlases at an integer source scale')
    if mask.dtype!=bool or mask.shape!=(parent.height,parent.width):
        raise ValueError('Use same-size boolean material/feature mask')
    if not 0<strength<=1 or radius_source<1 or feather_source<0:
        raise ValueError('Invalid detail correction parameters')
    x0,y0,x1,y1=box
    if not 0<=x0<x1<=parent.width or not 0<=y0<y1<=parent.height:
        raise ValueError('Feature crop outside atlas')
    width,height=x1-x0,y1-y0
    error=abs(generated.width*height/(generated.height*width)-1)
    if error>.005:raise ValueError('Generated crop aspect ratio changed')
    before=np.asarray(parent);ref=np.asarray(reference)
    if not np.array_equal(before[...,3],ref[...,3]):
        raise ValueError('Parent/source material alpha differs')
    allowed=mask.copy();allowed[:y0]=False;allowed[y1:]=False;allowed[:,:x0]=False;allowed[:,x1:]=False
    if not allowed.any():raise ValueError('No safe feature pixels')
    scale=parent.width//source_size
    raw=rgb_to_lab(np.asarray(generated.convert('RGB').resize((width,height),Image.Resampling.LANCZOS)))
    target=rgb_to_lab(ref[y0:y1,x0:x1,:3]);drift=raw-target
    radius=max(1,round(radius_source*scale))
    for _ in range(3):drift=box_blur(drift,radius)
    rgb,clipped=lab_to_rgb(raw-drift)
    weight=allowed.astype(float)
    if feather_source:
        blurred=np.asarray(Image.fromarray((allowed*255).astype('uint8')).filter(
            ImageFilter.GaussianBlur(feather_source*scale)),dtype=float)/255
        weight*=np.clip((blurred-.5)*2,0,1)
    weight=weight[y0:y1,x0:x1]*strength
    out=before.copy();active=weight>0
    tile=out[y0:y1,x0:x1,:3];prior=before[y0:y1,x0:x1,:3]
    blended=np.rint(prior*(1-weight[...,None])+rgb*weight[...,None]).astype('uint8')
    tile[active]=blended[active]
    changed=np.any(out!=before,axis=-1)
    if not changed.any():raise ValueError('Named feature remains unchanged/held')
    checks=dict(alpha_exact=bool(np.array_equal(out[...,3],before[...,3])),
                outside_feature_exact=bool(np.array_equal(out[~allowed],before[~allowed])))
    if not all(checks.values()):raise ValueError('Feature assembly invariant failed')
    return Image.fromarray(out),dict(version=VERSION,box=list(box),source_size=source_size,
        radius_source=radius_source,feather_source=feather_source,strength=strength,
        aspect_rounding_error=error,safe_pixels=int(allowed.sum()),changed_pixels=int(changed.sum()),
        gamut_clipped_active_pixels=int((clipped&active).sum()),checks=checks,visual_review_required=True)
