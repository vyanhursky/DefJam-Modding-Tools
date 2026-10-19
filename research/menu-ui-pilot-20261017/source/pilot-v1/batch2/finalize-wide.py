"""Private premultiplied-alpha bridge assembly and five-aspect art previews."""
from pathlib import Path
import hashlib,importlib.util,json
import numpy as np
from PIL import Image

root=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('bridge',root.parent/'seam-v2/assemble-bridges.py')
bridge=importlib.util.module_from_spec(spec);spec.loader.exec_module(bridge)
bridge.check_solver()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def premul(a):
    a=a.astype(float)
    return np.dstack([a[:,:,:3]*a[:,:,3:4]/255,a[:,:,3]])
def straight(a):
    alpha=a[:,:,3].clip(0,255)
    rgb=np.minimum(np.maximum(a[:,:,:3],0),alpha[:,:,None])
    rgb=np.divide(rgb*255,alpha[:,:,None],out=np.zeros_like(rgb),where=alpha[:,:,None]>.0001)
    return np.rint(np.dstack([rgb,alpha])).clip(0,255).astype(np.uint8)
def match(proposal,fixed):
    a,res=bridge.boundary_match(proposal[:,:,:3],fixed[:,:,:3])
    al,resa=bridge.boundary_match(np.repeat(proposal[:,:,3:4],3,axis=2),np.repeat(fixed[:,:,3:4],3,axis=2))
    return np.dstack([a,al[:,:,0]]),max(res,resa)

records=[];masters={}
for label in ['title-middle','title-tower','mode-environment']:
    old=np.array(Image.open(root/(label+'-assembled-proposal.png')).convert('RGBA'))
    master=old.copy();allowed=np.zeros(old.shape[:2],dtype=bool)
    h=old.shape[0]
    domains=[('left',1600,384,0,930 if label=='title-middle' else 1338 if label=='title-tower' else 1440),
             ('right',3520 if label.startswith('title') else 4086,384,0,930 if label=='title-middle' else 1338 if label=='title-tower' else 1440)]
    if label=='title-tower':domains[1]=('right',3520,512,512,1338)
    if label=='mode-environment':domains[0]=('left',1600,720,0,1440)
    for side,edge,width,y0,y1 in domains:
        x0,x1=(edge-width,edge) if side=='left' else (edge,edge+width)
        candidate=old[y0:y1,x0:x1].copy()
        raw_name=None;norm=None
        if label=='title-tower' and side=='right':
            raw_name='title-tower-right-bridge-raw.png'
            raw=Image.open(root/raw_name).convert('RGBA')
            assert raw.size==(1536,1024)
            candidate=np.array(raw)[0:826,768:1280]
        if label=='mode-environment' and side=='left':
            raw_name='mode-environment-left-bridge-raw.png'
            raw=Image.open(root/raw_name).convert('RGBA')
            assert raw.width==raw.height,'Reject aspect/crop drift'
            norm=dict(raw_size=list(raw.size),target_size=[1440,1440],
                method='Uniform full-canvas resolution normalization; original boundary at50% and poster top at24% retain registration. Protected context restored exactly.')
            candidate=np.array(raw.resize((1440,1440),Image.Resampling.LANCZOS))[:,:720]
        proposal=premul(candidate)
        fixed=premul(old[y0:y1,x0:x1])
        neighboring=premul(old)
        if side=='left':fixed[:,-1]=np.clip(2*neighboring[y0:y1,edge]-neighboring[y0:y1,edge+1],0,255)
        else:fixed[:,0]=np.clip(2*neighboring[y0:y1,edge-1]-neighboring[y0:y1,edge-2],0,255)
        # At the canvas top/bottom there is no unedited row beyond the domain.
        # Reconcile corner values instead of retaining a mismatched old edge row.
        for row in ([0] if y0==0 else [])+([-1] if y1==h else []):
            t=np.linspace(0,1,width)[:,None]
            fixed[row]=proposal[row]+(fixed[row,0]-proposal[row,0])*(1-t)+(fixed[row,-1]-proposal[row,-1])*t
        result,res=match(proposal,fixed)
        master[y0:y1,x0:x1]=straight(result)
        allowed[y0:y1,x0:x1]=True
        records.append(dict(label=label,side=side,domain=[x0,y0,x1-x0,y1-y0],raw=raw_name,normalization=norm,residual=res))
    protected_end=3520 if label.startswith('title') else 4086
    assert np.array_equal(master[:,1600:protected_end],old[:,1600:protected_end])
    assert np.array_equal(master[~allowed],old[~allowed])
    if label=='title-tower':
        # A rigid roof plane needs alpha/geometry registration as well as color.
        # Trace its real final source-edge slope and continue that same plane;
        # it naturally leaves the active layer at the bottom on very wide views.
        # AI supplies surface pixels. Only new right-side pixels are remapped.
        ys=[];xs=np.arange(3440,3520)
        for x in xs:
            hits=np.flatnonzero(old[800:1338,x,3]>=128)
            ys.append(800+hits[0])
        slope=float(np.polyfit(xs,np.array(ys),1)[0])
        start=float(ys[-1])
        raw=np.array(Image.open(root/'title-tower-outpaint-raw.png').convert('RGBA').resize((5120,1707),Image.Resampling.LANCZOS))[:1536]
        for x in range(3520,5120):
            desired=start+slope*(x-3519)
            hits=np.flatnonzero(raw[700:1338,x,3]>=100)
            observed=700+hits[0] if len(hits) else 1200
            yy=np.arange(1338,dtype=float)
            sample=(yy-desired+observed).clip(0,1535)
            lo=np.floor(sample).astype(int);hi=np.minimum(lo+1,1535)
            w=(sample-lo)[:,None]
            rgb=(1-w)*raw[lo,x,:3]+w*raw[hi,x,:3]
            a=np.clip((yy-desired+1)*255,0,255)
            master[:1338,x]=np.rint(np.column_stack([rgb,a])).clip(0,255).astype(np.uint8)
        # Small value matching remains one-sided and preserves the exact source.
        x0,x1,y0,y1=3520,3904,800,1338
        p=premul(master[y0:y1,x0:x1]);fixed=p.copy()
        neighbor=premul(old)
        fixed[:,0]=np.clip(2*neighbor[y0:y1,3519]-neighbor[y0:y1,3518],0,255)
        result,res=match(p,fixed)
        master[y0:y1,x0:x1]=straight(result)
        allowed[:1338,3520:]=True
        records.append(dict(label=label,method='AI texture vertically registered to source rigid-roof alpha plane',
            domain=[3520,0,1600,1338],source_edge_top=start,source_edge_slope=slope,
            note='Full right extension contour continues source slope, exits at bottom; original center unchanged'))
        assert np.array_equal(master[:,1600:3520],old[:,1600:3520])
    path=root/(label+'-wide-draft.png');Image.fromarray(master).save(path)
    masters[label]=Image.fromarray(master)
    for side,edge in [('left',1600),('right',protected_end)]:
        x0=max(0,min(5120-768,edge-384))
        Image.fromarray(master).crop((x0,0,x0+768,h)).save(root/(label+'-'+side+'-full-height.png'))

# Full-strength lit envelope uses the SAME extended brick structure, exact lit center.
lit=masters['mode-environment'].copy()
lit.paste(Image.open(root/'mode-environment-lit-known3x.png').convert('RGBA'),(1600,0))
lit.save(root/'mode-environment-lit-wide-draft.png')
masters['mode-environment-lit']=lit
sky=Image.open(root.parent/'seam-v3/title-skyline-32x9-v3.png').convert('RGBA')
full=sky.copy()
full.alpha_composite(masters['title-middle'].crop((0,0,5120,930)),(0,306))
full.alpha_composite(masters['title-tower'].crop((0,0,5120,1338)),(0,48))
full.save(root/'title-layers-32x9-draft.png')
masters['title-layers']=full
for label,im in list(masters.items()):
    if label=='title-middle':
        stage=sky.copy();stage.alpha_composite(im.crop((0,0,5120,930)),(0,306))
    elif label=='title-tower':
        stage=sky.copy();stage.alpha_composite(im.crop((0,0,5120,1338)),(0,48))
    else:stage=im
    for ratio,width in [('4x3',1920),('16x10',2304),('16x9',2560),('21x9',3360),('32x9',5120)]:
        x=(5120-width)//2
        frame=stage.crop((x,0,x+width,1440))
        p=root/(label+'-'+ratio+'-preview.png');frame.convert('RGB').save(p)
    center=np.array(stage.crop((1600,0,3520,1440)))
    for ratio,width in [('4x3',1920),('16x10',2304),('16x9',2560),('21x9',3360),('32x9',5120)]:
        cropped=Image.open(root/(label+'-'+ratio+'-preview.png')).convert('RGB')
        assert np.array_equal(np.array(cropped.crop(((width-1920)//2,0,(width+1920)//2,1440))),center[:,:,:3])

(root/'wide-receipt.json').write_text(json.dumps(dict(schema=1,processor_sha256=sha(Path(__file__)),
    boundary_processor_sha256=sha(root.parent/'seam-v2/assemble-bridges.py'),records=records,
    protected_context='exact',outside_domains='exact',aspect_centers='5/5 for each of5view groups',
    approved_skyline_sha256=sha(root.parent/'seam-v3/title-skyline-wide-master-v3.png'),
    status='New layers and composites UNAPPROVED; alpha outside original is a generated proposal; mode is a nominal idle layout/envelope, not a game capture'),indent=2))
print('5view groups x5aspects; source contexts exact; skyline unchanged')
