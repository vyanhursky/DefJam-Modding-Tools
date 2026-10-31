"""Local FP32 x4 RRDB inference, compatible with official RealESRNet_x4plus weights.

Independent inference graph implementation; architecture reference:
https://github.com/XPixelGroup/BasicSR/blob/master/basicsr/archs/rrdbnet_arch.py
Only torch primitives; strict checkpoint keys/shapes and weights_only loading.
No web/API/imagegen calls. RGB tiles have context padding; own alpha is separate.
"""
from pathlib import Path
import json,time,hashlib,argparse,sys
import numpy as np
from PIL import Image
import torch
from torch import nn
from torch.nn import functional as F
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'src'))
from defjam_tools.paths import require_private_output
CHECKPOINT_SHA='a820b9bde89a874d7599d545567308ce6c128fc8754a53208eda016d40aa81df'
class Dense(nn.Module):
 def __init__(self):
  super().__init__()
  for i in range(1,6):setattr(self,'conv'+str(i),nn.Conv2d(64+32*(i-1),32 if i<5 else 64,3,padding=1))
 def forward(self,x):
  terms=[x]
  for i in range(1,6):
   y=getattr(self,'conv'+str(i))(torch.cat(terms,1));terms.append(F.leaky_relu(y,.2) if i<5 else y)
  return x+.2*terms[-1]
class Residual(nn.Module):
 def __init__(self):
  super().__init__();self.rdb1=Dense();self.rdb2=Dense();self.rdb3=Dense()
 def forward(self,x):return x+.2*self.rdb3(self.rdb2(self.rdb1(x)))
class Network(nn.Module):
 def __init__(self):
  super().__init__();self.conv_first=nn.Conv2d(3,64,3,padding=1);self.body=nn.Sequential(*[Residual() for _ in range(23)])
  for key in ['conv_body','conv_up1','conv_up2','conv_hr']:setattr(self,key,nn.Conv2d(64,64,3,padding=1))
  self.conv_last=nn.Conv2d(64,3,3,padding=1)
 def forward(self,x):
  f=self.conv_first(x);f=f+self.conv_body(self.body(f))
  for op in [self.conv_up1,self.conv_up2]:f=F.leaky_relu(op(F.interpolate(f,scale_factor=2,mode='nearest')),.2)
  return self.conv_last(F.leaky_relu(self.conv_hr(f),.2))
def infer(model,image,device,tile=128,context=32):
 a=np.array(image.convert('RGB'),dtype=np.float32)/255.;h,w=a.shape[:2];out=np.zeros((h*4,w*4,3),np.uint8);tiles=[]
 with torch.inference_mode():
  for y in range(0,h,tile):
   for x in range(0,w,tile):
    x1,y1=min(x+tile,w),min(y+tile,h);l,t=max(0,x-context),max(0,y-context);r,b=min(w,x1+context),min(h,y1+context)
    v=torch.from_numpy(a[t:b,l:r].copy()).permute(2,0,1).unsqueeze(0).to(device);z=model(v).clamp(0,1).squeeze(0).permute(1,2,0).cpu().numpy();z=np.rint(z*255).astype(np.uint8)
    out[y*4:y1*4,x*4:x1*4]=z[(y-t)*4:(y1-t)*4,(x-l)*4:(x1-l)*4];tiles.append([x,y,x1,y1]);del v,z
 return Image.fromarray(out),tiles
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--plan',type=Path,required=True);ap.add_argument('--checkpoint',type=Path,required=True);ap.add_argument('--tile',type=int,default=128);args=ap.parse_args();torch.set_num_threads(4)
 if hashlib.sha256(args.checkpoint.read_bytes()).hexdigest()!=CHECKPOINT_SHA:raise ValueError('Official checkpoint fingerprint mismatch')
 device='mps' if torch.backends.mps.is_available() else 'cpu';model=Network();weights=torch.load(args.checkpoint,map_location='cpu',weights_only=True);model.load_state_dict(weights['params_ema'],strict=True);model.eval().to(device);print('MODEL strict702tensors',device,flush=True)
 plan=json.loads(args.plan.read_text());results=[]
 for r in plan['textures']:
  p=require_private_output(Path(r['raw_local_path']));p.parent.mkdir(exist_ok=True,parents=True)
  source_sha=hashlib.sha256(Path(r['original_path']).read_bytes()).hexdigest()
  if source_sha!=r['original_sha256']:raise ValueError('Original source fingerprint changed')
  if p.exists():
   cached=json.loads(p.with_suffix('.json').read_text())
   if (cached['raw_local_sha256']!=hashlib.sha256(p.read_bytes()).hexdigest() or cached['original_sha256']!=source_sha or cached['checkpoint_sha256']!=CHECKPOINT_SHA):raise ValueError('Cached inference changed; use a new stage')
   print('CACHED',r['key'],flush=True);continue
  start=time.monotonic();im=Image.open(r['original_path']);out,tiles=infer(model,im,device,args.tile);out.save(p)
  receipt=dict(key=r['key'],source_id=r['source_id'],original_sha256=hashlib.sha256(Path(r['original_path']).read_bytes()).hexdigest(),raw_local_path=str(p),raw_local_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),method='local RealESRNet_x4plus fixed-weight super-resolution; no ImageGen',device=device,precision='float32',torch=torch.__version__,numpy=np.__version__,tile=args.tile,context=32,tiles=tiles,checkpoint_sha256=hashlib.sha256(args.checkpoint.read_bytes()).hexdigest(),runner_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),seconds=time.monotonic()-start)
  p.with_suffix('.json').write_text(json.dumps(receipt,indent=2)+'\n');results.append(receipt);print('DONE',r['key'],round(receipt['seconds'],2),'seconds',flush=True)
if __name__=='__main__':main()
