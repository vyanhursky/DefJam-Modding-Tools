"""Measured fighter material/UV scopes and named-feature omission checks.

Explicit alpha-cloth RGB opt-in keeps source alpha separate. Other alpha/unknown
materials remain held. All paired UV seam evidence is per original geometry.
"""
from collections import defaultdict
import numpy as np
from PIL import Image,ImageDraw,ImageFilter

def scopes(geometry, size, editable_alpha_groups=()):
    actual={m['group'] for m in geometry['meshes']}
    if any(g not in actual or not g.startswith('emc4_cloth') for g in editable_alpha_groups):
        raise ValueError('Only explicit existing cloth alpha groups may restore RGB')
    groups={}
    edges=defaultdict(list)
    for mesh in geometry['meshes']:
        group=mesh['group'];canvas=groups.setdefault(group,Image.new('L',(size,size)))
        draw=ImageDraw.Draw(canvas);uv=mesh['uv'];pos=mesh['positions'];indices=mesh['indices']
        for at in range(0,len(indices),3):
            ids=indices[at:at+3]
            points=np.asarray([uv[i] for i in ids])
            if len(ids)!=3 or np.any(~np.isfinite(points)) or np.any((points<0)|(points>1)):
                raise ValueError('Invalid triangle UVs')
            draw.polygon([tuple(p*size) for p in points],fill=255)
            if not group.startswith('emc2_skin'):continue
            for a,b in zip(ids,ids[1:]+ids[:1]):
                pair=tuple(tuple(round(float(v),4) for v in pos[i]) for i in (a,b))
                tex=(uv[a],uv[b])
                if pair[0]==pair[1]:continue
                if pair[1]<pair[0]:pair=pair[::-1];tex=tex[::-1]
                edges[pair].append(tex)
    allowed=Image.new('L',(size,size));held=Image.new('L',(size,size));masks={}
    for group,canvas in groups.items():
        masks[group]=np.asarray(canvas)>0
        known=group.startswith(('emc2_skin','emc4_cloth','emc3_jewelry','nospec'))
        alpha='ALPHA' in group.upper() or 'MATALPH' in group.upper()
        target=allowed if known and (not alpha or group in editable_alpha_groups) else held
        target.paste(255,mask=canvas)
    # Material boundaries/eye-mouth-alpha tiles retain their source plus one
    # native texel. All unknown materials remain explicitly held.
    mask=(np.asarray(allowed)>0)&~(np.asarray(held.filter(ImageFilter.MaxFilter(3)))>0)
    seams=[];seen=set()
    for pair,items in edges.items():
        distinct=[]
        for tex in items:
            if not any(np.max(np.abs(np.asarray(tex)-old))*size<=1 for old in distinct):distinct.append(np.asarray(tex))
        if len(distinct)!=2:continue # absent/ambiguous weld is no seam guarantee
        for tex in distinct:
            key=tuple(map(tuple,tex))
            if key not in seen:seen.add(key);seams.append(dict(body=tex.tolist(),world_edge=pair))
    return mask,masks,seams



def feature_coverage(before,after,features,scale,minimum=.2):
    """Measure EACH declared feature/fragment, including any held pixels.

    This catches omission, not semantic authenticity or design fidelity. Final
    assembled feature crops and model front/back still require visual review.
    """
    if before.shape!=after.shape or before.ndim!=3 or scale<1:
        raise ValueError('Use equal arrays and positive source scale')
    changed=np.any(before!=after,axis=-1);reports=[]
    for feature in features:
        x0,y0,x1,y1=[v*scale for v in feature['source_box']]
        if not 0<=x0<x1<=before.shape[1] or not 0<=y0<y1<=before.shape[0]:raise ValueError('Feature outside atlas')
        fraction=float(changed[y0:y1,x0:x1].mean())
        status=feature.get('status','restore')
        if status not in ('restore','held'):raise ValueError('Unknown feature status')
        if status=='restore' and fraction<minimum:raise ValueError(feature['name']+' remains held/missing')
        reports.append(dict(name=feature['name'],source_box=feature['source_box'],status='pending-held' if status=='held' else 'detail-present-needs-review',changed_fraction=fraction))
    return reports


def include_unmapped_features(allowed,masks,regions):
    """Explicit RGB-only source tiles absent from this static model's UVs.

    Never use this to override a held mapped material. Alpha is still retained
    separately by assembly; static-model absence does not prove game non-use.
    """
    result=allowed.copy();covered=np.zeros_like(allowed)
    for mask in masks.values():covered|=mask
    h,w=allowed.shape
    for region in regions:
        x0,y0,x1,y1=region['source_box']
        if not region.get('reason') or not 0<=x0<x1<=w or not 0<=y0<y1<=h:
            raise ValueError('Declare exact unmapped source feature and reason')
        if covered[y0:y1,x0:x1].any():
            raise ValueError('Mapped feature must use its verified material scope')
        result[y0:y1,x0:x1]=True
    return result
