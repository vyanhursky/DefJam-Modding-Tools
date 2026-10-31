"""Reinsert exact final source pixels before seam QA; never approve raw output."""
from pathlib import Path
from PIL import Image
root=Path(__file__).resolve().parent
for label in ['title-middle','title-tower','mode-environment']:
    raw=Image.open(root/(label+'-outpaint-raw.png')).convert('RGBA')
    out=raw.resize((5120,1707),Image.Resampling.LANCZOS)
    if label.startswith('title'):
        center=Image.open(root/(label+'-restrained.png')).convert('RGBA').resize((1920,1536),Image.Resampling.LANCZOS)
        out.paste(center,(1600,0))
        out=out.crop((0,0,5120,1536))
    else:
        center=Image.open(root/'mode-environment-dark-known3x.png').convert('RGBA')
        out.paste(center,(1600,0))
        out=out.crop((0,0,5120,1440))
    out.save(root/(label+'-assembled-proposal.png'))
    if label.startswith('title'):
        h=310 if label=='title-middle' else 446
        active=out.crop((0,0,5120,h*3))
        bg=Image.new('RGB',active.size,'#303030');bg.paste(active,mask=active.getchannel('A'))
        bg.save(root/(label+'-proposal-visible.png'))
    for side,edge in [('left',1600),('right',3520 if label.startswith('title') else 4086)]:
        x0=max(0,min(5120-1536,edge-768))
        out.crop((x0,0,x0+1536,1024)).save(root/(label+'-'+side+'-join-target.png'))
