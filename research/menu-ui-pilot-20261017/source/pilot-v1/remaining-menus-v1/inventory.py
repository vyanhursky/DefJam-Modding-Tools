"""Private visual shortlist from remaining registered menu families; source IDs only."""
from pathlib import Path
from PIL import Image,ImageDraw
import csv,json
p=Path(__file__).resolve().parent;r=p.parent;corpus=Path('/Users/vlad/Library/Application Support/DefJamPR19-20/data/hd-work/setup-lanczos/b9aa783f1d66d41be59fb97ba25fb86e1e9f73d8ee041263b0ff5df85ceb26f0');rows=list(csv.DictReader((r.parent/'all-menu-texture-aliases.csv').open()));wanted=['extras/extras','hiScores/hiScores','battle/rematch','battle/matchSm1','battle/matchSm2','battle/matchSm3','battle/matchSm4','battle/rewards1','battle/rewardun','story/crib','story/gym','story/msgCentr','options/credits'];selected=[]
for label in wanted:
 candidates=[x for x in rows if '::screens/'+label+'.big::' in x['source'] and int(x['width'])>=256 and int(x['height'])>=128]
 for x in candidates:
  if int(x['width'])>=512 or label in ['extras/extras','hiScores/hiScores','battle/rematch']:selected.append(dict(label=label,**x))
(p/'candidates.json').write_text(json.dumps(selected,indent=2)+'\n')
for page in range((len(selected)+11)//12):
 items=selected[page*12:page*12+12];out=Image.new('RGB',(1440,4*300),'#222');d=ImageDraw.Draw(out)
 for i,x in enumerate(items):
  im=Image.open(corpus/x['original']).convert('RGBA');im.thumbnail((460,260));bg=Image.new('RGBA',im.size,'#666');bg.alpha_composite(im);xx=i%3*480;yy=i//3*300;out.paste(bg.convert('RGB'),(xx,yy+22));d.text((xx+3,yy+2),x['label']+' '+x['name'].strip()+' '+x['width']+'x'+x['height'],fill='white')
 out.save(p/f'candidates-{page+1}.jpg')
print(len(selected),'textures;', (len(selected)+11)//12,'contact sheets')
for x in selected:print(x['label'],x['name'].strip(),x['width'],x['height'],x['id'][:12])
