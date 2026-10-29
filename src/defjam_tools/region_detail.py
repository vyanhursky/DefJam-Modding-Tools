"""Assemble localized imagegen studies under source UV and current-parent holds.

Material grain transfers luminance detail only. Direct crops retain the source
coarse palette; source-locked crops transfer small luminance residuals only into
existing dark ink interiors. These checks cannot establish tattoo authenticity.
"""
import numpy as np
from PIL import Image
from . import face_detail
from .color_trial import rgb_to_lab, lab_to_rgb, box_blur

VERSION = 1


def validate(parent, mask, guard):
    shape = (parent.height, parent.width)
    if parent.mode != 'RGBA' or mask.shape != shape or mask.dtype != bool:
        raise ValueError('Use RGBA parent and same-size boolean edit mask')
    if guard.shape != shape or not np.isfinite(guard).all() or np.any((guard<0)|(guard>1)):
        raise ValueError('Invalid seam guard')


def hold_regions(mask, boxes):
    result = mask.copy()
    h, w = mask.shape
    for x0,y0,x1,y1 in boxes:
        if not 0<=x0<x1<=w or not 0<=y0<y1<=h:
            raise ValueError('Hold outside atlas')
        result[y0:y1,x0:x1] = False
    return result


def finish(before, out, allowed, guard):
    checks = dict(alpha_exact=bool(np.array_equal(out[...,3],before[...,3])),
                  outside_edit_mask_exact=bool(np.array_equal(out[~allowed],before[~allowed])),
                  seam_core_exact=bool(np.array_equal(out[guard>=1],before[guard>=1])))
    if not all(checks.values()):
        raise ValueError('Regional assembly invariant failed')
    return dict(checks=checks,changed_pixels=int(np.any(out!=before,axis=-1).sum()))


def grain(parent, generated_swatch, mask, guard, held_boxes=(), amplitude=.8):
    validate(parent,mask,guard)
    if not 0<amplitude<=2:
        raise ValueError('Invalid grain amplitude')
    allowed = hold_regions(mask,held_boxes)
    before = np.asarray(parent)
    sample = rgb_to_lab(np.asarray(generated_swatch.convert('RGB').resize(parent.size,Image.Resampling.LANCZOS)))[...,0]
    smooth = sample
    for _ in range(3): smooth=box_blur(smooth,8)
    residual = np.clip(sample-smooth,-3,3)
    lab = rgb_to_lab(before[...,:3])
    # Dark ink is held; source chroma and broad lighting are never replaced by
    # the generated sample's orange/tan base color.
    weight = np.clip((lab[...,0]-28)/20,0,1)*(1-guard)*allowed
    edited = lab.copy(); edited[...,0] += amplitude*residual*weight
    rgb,_ = lab_to_rgb(edited)
    out=before.copy();active=weight>0;out[active,:3]=rgb[active]
    report=finish(before,out,allowed,guard)
    report.update(version=VERSION,method='generated material luminance residual',amplitude=amplitude,
                  chroma_shift=0,held_boxes=[list(b) for b in held_boxes])
    return Image.fromarray(out),report


def patch(reference,parent,generated,box,mask,guard,held_boxes=(),method='direct',strength=.8):
    validate(parent,mask,guard)
    if method not in ('direct','source-locked'):
        raise ValueError('Unknown crop assembly method')
    x0,y0,x1,y1=box
    if not 0<=x0<x1<=parent.width or not 0<=y0<y1<=parent.height or not 0<strength<=1:
        raise ValueError('Invalid crop box or detail strength')
    generated_size=list(generated.size)
    aspect_error=abs(generated.width*(y1-y0)/(generated.height*(x1-x0))-1)
    if aspect_error>.005:
        raise ValueError('Generated crop aspect ratio changed')
    # Built-in outputs sometimes round an edge by a pixel. Normalize only that
    # small rounding error, never silently stretch a differently framed study.
    if aspect_error:
        generated=generated.resize((x1-x0,y1-y0),Image.Resampling.LANCZOS)
    allowed=hold_regions(mask,held_boxes)
    crop_mask=np.zeros_like(mask);crop_mask[y0:y1,x0:x1]=True;allowed &= crop_mask
    if method=='direct':
        # A prompt is not a lock: all other materials, source letters and the
        # current head/body seam are protected by the actual weight field.
        result,detail=face_detail.merge(reference,parent,generated,box,
                                        guard=np.maximum(guard,~allowed),strength=strength)
        report=finish(np.asarray(parent),np.asarray(result),allowed,guard)
        report.update(detail=detail)
    else:
        if reference.mode!='RGBA' or reference.size!=parent.size or not np.array_equal(np.asarray(reference)[...,3],np.asarray(parent)[...,3]):
            raise ValueError('Reference/parent alpha or dimensions differ')
        before=np.asarray(parent);out=before.copy()
        raw=rgb_to_lab(np.asarray(generated.convert('RGB').resize((x1-x0,y1-y0),Image.Resampling.LANCZOS)))[...,0]
        residual=np.clip(raw-box_blur(box_blur(raw,2),2),-3,3)
        lab=rgb_to_lab(before[y0:y1,x0:x1,:3])
        # Only inside original ink; never stamp a shifted/new generated contour
        # or replace source lettering with guessed words.
        weight=allowed[y0:y1,x0:x1]*(1-guard[y0:y1,x0:x1])*(lab[...,0]<32)*strength
        edited=lab.copy();edited[...,0]+=residual*weight
        rgb,_=lab_to_rgb(edited);active=weight>0
        tile=out[y0:y1,x0:x1,:3];tile[active]=rgb[active]
        report=finish(before,out,allowed,guard)
        report['ink_interior_pixels']=int(active.sum())
        result=Image.fromarray(out)
    report.update(version=VERSION,method=method,box=list(box),held_boxes=[list(b) for b in held_boxes],
                  generated_size=generated_size,aspect_rounding_error=aspect_error,visual_review_required=True)
    return result,report
