"""Private restrained derivatives; exact alpha, graphics, padding and seams.

Raw built-in generations provide only bounded fine L* detail. Source a*/b*
and broad lighting remain fixed. Lit-wall detail is shared from the dark trial.
No workshop import or approval is performed here.
"""
from pathlib import Path
import hashlib,json
import numpy as np
from PIL import Image,ImageDraw
from defjam_tools.color_trial import rgb_to_lab,lab_to_rgb,box_blur

root=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
configs={
'title-middle':dict(active=(640,310),seams=[('x',512)],boxes=[]),
'title-tower':dict(active=(640,446),seams=[('x',512)],boxes=[]),
'mode-shutter':dict(active=(230,354),seams=[('y',256)],boxes=[]),
'mode-surround':dict(active=(576,480),seams=[('x',512),('x',449)],boxes=[(110,0,75,75),(20,80,250,370),(280,118,165,235)]),
'mode-wall-lit':dict(active=(320,480),seams=[('x',256)],boxes=[(0,108,272,300)])}
records=[]
for label,cfg in configs.items():
    base_path=root/(label+'-faithful.png')
    base=Image.open(base_path).convert('RGBA')
    rgba=np.array(base)
    rgb=rgba[:,:,:3]
    lab=rgb_to_lab(rgb)
    if label=='mode-wall-lit':
        parent=root.parent/'mode-wall-dark-palette-constrained-trial.png'
        faithful=root.parent/'mode-wall-dark-faithful.png'
        detail=rgb_to_lab(np.array(Image.open(parent).convert('RGB')))[:,:,0]-rgb_to_lab(np.array(Image.open(faithful).convert('RGB')))[:,:,0]
        raw_size=None
        raw_hash=sha(parent)
        kind='Shared dark-wall fine detail; original lit palette/illumination retained'
    else:
        raw_path=root/(label+'-raw.png')
        raw=Image.open(raw_path).convert('RGB')
        raw_size=list(raw.size)
        draft=rgb_to_lab(np.array(raw.resize(base.size,Image.Resampling.LANCZOS)))[:,:,0]
        light=lab[:,:,0]
        detail=.25*((draft-box_blur(draft,8))-(light-box_blur(light,8)))
        raw_hash=sha(raw_path)
        kind='AI fine detail only; explicit full-canvas normalization'
    detail=np.clip(detail,-1.,1.)
    h,w=rgba.shape[:2]
    held=np.zeros((h,w),dtype=bool)
    held[:16]=True;held[:,:16]=True;held[:,-16:]=True
    aw,ah=cfg['active']
    held[ah*4:]=True;held[:,aw*4:]=True
    for axis,pos in cfg['seams']:
        if axis=='x':held[:,(pos-4)*4:(pos+4)*4]=True
        else:held[(pos-4)*4:(pos+4)*4]=True
    for x,y,bw,bh in cfg['boxes']:
        held[y*4:(y+bh)*4,x*4:(x+bw)*4]=True
    # Preserve source alpha, partial coverage and a surrounding silhouette band.
    held|=(box_blur((rgba[:,:,3]==255).astype(float),4)<.999999)|(rgb.max(axis=2)<=16)
    allowed=box_blur((~held).astype(float),4)*(~held)
    newlab=lab.copy()
    newlab[:,:,0]+=detail*allowed
    assert np.array_equal(newlab[:,:,1:],lab[:,:,1:])
    new,clipped=lab_to_rgb(newlab)
    new[held|clipped]=rgb[held|clipped]
    out=np.dstack([new,rgba[:,:,3]])
    assert np.array_equal(out[:,:,3],rgba[:,:,3]) and np.array_equal(out[held],rgba[held])
    p=root/(label+'-restrained.png')
    Image.fromarray(out).save(p)
    Image.fromarray(held.astype(np.uint8)*255).save(root/(label+'-protected.png'))
    delta=rgb_to_lab(new)-lab
    visible=(rgba[:,:,3]>0)&(rgb.max(axis=2)>16)
    records.append(dict(label=label,kind=kind,raw_dimensions=raw_size,raw_sha256=raw_hash,
        baseline_sha256=sha(base_path),output_sha256=sha(p),size=list(base.size),
        alpha='exact',protected='exact',median_Lab=np.median(delta[visible],axis=0).tolist(),
        mean_Lab=np.mean(delta[visible],axis=0).tolist(),max_detail_L=1.,strength=.25,
        active_source_bounds=list(cfg['active']),protected_boxes=cfg['boxes'],seams=cfg['seams']))
    print(label,'alpha/protected exact',flush=True)
(root/'restoration-receipt.json').write_text(json.dumps(dict(schema=1,
    processor_sha256=sha(Path(__file__)),records=records,status='Unapproved restoration trials; no import/install'),indent=2))

# Real opaque source padding is retained above; layer previews clip active UVs.
for label,height in [('title-middle',310),('title-tower',446)]:
    img=Image.open(root/(label+'-restrained.png')).convert('RGBA').resize((1920,1536),Image.Resampling.LANCZOS)
    target=Image.new('RGBA',(5120,1536),(0,0,0,0))
    target.paste(img,(1600,0))
    target.save(root/(label+'-wide-target.png'))
    guide=target.copy()
    draw=ImageDraw.Draw(guide)
    draw.rectangle((1600,0,3519,1535),outline='#58dfff',width=7)
    draw.line((0,height*3,5119,height*3),fill='#ff65c0',width=6)
    guide.save(root/(label+'-wide-guide.png'))
    # Premultiplied visual target against checker, for reliable alpha inspection.
    check=Image.new('RGB',target.size,'#202020')
    check.paste(target,mask=target.getchannel('A'))
    check.save(root/(label+'-wide-target-visible.png'))
