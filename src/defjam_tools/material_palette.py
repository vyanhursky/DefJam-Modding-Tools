"""Source-palette matching for cloth, footwear and headwear after imagegen.

Derive coverage from source UV triangles; hold all other materials plus one
source texel. A masked local Lab drift field restores broad color/shading while
retaining fine generated texture. No skin calibration heuristics are reused.
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from .color_trial import rgb_to_lab, lab_to_rgb, box_blur, components, resize_float
from .fighter_scopes import bounded_uv_triangle

VERSION=1


def clothing_mask(geometry,size):
    if geometry.get('schema')!=1 or not isinstance(size,int) or not 8<=size<=2048:
        raise ValueError('Use schema1 geometry and analysis size8..2048')
    cloth=Image.new('L',(size,size));other=Image.new('L',(size,size))
    found=False
    for mesh in geometry.get('meshes',[]):
        is_cloth=mesh['group'].startswith('emc4_cloth');found|=is_cloth
        draw=ImageDraw.Draw(cloth if is_cloth else other);uv=mesh['uv'];indices=mesh['indices']
        if len(indices)%3:raise ValueError('Incomplete triangle')
        for at in range(0,len(indices),3):
            tri=indices[at:at+3]
            if any(type(i)!=int or not 0<=i<len(uv) for i in tri):raise ValueError('Bad UV index')
            points=bounded_uv_triangle([uv[i] for i in tri],size)
            draw.polygon([tuple(p*size) for p in points],fill=255)
    if not found:raise ValueError('No source clothing material')
    coverage=np.asarray(cloth)>0;held=np.asarray(other.filter(ImageFilter.MaxFilter(3)))>0
    return coverage&~held,held,coverage


def match(reference,parent,geometry,source_size=512,radius=6):
    if reference.mode!='RGBA' or parent.mode!='RGBA' or reference.size!=parent.size or reference.width!=reference.height:
        raise ValueError('Use equal square RGBA atlases')
    if reference.width%source_size or reference.width>4096 or radius<1:
        raise ValueError('Invalid source scale or radius')
    ref=np.asarray(reference);raw=np.asarray(parent)
    if not np.array_equal(ref[...,3],raw[...,3]):raise ValueError('Material alpha differs from reference')
    editable,held,coverage=clothing_mask(geometry,source_size)
    if not editable.any():raise ValueError('No unshared clothing pixels')
    lowref=rgb_to_lab(np.asarray(reference.convert('RGB').resize((source_size,source_size),Image.Resampling.LANCZOS)))
    lowraw=rgb_to_lab(np.asarray(parent.convert('RGB').resize((source_size,source_size),Image.Resampling.LANCZOS)))
    delta=lowref-lowraw;field=np.zeros_like(delta);parts=0
    for points in components(editable):
        ys,xs=points.T;y0,y1=int(ys.min()),int(ys.max())+1;x0,x1=int(xs.min()),int(xs.max())+1
        mask=np.zeros((y1-y0,x1-x0));mask[ys-y0,xs-x0]=1
        local=delta[y0:y1,x0:x1];anchor=np.median(delta[ys,xs],axis=0)
        local=np.clip(local,anchor-[12,16,16],anchor+[12,16,16])
        numerator=local*mask[...,None];denominator=mask
        for _ in range(3):numerator=box_blur(numerator,radius);denominator=box_blur(denominator,radius)
        values=np.divide(numerator,denominator[...,None],out=np.broadcast_to(anchor,local.shape).copy(),where=denominator[...,None]>.001)
        field[ys,xs]=values[ys-y0,xs-x0];parts+=1
    size=parent.size
    # Normalize interpolation at mask boundaries; do not attenuate corrections
    # by mixing zero fields from protected neighboring materials.
    smooth_weight=resize_float(editable.astype(float),size)
    shift=np.divide(resize_float(field,size),np.maximum(smooth_weight[...,None],1e-8))
    maskhd=resize_float(editable.astype(float),size,Image.Resampling.NEAREST)>0
    rgb,clipped=lab_to_rgb(rgb_to_lab(raw[...,:3])+shift)
    out=raw.copy();out[maskhd,:3]=rgb[maskhd]
    checks=dict(alpha_exact=bool(np.array_equal(out[...,3],raw[...,3])),
                outside_clothing_exact=bool(np.array_equal(out[~maskhd],raw[~maskhd])))
    if not all(checks.values()):raise ValueError('Clothing palette invariant failed')
    result=Image.fromarray(out)
    lowout=rgb_to_lab(np.asarray(result.convert('RGB').resize((source_size,source_size),Image.Resampling.LANCZOS)))
    report=dict(version=VERSION,source_size=source_size,radius=radius,blur_passes=3,components=parts,
                analysis_pixels=int(editable.sum()),held_overlap_pixels=int((coverage&held).sum()),
                edited_pixels=int(np.count_nonzero(np.any(out!=raw,axis=-1))),
                median_Lab_distance_before=float(np.median(np.linalg.norm(lowraw[editable]-lowref[editable],axis=-1))),
                median_Lab_distance_after=float(np.median(np.linalg.norm(lowout[editable]-lowref[editable],axis=-1))),
                median_chroma_reference=float(np.median(np.linalg.norm(lowref[editable,1:],axis=-1))),
                median_chroma_before=float(np.median(np.linalg.norm(lowraw[editable,1:],axis=-1))),
                median_chroma_after=float(np.median(np.linalg.norm(lowout[editable,1:],axis=-1))),
                gamut_clipped_pixels=int(np.count_nonzero(clipped&maskhd)),checks=checks)
    return result,report,Image.fromarray(maskhd.astype(np.uint8)*255)
