from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib
p=Path(__file__).resolve().parent;root=p.parent;sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();before=json.loads((p/'before-hashes.json').read_text())
for f,h in before.items():assert sha(root/f)==h,f
for menu in ['options','jukebox']:
 a=np.array(Image.open(p/(menu+'-wide-v2.png')).convert('RGB'));old=np.array(Image.open(root/'menus-v1'/(menu+'-wide-refined.png')).convert('RGB'));assert np.array_equal(a[:,1600:3520],old[:,1600:3520])
 if menu=='options':assert np.array_equal(a[:,:3520],old[:,:3520])
 for ratio,w in [('4x3',1920),('16x10',2304),('16x9',2560),('21x9',3360),('32x9',5120)]:
  im=np.array(Image.open(p/(menu+'-'+ratio+'-v2.png')).convert('RGB'));x=(5120-w)//2;assert im.shape==(1440,w,3);assert np.array_equal(im,a[:,x:x+w]);assert np.array_equal(im[:,(w-1920)//2:(w+1920)//2],old[:,1600:3520])
# Visual audit sheet: every supported aspect, at common height and exact crop.
contact=Image.new('RGB',(1800,5*290),(18,20,18));d=ImageDraw.Draw(contact)
for i,(r,w) in enumerate([('4x3',1920),('16x10',2304),('16x9',2560),('21x9',3360),('32x9',5120)]):
 for j,menu in enumerate(['options','jukebox']):
  im=Image.open(p/(menu+'-'+r+'-v2.png'));im.thumbnail((890,250));contact.paste(im,(j*900+(890-im.width)//2,i*290+25));d.text((j*900+10,i*290+5),menu+' '+r,fill='white')
contact.save(p/'all-aspects-contact.png')
result=dict(prior_png_hashes_unchanged=len(before),original_centers_exact=2,options_full_left_and_original_center_exact=True,aspect_crops_and_original_centers_exact=10,restoration_tiles_and_alpha_unchanged=True,mode_reference_art_unchanged=True,new_calls=5,pilot_total=54,new_art_approved=False,workshop_writes=False,game_run=False,scope='Three beyond4:3 side regions only')
(p/'verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
