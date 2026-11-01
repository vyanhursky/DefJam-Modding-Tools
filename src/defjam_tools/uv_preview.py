"""Offline orthographic source-UV diagnostic, not a game-shader preview.

RGB is sampled independently of alpha to inspect split texture features. No
geometry/UVs are changed. Use the live model viewer for actual alpha materials.
"""
import numpy as np
from PIL import Image


def render(geometry,texture,view='front',bounds=None,size=(512,768),groups=()):
    if view not in ('front','back') or geometry.get('schema')!=1:
        raise ValueError('Use schema1 geometry and front/back view')
    width,height=size
    if not all(type(v)==int and 8<=v<=2048 for v in size):raise ValueError('Invalid diagnostic dimensions')
    if bounds is None:
        lo,hi=geometry['bounds'];pad=(hi[1]-lo[1])*.04
        cx,cy=(lo[0]+hi[0])/2,(lo[1]+hi[1])/2
        sx,sy=hi[0]-lo[0]+2*pad,hi[1]-lo[1]+2*pad
        if sx/sy>width/height:sy=sx*height/width
        else:sx=sy*width/height
        bounds=(cx-sx/2,cy-sy/2,cx+sx/2,cy+sy/2)
    xmin,ymin,xmax,ymax=bounds
    if not np.isfinite(bounds).all() or xmin>=xmax or ymin>=ymax:raise ValueError('Invalid diagnostic bounds')
    source=np.asarray(texture.convert('RGB'));out=np.empty((height,width,3),dtype='uint8');out[:]=[33,41,31]
    depth=np.full((height,width),-np.inf);sign=1 if view=='front' else -1
    for mesh in geometry['meshes']:
        if groups and not any(mesh['group'].startswith(g) for g in groups):continue
        pos=np.asarray(mesh['positions']);uv=np.asarray(mesh['uv']);idx=mesh['indices']
        for at in range(0,len(idx),3):
            ids=idx[at:at+3];p=pos[ids];u=uv[ids]
            xx=(p[:,0]-xmin)/(xmax-xmin)*width
            if sign<0:xx=width-xx
            yy=(ymax-p[:,1])/(ymax-ymin)*height
            lo=np.maximum(np.floor([xx.min(),yy.min()]).astype(int),0);hi=np.minimum(np.ceil([xx.max(),yy.max()]).astype(int),[width,height])
            if np.any(hi<=lo):continue
            d=(yy[1]-yy[2])*(xx[0]-xx[2])+(xx[2]-xx[1])*(yy[0]-yy[2])
            if abs(d)<1e-9:continue
            y,x=np.mgrid[lo[1]:hi[1],lo[0]:hi[0]];x=x+.5;y=y+.5
            a=((yy[1]-yy[2])*(x-xx[2])+(xx[2]-xx[1])*(y-yy[2]))/d
            b=((yy[2]-yy[0])*(x-xx[2])+(xx[0]-xx[2])*(y-yy[2]))/d;c=1-a-b
            z=(a*p[0,2]+b*p[1,2]+c*p[2,2])*sign
            patch=depth[lo[1]:hi[1],lo[0]:hi[0]];active=(a>=-1e-7)&(b>=-1e-7)&(c>=-1e-7)&(z>patch)
            if not active.any():continue
            tex=a[...,None]*u[0]+b[...,None]*u[1]+c[...,None]*u[2]
            tx=np.clip((tex[...,0]*source.shape[1]).astype(int),0,source.shape[1]-1);ty=np.clip((tex[...,1]*source.shape[0]).astype(int),0,source.shape[0]-1)
            tile=out[lo[1]:hi[1],lo[0]:hi[0]];tile[active]=source[ty[active],tx[active]];patch[active]=z[active]
    return Image.fromarray(out)
