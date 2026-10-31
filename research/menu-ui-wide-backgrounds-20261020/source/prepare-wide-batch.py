from pathlib import Path
from PIL import Image,ImageDraw
import json,csv,hashlib
root=Path('logs/ui-restoration-20261017/pilot-v1');out=root/'wide-backgrounds-v1-20261020';out.mkdir(exist_ok=True)
corpus=Path('/Users/vlad/Library/Application Support/DefJamPR19-20/data/hd-work/setup-lanczos/b9aa783f1d66d41be59fb97ba25fb86e1e9f73d8ee041263b0ff5df85ceb26f0')
rows={x['id']:x for x in csv.DictReader(Path('logs/ui-restoration-20261017/all-menu-texture-aliases.csv').open())}
groups=[]
labels={'choosGF2':'Story · girlfriend selection · brick shield wall','choosGF4':'Story · girlfriend selection · alternate wall','choosPart':'Story · partner selection · paper wall','charDec':'Story · character details · desktop','cribOptions':'Crib Options · paper wall'}
for r in json.loads(Path('logs/ui-restoration-20261020/menu-widescreen-background-gaps-metadata.json').read_text())['resources']:
 key=r['label'].split('/')[-1];parts=[]
 if key not in labels:continue
 for shape in r['matched_shapes']:
  for p in shape['parts']:
   sid=p['source']['source_id'];uv=p['uv_bounds'];xy=p['geometry_bounds_xy'];parts.append({'id':sid,'crop':[round(v) for v in uv],'xy':[round(v) for v in xy[:2]],'uv_exact':uv,'geometry_exact':xy})
 groups.append(dict(key=key,label=labels[key],parts=parts,sides=['left'] if key=='cribOptions' else ['left','right']))
pre=json.loads(Path('logs/ui-restoration-20261020/prefight-loading-uv-metadata.json').read_text())['resources']
for movie,shape,label in [('matchLoa',2,'Pre-fight · match loading plate'),('tips',3,'Pre-fight · tips wall')]:
 r=next(x for x in pre if x['resource'].endswith('/'+movie+'.big'));parts=[]
 for p in r['parts']:
  if p['shape']!=shape:continue
  uv=p['uv_pixels'];xy=p['decoded_xy'];box=[min(v[j] for v in uv) for j in (0,1)]+[max(v[j] for v in uv) for j in (0,1)];geom=[min(v[j] for v in xy) for j in (0,1)]+[max(v[j] for v in xy) for j in (0,1)];parts.append(dict(id=p['source_id'],crop=[round(v) for v in box],xy=[round(v) for v in geom[:2]],uv_exact=box,geometry_exact=geom))
 groups.append(dict(key=movie,label=label,parts=parts,sides=['left','right']))
for g in groups:
 for mode in ['original','faithful']:
  im=Image.new('RGBA',(640,480))
  for p in g['parts']:
   src=Image.open(corpus/rows[p['id']][mode]).convert('RGBA');scale=4 if mode=='faithful' else 1;crop=[v*scale for v in p['crop']];tile=src.crop(crop)
   if mode=='faithful':tile=tile.resize((crop[2]//4-crop[0]//4,crop[3]//4-crop[1]//4),Image.Resampling.LANCZOS)
   im.paste(tile,p['xy'])
  im.save(out/f'{g["key"]}-{mode}.png')
 for side in g['sides']:
  core=Image.open(out/f'{g["key"]}-faithful.png');target=Image.new('RGB',(790,480),(128,128,128));target.paste(core.crop((0,0,256,480) if side=='left' else (384,0,640,480)),(534,0) if side=='left' else (0,0));target.save(out/f'{g["key"]}-{side}-target.png')
(out/'groups.json').write_text(json.dumps(groups,indent=2)+'\n')
board=Image.new('RGB',(1400,900),'#333');d=ImageDraw.Draw(board)
for i,g in enumerate(groups):
 im=Image.open(out/f'{g["key"]}-faithful.png');im.thumbnail((320,240));x=i%4*350;y=i//4*450;board.paste(im,(x,y+25),im);d.text((x,y),g['label'],fill='white')
board.save(out/'source-overview.png');print(out.resolve());print([(g['key'],len(g['parts'])) for g in groups])
