from pathlib import Path
import csv,json
from PIL import Image,ImageDraw,ImageFont
r=Path('logs/ui-restoration-20261017/pilot-v1');out=r/'controls-v1-20261020';out.mkdir(exist_ok=True);corpus=Path('/Users/vlad/Library/Application Support/DefJamPR19-20/data/hd-work/setup-lanczos/b9aa783f1d66d41be59fb97ba25fb86e1e9f73d8ee041263b0ff5df85ceb26f0');rows=list(csv.DictReader((r.parent/'all-menu-texture-aliases.csv').open()));approved={x['source_id'] for x in json.loads(Path('config/menu-ui-approved-artwork.json').read_text())['reviewed_sources']};pending={x['id'] for x in json.loads((r/'menu-details-v1-20261020/references.json').read_text())['sources']};seen=approved|pending;items=[]
for x in rows:
 if x['id'] in seen:continue
 if ('mainMenuButtons.xsh' in x['source'] and int(x['width'])>=128) or ('::popups.xsh' in x['source'] and int(x['width'])>=128) or ('story/gym.big' in x['source'] and int(x['width'])>=128 and int(x['height'])>=128):items.append(x);seen.add(x['id'])
(out/'survey.json').write_text(json.dumps(items,indent=2)+'\n');canvas=Image.new('RGB',(1000,230*((len(items)+3)//4)), '#303030');d=ImageDraw.Draw(canvas)
for i,x in enumerate(items):
 im=Image.open(corpus/x['original']).convert('RGBA');im.thumbnail((230,180));x0=(i%4)*250;y=(i//4)*230;canvas.paste(im,(x0,y),im);d.text((x0,y+180),f'{i}: {x["source"].split("::")[-1]} #{x["name"].strip()}\n{x["width"]}x{x["height"]} {x["id"][:10]}',fill='white')
canvas.save(out/'survey.png');print(len(items))
