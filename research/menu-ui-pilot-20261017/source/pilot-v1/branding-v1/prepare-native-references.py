from pathlib import Path
import csv,json,shutil,hashlib
from PIL import Image,ImageOps,ImageDraw
import numpy as np
out=Path('logs/ui-restoration-20261017/pilot-v1/branding-v1')
corpus=Path('/Users/vlad/Library/Application Support/DefJamPR19-20/data/hd-work/setup-lanczos/b9aa783f1d66d41be59fb97ba25fb86e1e9f73d8ee041263b0ff5df85ceb26f0')
assets=json.loads((corpus/'corpus.json').read_text())['assets']
records=[]
for label,menu,names in [('title-logo','prestart',['19']),('support','mainMenuLogosIcons',['11','14','17','20','23','26']),('door','mainMenu',['21','22','23','25','26','27','29','30','31','33','34','36','37','39','40','42','43','44','46','47','48']),('start','prestart',['27','28','30','31','34','35','37'])]:
 for name in names:
  a=next(a for a in assets if any('::' in z['source'] and z['source'].split('::')[-2].lower().endswith('/'+menu.lower()+'.big') and z['name'].strip()==name for z in a['aliases']))
  f=corpus/a['original'];assert hashlib.sha256(f.read_bytes()).hexdigest()==a['original_hash']
  stem=label if label=='title-logo' else f'{label}-{name}'
  shutil.copy2(f,out/f'{stem}-source.png');shutil.copy2(corpus/a['upscaled'],out/f'{stem}-faithful.png')
  arr=np.array(Image.open(f).convert('RGBA'));vis=arr[:,:,3]>128
  records.append({'label':stem,'name':name,'menu':menu,'source_id':a['id'],'source_size':[a['width'],a['height']],'source_sha256':a['original_hash'],'faithful_sha256':a['upscaled_hash'],'alpha_range':[int(arr[:,:,3].min()),int(arr[:,:,3].max())],'visible_rgb_range':[[int(arr[:,:,i][vis].min()),int(arr[:,:,i][vis].max())] if vis.any() else [] for i in range(3)]})
  if label=='title-logo':
   im=Image.open(corpus/a['upscaled']).convert('RGBA');bg=Image.new('RGBA',im.size,(40,40,40,255));bg.alpha_composite(im);bg.convert('RGB').save(out/'title-logo-faithful-dark.png')
for label in ['support','door','start']:
 rs=[r for r in records if r['label'].startswith(label+'-')];w=900;h=((len(rs)+5)//6)*190;bg=Image.new('RGB',(w,h),(45,45,45));d=ImageDraw.Draw(bg)
 for i,r in enumerate(rs):
  im=Image.open(out/(r['label']+'-source.png')).convert('RGBA');back=Image.new('RGBA',im.size,(50,50,50,255));back.alpha_composite(im);thumb=ImageOps.contain(back,(140,150));x=i%6*150;y=i//6*190;bg.paste(thumb.convert('RGB'),(x+(150-thumb.width)//2,y+25));d.text((x+4,y+4),r['label'],fill='white')
 bg.save(out/f'{label}-contact.png')
(out/'references.json').write_text(json.dumps(records,indent=2)+'\n')
print(json.dumps(records[:7],indent=2));print('35 source/faithful references copied, identity verified')
