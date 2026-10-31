"""Mechanical native-canvas registration of approved raster masters.

No image generation, font substitution, colour correction or sharpening. Callers
own immutable source/approval hashes, source UV geometry and output staging.
"""
from __future__ import annotations
import numpy as np
from PIL import Image


def ink_bounds(image, threshold=128):
    return image.getchannel('A').point(lambda v: 255 if v >= threshold else 0).getbbox()


def fit_canvas(raw, native_size, source_bounds, scale=4):
    """Fit once in logical source space, before splitting a multi-material word."""
    raw = raw.convert('RGBA')
    db = ink_bounds(raw)
    if not db or len(source_bounds) != 4 or scale < 1:
        raise ValueError('Nonempty raw ink and valid source bounds required')
    ob = tuple(float(v)*scale for v in source_bounds)
    if ob[2] <= ob[0] or ob[3] <= ob[1]:
        raise ValueError('Empty source bounds')
    sx = (ob[2]-ob[0])/(db[2]-db[0]); sy = (ob[3]-ob[1])/(db[3]-db[1])
    soft = raw.getchannel('A').getbbox()
    patch = raw.crop(soft)
    size = (max(1,round(patch.width*sx)), max(1,round(patch.height*sy)))
    pos = (round(ob[0]+(soft[0]-db[0])*sx), round(ob[1]+(soft[1]-db[1])*sy))
    patch = patch.resize(size, Image.Resampling.LANCZOS)
    canvas = Image.new('RGBA', tuple(round(v*scale) for v in native_size))
    arr = np.asarray(patch)
    xx0=max(0,-pos[0]); yy0=max(0,-pos[1]); xx1=min(size[0],canvas.width-pos[0]); yy1=min(size[1],canvas.height-pos[1])
    clipped = np.ones(arr.shape[:2],bool)
    if xx1>xx0 and yy1>yy0:clipped[yy0:yy1,xx0:xx1]=False
    alpha = arr[:,:,3][clipped]
    canvas.paste(patch,pos)
    return canvas, dict(raw_bounds=list(db),source_bounds=list(source_bounds),scale_xy=[sx,sy],
                        resized=list(size),paste_xy=list(pos),max_clipped_alpha=int(alpha.max()) if alpha.size else 0,
                        visible_clipped_texels=int((alpha>=128).sum()),rounding_policy='One shared resize and rounded placement at final resolution')


def material_patch(atlas, rendered, source_rect, joined_rect, scale=4):
    """Copy exact rendered joined pixels into the original native UV rectangle."""
    sr=tuple(round(v*scale) for v in source_rect); jr=tuple(round(v*scale) for v in joined_rect)
    if sr[2]-sr[0] != jr[2]-jr[0] or sr[3]-sr[1] != jr[3]-jr[1]:
        raise ValueError('Source and logical material extents differ')
    if not (0<=sr[0]<sr[2]<=atlas.width and 0<=sr[1]<sr[3]<=atlas.height):
        raise ValueError('Material rectangle outside native atlas')
    result=atlas.copy();result.paste(rendered.crop(jr),sr[:2])
    # Exact region insertion: never independently scale adjoining pieces.
    if result.crop(sr).tobytes()!=rendered.crop(jr).tobytes():raise ValueError('Material copy changed pixels')
    return result


def repeated_guard(source, atlas, source_rect, scale=4):
    """Refresh one-texel repeated native gutters only where source proves repetition.

    Unrelated atlas content and transparent source gaps remain unchanged.
    """
    a=np.asarray(source.convert('RGBA'));out=np.array(atlas.convert('RGBA'));x0,y0,x1,y1=source_rect
    changed=0
    for y in range(max(0,y0-1),min(a.shape[0],y1+1)):
        for x in range(max(0,x0-1),min(a.shape[1],x1+1)):
            if x0<=x<x1 and y0<=y<y1:continue
            cx=min(max(x,x0),x1-1);cy=min(max(y,y0),y1-1)
            if not np.array_equal(a[y,x],a[cy,cx]):continue
            # A true repeated source texel receives the corresponding new edge block.
            block=out[cy*scale:(cy+1)*scale,cx*scale:(cx+1)*scale].copy()
            if x<x0:block=np.repeat(block[:,:1],scale,axis=1)
            if x>=x1:block=np.repeat(block[:,-1:],scale,axis=1)
            if y<y0:block=np.repeat(block[:1,:],scale,axis=0)
            if y>=y1:block=np.repeat(block[-1:,:],scale,axis=0)
            out[y*scale:(y+1)*scale,x*scale:(x+1)*scale]=block;changed+=1
    return Image.fromarray(out),changed


def ranges(occupied):
    indices=np.flatnonzero(occupied)
    return [(int(s[0]),int(s[-1]+1)) for s in np.split(indices,np.flatnonzero(np.diff(indices)>1)+1) if len(s)]


def glyph_cells(image, threshold=64):
    """Read ordered occupied rows/columns, including detached accents in each row."""
    mask=np.asarray(image.convert('RGBA'))[:,:,3]>=threshold;rows=[]
    for y0,y1 in ranges(mask.any(axis=1)):
        row=[]
        for x0,x1 in ranges(mask[y0:y1].any(axis=0)):
            yy=np.flatnonzero(mask[y0:y1,x0:x1].any(axis=1))
            row.append((x0,y0+int(yy[0]),x1,y0+int(yy[-1])+1))
        rows.append(row)
    return rows


def register_glyph_page(source, raw, scale=4):
    """Register each approved glyph to its original cell, without retyping text."""
    source=source.convert('RGBA');raw=raw.convert('RGBA');old=glyph_cells(source);new=glyph_cells(raw)
    if [len(r) for r in old]!=[len(r) for r in new]:
        raise ValueError('Glyph row/count mismatch; explicit source mapping required')
    if not old:raise ValueError('Empty glyph page')
    canvas=Image.new('RGBA',(source.width*scale,source.height*scale));records=[]
    old_rows=[(min(b[1] for b in row),max(b[3] for b in row)) for row in old]
    new_rows=[(min(b[1] for b in row),max(b[3] for b in row)) for row in new]
    for ri,(sr,rr) in enumerate(zip(old,new)):
        for ci,(sb,rb) in enumerate(zip(sr,rr)):
            # Half-gap cell boundaries partition each row; detached accents stay inside.
            source_cell=[0 if ci==0 else (sr[ci-1][2]+sb[0])//2,
                         0 if ri==0 else (old_rows[ri-1][1]+old_rows[ri][0])//2,
                         source.width if ci==len(sr)-1 else (sb[2]+sr[ci+1][0])//2,
                         source.height if ri==len(old)-1 else (old_rows[ri][1]+old_rows[ri+1][0])//2]
            raw_cell=[0 if ci==0 else (rr[ci-1][2]+rb[0])//2,
                      0 if ri==0 else (new_rows[ri-1][1]+new_rows[ri][0])//2,
                      raw.width if ci==len(rr)-1 else (rb[2]+rr[ci+1][0])//2,
                      raw.height if ri==len(new)-1 else (new_rows[ri][1]+new_rows[ri+1][0])//2]
            glyph=raw.crop(raw_cell);local=[rb[0]-raw_cell[0],rb[1]-raw_cell[1],rb[2]-raw_cell[0],rb[3]-raw_cell[1]]
            # Fit threshold64 bounds consistently, while preserving actual raw RGBA.
            sx=(sb[2]-sb[0])*scale/(rb[2]-rb[0]);sy=(sb[3]-sb[1])*scale/(rb[3]-rb[1])
            resized=glyph.resize((max(1,round(glyph.width*sx)),max(1,round(glyph.height*sy))),Image.Resampling.LANCZOS)
            pos=(round(sb[0]*scale-local[0]*sx),round(sb[1]*scale-local[1]*sy))
            cell=tuple(v*scale for v in source_cell);patch=Image.new('RGBA',(cell[2]-cell[0],cell[3]-cell[1]));patch.paste(resized,(pos[0]-cell[0],pos[1]-cell[1]));canvas.paste(patch,cell[:2])
            records.append(dict(row=ri,column=ci,source_bounds=list(sb),raw_bounds=list(rb),source_cell=source_cell,raw_cell=raw_cell,scale_xy=[sx,sy]))
    return canvas,dict(glyph_count=len(records),row_counts=[len(row) for row in old],method='Ordered one-to-one alpha occupancy registration; source positions, glyph extents and row baselines retained; no OCR/typeface substitution',glyphs=records)


def preserve_gray_marks(source, atlas, scale=4):
    """Retain proven opaque RGB127 runtime marks; do not reinterpret them as holes."""
    source=source.convert('RGBA');a=np.asarray(source);mask=(a[:,:,3]==255)&np.all(a[:,:,:3]==127,axis=2)
    mask=np.repeat(np.repeat(mask,scale,axis=0),scale,axis=1)
    if atlas.size!=(source.width*scale,source.height*scale):raise ValueError('Gray-mark native size mismatch')
    out=np.array(atlas);native=np.asarray(source.resize(atlas.size,Image.Resampling.NEAREST));out[mask]=native[mask]
    return Image.fromarray(out),int(mask.sum())
