"""Register authentic alpha to generated artwork with local grayscale block matching.

Private technical prototype. Source alpha is independently authored coverage,
not a black/green color key. No source, raw or approved asset is overwritten.
"""
from pathlib import Path
import numpy as np,json
from PIL import Image,ImageFilter
p=Path(__file__).resolve().parent;b=p.parent/'branding-v1'
def blur(x,r):
 z=np.pad(x,((r,r),(r,r)),mode='edge');i=np.pad(z,((1,0),(1,0))).cumsum(0).cumsum(1);n=2*r+1
 return (i[n:,n:]-i[:-n,n:]-i[n:,:-n]+i[:-n,:-n])/(n*n)
def warp(x,u,v):
 yy,xx=np.indices(u.shape);xx=np.clip(xx+u,0,x.shape[1]-1.001);yy=np.clip(yy+v,0,x.shape[0]-1.001);xi=xx.astype(int);yi=yy.astype(int);fx=xx-xi;fy=yy-yi
 return x[yi,xi]*(1-fx)*(1-fy)+x[yi,xi+1]*fx*(1-fy)+x[yi+1,xi]*(1-fx)*fy+x[yi+1,xi+1]*fx*fy
def scale(x,size):return np.array(Image.fromarray(x.astype('float32'),'F').resize(size,Image.Resampling.BILINEAR))
def register(label):
 raw=Image.open(b/(label+'-raw.png')).convert('RGBA');ref=Image.open(p/(label+'-mapped-source.png')).convert('RGBA')
 a=np.array(raw).astype('float32');s=np.array(ref).astype('float32')
 # Structural material appearance, no source filler RGB enters the registration.
 sr=np.clip((s[:,:,:3].mean(2)-35)/140,0,1)*s[:,:,3]/255
 tr=np.clip((a[:,:,:3].mean(2)-35)/140,0,1)*a[:,:,3]/255
 u=v=None
 for maxdim in [96,192,384]:
  size=tuple(max(12,round(d*maxdim/max(raw.size))) for d in raw.size);S=scale(sr,size);T=scale(tr,size)
  if u is None:u=np.zeros(T.shape,'float32');v=u.copy()
  else:
   rx=size[0]/u.shape[1];ry=size[1]/u.shape[0];u=scale(u,size)*rx;v=scale(v,size)*ry
  for iteration in range(3):
   best=np.full(T.shape,100.,'float32');du=np.zeros(T.shape,'float32');dv=du.copy()
   for dy in range(-3,4):
    for dx in range(-3,4):
     W=warp(S,u+dx,v+dy);cost=blur((W-T)**2,5)+.0007*(dx*dx+dy*dy)
     choose=cost<best;best[choose]=cost[choose];du[choose]=dx;dv[choose]=dy
   u=blur(u+du,3);v=blur(v+dv,3)
 full=(raw.width,raw.height);u=scale(u,full)*raw.width/u.shape[1];v=scale(v,full)*raw.height/v.shape[0]
 alpha=np.clip(np.rint(warp(s[:,:,3],u,v)),0,255).astype('uint8')
 Image.fromarray(alpha).save(p/(label+'-registered-alpha.png'));np.savez_compressed(p/(label+'-registration.npz'),u=u,v=v)
 out=raw.copy();out.putalpha(Image.fromarray(np.minimum(np.array(raw)[:,:,3],alpha)))
 bg=Image.new('RGBA',raw.size,(180,180,180,255));bg.alpha_composite(out);bg.convert('RGB').save(p/(label+'-registered-proof.jpg'))
 return dict(label=label,max_displacement=[float(abs(u).max()),float(abs(v).max())],mean_displacement=[float(abs(u).mean()),float(abs(v).mean())])
if __name__=='__main__':
 import sys
 labels=sys.argv[1:] or ['title-logo']+['emblem-'+s for s in ['story','battle','options','jukebox','extras','high-scores','rewards','credits']]
 records=[]
 for label in labels:
  r=register(label);records.append(r);print(r,flush=True)
 (p/'registration-receipt.json').write_text(json.dumps(records,indent=2)+'\n')
