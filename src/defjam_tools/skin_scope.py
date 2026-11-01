"""Rasterize an anatomical skin scope without selecting triangles by centroid.

World/UV planes clip each source triangle with interpolated UV coordinates.
Explicit small source islands may be unioned by RM/triangle identity. Callers
still intersect material/approved-region holds before editing atlas pixels.
"""
import numpy as np
from PIL import Image,ImageDraw


def clip(vertices,axis,limit,above):
    if not vertices:return []
    out=[];a=vertices[-1];inside_a=a[axis]>=limit if above else a[axis]<=limit
    for b in vertices:
        inside_b=b[axis]>=limit if above else b[axis]<=limit
        if inside_a!=inside_b:
            t=(limit-a[axis])/(b[axis]-a[axis]);out.append(a+(b-a)*t)
        if inside_b:out.append(b)
        a=b;inside_a=inside_b
    return out


def rasterize(geometry,size,planes,extra_triangles=None):
    if geometry.get('schema')!=1 or type(size)!=int or not 8<=size<=2048:
        raise ValueError('Use schema1 geometry and valid raster size')
    if any(type(axis)!=int or not 0<=axis<5 or not np.isfinite(limit) or type(above)!=bool
           for axis,limit,above in planes):raise ValueError('Invalid clipping plane')
    extra_triangles=extra_triangles or {}
    image=Image.new('L',(size,size));draw=ImageDraw.Draw(image);contributors=[]
    for mesh in geometry.get('meshes',[]):
        if not mesh['group'].startswith('emc2_skin'):continue
        pos,uv,indices=mesh['positions'],mesh['uv'],mesh['indices']
        if len(pos)!=len(uv) or len(indices)%3:raise ValueError('Invalid triangle arrays')
        extras=set(extra_triangles.get(mesh['rm'],[]))
        if any(type(i)!=int or not 0<=i<len(indices)//3 for i in extras):raise ValueError('Invalid extra triangle')
        used=[]
        for at in range(0,len(indices),3):
            ids=indices[at:at+3]
            if any(type(i)!=int or not 0<=i<len(uv) for i in ids):raise ValueError('Invalid triangle index')
            polygon=[np.asarray([*pos[i],*uv[i]],dtype=float) for i in ids]
            if any(p.shape!=(5,) or not np.isfinite(p).all() or np.any((p[3:]<0)|(p[3:]>1)) for p in polygon):
                raise ValueError('Invalid position/UV coordinate')
            if at//3 not in extras:
                for axis,limit,above in planes:polygon=clip(polygon,axis,limit,above)
            if len(polygon)<3:continue
            draw.polygon([tuple(p[3:]*size) for p in polygon],fill=255);used.append(at//3)
        if used:contributors.append(dict(rm=mesh['rm'],triangles=used))
    return np.asarray(image)>0,contributors
