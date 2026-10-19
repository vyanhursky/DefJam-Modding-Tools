from pathlib import Path
import json
from PIL import Image,ImageDraw

root=Path(__file__).resolve().parent
previous=root.parent/'seam-v2/title-skyline-wide-master-refined.png'
image=Image.open(previous).convert('RGB')
crop=image.crop((2752,256,4288,1280))
crop.save(root/'right-join-target.png')
guide=crop.copy()
d=ImageDraw.Draw(guide)
d.rectangle((768,124,1280,704),outline='#ff60c8',width=3)
d.line((768,0,768,1023),fill='#59eaff',width=2)
guide.save(root/'right-join-guide.png')
image.crop((3136,350,3904,1024)).save(root/'right-before-close.png')
(root/'geometry.json').write_text(json.dumps(dict(parent=str(previous),
    master_crop=[2752,256,1536,1024],seam_local_x=768,
    permitted_rect_local=[768,124,512,580],
    previous_domain_master=[3520,380,384,324],
    note='Prior repair stopped at master y704, excluding lower sky and horizon haze.'),indent=2))
