"""Private native references, active mosaics and exact owner-art approval pins."""
from pathlib import Path
from PIL import Image
import json,hashlib,shutil
p=Path(__file__).resolve().parent;root=p.parent;sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
corpusroot=Path('/Users/vlad/Library/Application Support/DefJamPR19-20/data/hd-work/setup-lanczos/b9aa783f1d66d41be59fb97ba25fb86e1e9f73d8ee041263b0ff5df85ceb26f0');corpus=json.loads((corpusroot/'corpus.json').read_text());refs=[];images={}
for resource,names in [('screens/options/options.big',[71,70,4,8,7]),('screens/jukebox/beatbox.big',[20,19,88,87])]:
 base=Path(resource).stem
 for name in names:
  matches=[a for a in corpus['assets'] if any(al['source']==f'screens/screens.viv::{resource}::{base}.xsh' and int(al['name'].strip())==name for al in a['aliases'])];assert len(matches)==1
  a=matches[0];f=corpusroot/a['original'];assert sha(f)==a['original_hash'];im=Image.open(f).convert('RGBA');label=f'{base}-{name}';out=p/(label+'-source.png');shutil.copy2(f,out);im.resize((im.width*4,im.height*4),Image.Resampling.LANCZOS).save(p/(label+'-faithful.png'));images[label]=im
  refs.append(dict(label=label,resource=resource,name=name,id=a['id'],source_sha256=sha(out),faithful_sha256=sha(p/(label+'-faithful.png')),size=list(im.size),alpha_range=im.getchannel('A').getextrema()))
def join(label,left,right,width,height):
 im=Image.new('RGBA',(width,height));im.paste(images[left],(0,0));im.paste(images[right],(512,0));im.save(p/(label+'-source.png'));im.resize((width*4,height*4),Image.Resampling.LANCZOS).save(p/(label+'-faithful.png'));return im
join('options-panel','options-71','options-70',576,512)
images['options-4'].save(p/'options-wall-source.png');images['options-4'].resize((1024,2048),Image.Resampling.LANCZOS).save(p/'options-wall-faithful.png')
join('options-alternate','options-8','options-7',576,512)
join('jukebox-background','beatbox-20','beatbox-19',640,512)
print([(r['label'],r['size']) for r in refs])
# Bottom strip is a separate live element, retained as a source-only reference.
join('jukebox-bottom','beatbox-88','beatbox-87',640,images['beatbox-88'].height)
(p/'references.json').write_text(json.dumps(refs,indent=2)+'\n')
approval=root/'branding-approval-20261018.json'
assert not approval.exists(),'Never overwrite approval pins'
rows=json.loads((root/'transparency-v2/assembly-receipt.json').read_text())['records'];files=[]
for r in rows:
 f=root/'transparency-v2'/(r['label']+'-repaired.png');assert sha(f)==r['output_sha256'];files.append(dict(label=r['label'],path=str(f.relative_to(root)),sha256=sha(f),size=r['size']))
approval.write_text(json.dumps(dict(schema=1,date='2026-10-18',decision='D137',status='owner-approved artwork',owner_words='The Nine textures look great - I approve all of them. Let\'s proceed to the next set of menu backgrounds',scope='Exactly the nine transparency-v2 repaired title/emblem PNGs; no raw retry, source-safe alternate or runtime acceptance implied.',files=files),indent=2)+'\n')
shutil.copy2(root/'review.html',p/'review-before-menus.html');print('9 approval pins; 9 native texture references; 3 restoration targets + alternate/bottom references')
