from pathlib import Path
from PIL import Image,ImageDraw
import csv,json
r=Path('logs/ui-restoration-20261017/pilot-v1');p=r/'story-shop-v1-20261020';p.mkdir(exist_ok=True);corpus=Path('/Users/vlad/Library/Application Support/DefJamPR19-20/data/hd-work/setup-lanczos/b9aa783f1d66d41be59fb97ba25fb86e1e9f73d8ee041263b0ff5df85ceb26f0');rows=list(csv.DictReader((r.parent/'all-menu-texture-aliases.csv').open()));cat=json.loads(Path('config/menu-ui-approved-artwork.json').read_text());seen={x['source_id'] for x in cat['reviewed_sources']}|{x['id'] for x in json.loads((r/'controls-v1-20261020/sources.json').read_text())}|{x['id'] for x in json.loads((r/'menu-details-v1-20261020/references.json').read_text())['sources']};items=[]
for x in rows:
 if x['id'] in seen:continue
 if any(n+'.big' in x['source'] for n in ['/conSetup','/saveWarn','/memWarn','/barber','/clothing','/jeweller','/wardrobe','/cribOptions','/credits','/screenPosition','/chooseStyle']) and int(x['width'])>=128 and int(x['height'])>=128:items.append(x);seen.add(x['id'])
(p/'survey.json').write_text(json.dumps(items,indent=2)+'\n')
for page in range((len(items)+39)//40):
 canvas=Image.new('RGB',(1200,210*((len(items[page*40:page*40+40])+4)//5)),'#333');d=ImageDraw.Draw(canvas)
 for j,x in enumerate(items[page*40:page*40+40]):
  im=Image.open(corpus/x['original']).convert('RGBA');im.thumbnail((230,165));x0=j%5*240;y=j//5*210;canvas.paste(im,(x0,y),im);d.text((x0,y+165),f'{j+page*40}: {x["source"].split("::")[-1]} #{x["name"].strip()}\n{x["width"]}x{x["height"]}',fill='white')
 canvas.save(p/f'survey-{page}.png')
print(len(items))
