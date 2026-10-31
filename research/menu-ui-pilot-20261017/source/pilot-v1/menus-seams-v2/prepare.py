from pathlib import Path
from PIL import Image,ImageDraw
import hashlib,json,shutil
p=Path(__file__).resolve().parent;old=p.parent/'menus-v1';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
shutil.copy2(p.parent/'review.html',p/'review-before.html')
files={str(f.relative_to(p.parent)):sha(f) for d in ['menus-v1','batch2','transparency-v2'] for f in (p.parent/d).glob('*.png')};(p/'before-hashes.json').write_text(json.dumps(files,indent=2)+'\n')
rows=[]
for label,side,crop,join in [('options','right',(2800,0,5120,1440),720),('jukebox','left',(0,0,2320,1440),1600),('jukebox','right',(2800,0,5120,1440),720)]:
 name=f'{label}-{side}';im=Image.open(old/(label+'-wide-refined.png')).convert('RGB');target=im.crop(crop);target.save(p/(name+'-target.png'));guide=target.copy();d=ImageDraw.Draw(guide);rect=(0,0,join-1,1439) if side=='left' else (join,0,2319,1439);d.rectangle(rect,outline='#ff40d0',width=6);d.line((join,0,join,1439),fill='#40ffff',width=5);guide.save(p/(name+'-guide.png'));rows.append(dict(label=name,menu=label,side=side,crop=list(crop),size=[2320,1440],join=join,allowed=[0,0,join,1440] if side=='left' else [join,0,2320-join,1440],original_context='right720' if side=='left' else 'left720'))
ref=Image.open(p.parent/'batch2/mode-environment-lit-32x9-preview.png').convert('RGB');ref.crop((2600,0,4900,1440)).save(p/'mode-lit-door-reference.png')
(p/'layout.json').write_text(json.dumps(rows,indent=2)+'\n')
