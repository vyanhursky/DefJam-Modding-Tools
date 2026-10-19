"""Private Battle native reference assembly; never mutates corpus or approved art."""
from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib,shutil
p=Path(__file__).resolve().parent;r=p.parent;repo=r.parents[2];sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
meta=json.loads((repo/'logs/ui-restoration-20261017/next-scope/battle-background-geometry.json').read_text());rows=[]
(p/'before-hashes.json').write_text(json.dumps({str(f.relative_to(r)):sha(f) for f in r.rglob('*.png') if p not in f.parents},indent=2)+'\n');shutil.copy2(r/'review.html',p/'review-before.html')
for m in meta['movies']:
 label=m['movie'];canvas=Image.new('RGBA',(640,512));tiles=[]
 for i,a in enumerate(sorted(m['background_parts'],key=lambda a:a['part'])):
  f=Path(a['original']);im=Image.open(f).convert('RGBA');assert list(im.size)==a['size'];name=f'{label}-{a["image"]}';shutil.copy2(f,p/(name+'-source.png'));im.resize((im.width*4,im.height*4),Image.Resampling.LANCZOS).save(p/(name+'-faithful.png'));canvas.paste(im,(i*512,0));tiles.append(dict(name=name,id=a['source_id'],original=str(f),sha256=sha(f),size=list(im.size)))
 canvas.save(p/(label+'-source.png'));canvas.resize((2560,2048),Image.Resampling.LANCZOS).save(p/(label+'-faithful.png'));canvas.crop((0,0,640,480)).resize((1920,1440),Image.Resampling.BILINEAR).save(p/(label+'-original-layout.png'));rows.append(dict(label=label,tiles=tiles,active=[640,480],stored=[640,512],join=512))
(p/'references.json').write_text(json.dumps(rows,indent=2)+'\n')
thumb=Image.new('RGB',(1280,1024),'#111');d=ImageDraw.Draw(thumb)
for i,row in enumerate(rows):
 im=Image.open(p/(row['label']+'-source.png')).convert('RGB');thumb.paste(im,(i%2*640,i//2*512));d.text((i%2*640+8,i//2*512+488),row['label'],fill='white')
thumb.save(p/'native-contact.png');print('4 mosaics /8source refs saved; previous artwork fingerprinted')
