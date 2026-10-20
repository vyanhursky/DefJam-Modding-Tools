"""Visual census of bounded popup/profile/autosave originals, excluding all reviewed/pending art."""
from pathlib import Path
from PIL import Image,ImageDraw
import json,csv,hashlib,shutil
r=Path('logs/ui-restoration-20261017/pilot-v1');p=r/'popup-profile-v1-20261020';p.mkdir(exist_ok=False);sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();cat=json.loads(Path('config/menu-ui-approved-artwork.json').read_text());exclude={x['source_id'] for x in cat['reviewed_sources']}|{s for x in json.loads((r/'menu-details-v1-20261020/review-items.json').read_text()) for s in x['source_ids']};rows=list(csv.DictReader((r.parent/'all-menu-texture-aliases.csv').open()));root=Path('/Users/vlad/Library/Application Support/DefJamPR19-20/data/hd-work/setup-lanczos/b9aa783f1d66d41be59fb97ba25fb86e1e9f73d8ee041263b0ff5df85ceb26f0');wanted={'screens/feloader.big','screens/beloader.big','screens/intMain/message.big','screens/options/userID.big','screens/memoryCard/autosaveMessage.big'};seen=set();items=[]
for a in rows:
 if a['source'].split('::')[1] not in wanted or a['id'] in exclude|seen or int(a['width'])<128 or int(a['height'])<128:continue
 seen.add(a['id']);key='asset-'+a['id'][:12];a=dict(a,key=key,source_file=key+'-source.png',source_sha256=sha(root/a['original']));items.append(a);shutil.copy2(root/a['original'],p/a['source_file'])
(p/'survey-sources.json').write_text(json.dumps(items,indent=2)+'\n');(p/'before-hashes.json').write_text(json.dumps({str(f.relative_to(r)):sha(f) for f in r.rglob('*.png') if p not in f.parents},indent=2)+'\n');shutil.copy2(r/'review.html',p/'review-before.html')
for page in range((len(items)+11)//12):
 board=Image.new('RGB',(1440,4*340),(60,60,60));draw=ImageDraw.Draw(board)
 for i,a in enumerate(items[page*12:page*12+12]):
  im=Image.open(p/a['source_file']).convert('RGBA');im.thumbnail((460,280));x=(i%3)*480;y=(i//3)*340;board.paste(im,(x+(480-im.width)//2,y+35),im);draw.text((x+5,y+4),a['source'].split('::')[1]+' #'+a['name'].strip(),fill='white');draw.text((x+5,y+315),a['width']+'x'+a['height']+' '+a['id'][:12],fill='white')
 board.save(p/f'survey-{page+1}.png')
print(len(items),'bounded sources,',(len(items)+11)//12,'sheets')
