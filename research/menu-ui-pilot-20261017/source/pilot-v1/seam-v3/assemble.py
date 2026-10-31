"""Extend right-side AI bridge through the lower sky; retain accepted left."""
from pathlib import Path
import hashlib
import importlib.util
import json
import numpy as np
from PIL import Image,ImageDraw

root=Path(__file__).resolve().parent
oldroot=root.parent/'seam-v2'
spec=importlib.util.spec_from_file_location('prior_assembly',oldroot/'assemble-bridges.py')
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
module.check_solver()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
previous=oldroot/'title-skyline-wide-master-refined.png'
raw_path=root/'right-full-height-raw.png'
raw_image=Image.open(raw_path).convert('RGB')
assert raw_image.size==(1536,1024),'Reject changed registration/dimensions'
old=np.array(Image.open(previous).convert('RGB'))
master=old.copy()
x0,x1,y0,y1=3520,4032,380,960
raw=np.asarray(raw_image,dtype=float)
proposal=raw[y0-256:y1-256,768:1280].copy()
fixed=old[y0:y1,x0:x1].astype(float)
fixed[1:-1,0]=np.clip(2*old[y0+1:y1-1,x0-1].astype(float)-old[y0+1:y1-1,x0-2],0,255)
matched,residual=module.boundary_match(proposal,fixed)
master[y0:y1,x0:x1]=np.rint(matched).clip(0,255).astype(np.uint8)
mask=np.zeros(old.shape[:2],dtype=bool)
mask[y0:y1,x0:x1]=True
assert np.array_equal(master[:,:3520],old[:,:3520]),'Original center AND accepted left must remain exact'
assert np.array_equal(master[~mask],old[~mask])
out=root/'title-skyline-wide-master-v3.png'
Image.fromarray(master).save(out)
Image.fromarray(mask.astype(np.uint8)*255).save(root/'edit-domain.png')
for side,edge in [('left',1600),('right',3520)]:
    rect=(edge-384,350,edge+384,1024)
    Image.fromarray(old).crop(rect).save(root/(side+'-previous-close.png'))
    Image.fromarray(master).crop(rect).save(root/(side+'-current-close.png'))
stage=Image.new('RGB',(5120,1440))
stage.paste(Image.fromarray(master).crop((0,402,5120,1350)),(0,0))
baseline=np.array(Image.open(root.parent/'title-skyline-4x3-layer-preview.png').convert('RGB'))
outputs={}
for ratio,width in [('4x3',1920),('16x10',2304),('16x9',2560),('21x9',3360),('32x9',5120)]:
    frame=stage.crop(((5120-width)//2,0,(5120+width)//2,1440))
    assert np.array_equal(np.array(frame.crop(((width-1920)//2,0,(width+1920)//2,1440))),baseline)
    p=root/('title-skyline-'+ratio+'-v3.png')
    frame.save(p)
    outputs[ratio]=dict(path=p.name,sha256=sha(p))
sheet=Image.new('RGB',(1560,716),'#111310')
d=ImageDraw.Draw(sheet)
d.text((12,10),'RIGHT JOIN: PREVIOUS REPAIR (v2)',fill='#e7e9df')
d.text((792,10),'RIGHT JOIN: FULL-HEIGHT REPAIR (v3)',fill='#e7e9df')
sheet.paste(Image.open(root/'right-previous-close.png'),(8,34))
sheet.paste(Image.open(root/'right-current-close.png'),(788,34))
sheet.save(root/'right-join-before-after.png')
metrics=[]
for a,b in [(420,620),(704,850),(850,960)]:
    before=abs(old[a:b,3519].astype(float)-old[a:b,3520].astype(float)).mean()
    after=abs(master[a:b,3519].astype(float)-master[a:b,3520].astype(float)).mean()
    metrics.append(dict(master_y=[a,b],previous_mean_edge_rgb=float(before),current_mean_edge_rgb=float(after)))
inputs=[root/'right-join-target.png',root/'right-join-guide.png',previous]
receipt=dict(schema=1,tool='built-in image_gen.imagegen',date='2026-10-17',
    prompt=(root/'right-full-height-prompt.txt').read_text(),
    input_paths=[str(p) for p in inputs],input_hashes=[sha(p) for p in inputs],
    raw_output=str(raw_path),raw_sha256=sha(raw_path),raw_dimensions=list(raw_image.size),
    processor_sha256=sha(Path(__file__)),boundary_processor_sha256=sha(oldroot/'assemble-bridges.py'),
    allowed_domain=[x0,y0,x1-x0,y1-y0],harmonic_residual=residual,
    current_master_sha256=sha(out),accepted_left='byte-identical to v2',
    original_center='byte-identical',outside_domain='byte-identical',
    aspect_centers='5/5 pass',metrics=metrics,outputs=outputs,
    caution='Edge values partly enforced; inspect full-height structural flow separately.',
    status='Private right-only refinement; no workshop import/approval/install')
(root/'receipt.json').write_text(json.dumps(receipt,indent=2))
print(json.dumps({'invariants':'left, center, outside domain exact; 5/5 crops pass','metrics':metrics},indent=2))
