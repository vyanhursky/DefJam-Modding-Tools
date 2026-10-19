from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib
p=Path(__file__).resolve().parent;root=p.parent;sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();d=json.loads((p/'before-hashes.json').read_text())
for name,h in d.items():assert sha(root/name)==h,name
pins=json.loads((root/'jukebox-approval-20261018.json').read_text())['files']
for r in pins:assert sha(root/r['path'])==r['sha256']
a=np.array(Image.open(p/'options-wide-v3.png').convert('RGB'));old=np.array(Image.open(root/'menus-seams-v2/options-wide-v2.png').convert('RGB'));assert np.array_equal(a[:,:3520],old[:,:3520]);contact=Image.new('RGB',(1600,5*280),(18,20,18));draw=ImageDraw.Draw(contact)
for i,(r,w) in enumerate([('4x3',1920),('16x10',2304),('16x9',2560),('21x9',3360),('32x9',5120)]):
 im=Image.open(p/('options-'+r+'-v3.png')).convert('RGB');x=(5120-w)//2;z=np.array(im);assert np.array_equal(z,a[:,x:x+w]);assert np.array_equal(z[:,(w-1920)//2:(w+1920)//2],old[:,1600:3520]);im.thumbnail((1580,245));contact.paste(im,((1600-im.width)//2,i*280+25));draw.text((10,i*280+5),r,fill='white')
contact.save(p/'five-aspects.png');result=dict(previous_png_hashes_exact=len(d),jukebox_approved_files_exact=len(pins),options_accepted_left_and_original_center_exact=True,aspect_crops_and_centers_exact=5,only_changed_master=[3520,0,1600,1440],calls=2,pilot_total=56,options_art_approved=False,game_run=False,workshop_writes=False);(p/'verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
