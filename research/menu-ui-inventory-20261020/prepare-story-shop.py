"""Prepare larger30study batch from37mapped paper tiles and20Faithful UI sources."""
from pathlib import Path
from PIL import Image,ImageDraw
import csv,json,hashlib,shutil
r=Path('logs/ui-restoration-20261017/pilot-v1');p=r/'story-shop-v1-20261020';corpus=Path('/Users/vlad/Library/Application Support/DefJamPR19-20/data/hd-work/setup-lanczos/b9aa783f1d66d41be59fb97ba25fb86e1e9f73d8ee041263b0ff5df85ceb26f0');rows=list(csv.DictReader((r.parent/'all-menu-texture-aliases.csv').open()));metadata=json.loads(Path('logs/ui-restoration-20261020/story-shop-paper-shapes.json').read_text());sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();groups=[];sources={};approved={x['source_id'] for x in json.loads(Path('config/menu-ui-approved-artwork.json').read_text())['reviewed_sources']};pending={x['id'] for x in json.loads((r/'menu-details-v1-20261020/references.json').read_text())['sources']}
labels={'barber':'Barber · blue-header paper','clothing':'Clothing · red-header paper','jeweller':'Jeweller · purple-header paper','wardrobe':'Wardrobe · olive-header paper','chooseStyle':'Fighting style · folded paper','saveWarn':'Save warning · paper and hazard icon','memWarn':'Memory warning · paper and hazard icon','conSetup':'Controller setup · instructions paper','tattoo':'Tattoo shop · green-header paper','trophies':'Trophies · olive-header paper'}
def source(sid):
 if sid in sources:return sources[sid]
 x=next(x.copy() for x in rows if x['id']==sid);assert sid not in approved|pending,(sid,x);x['source_file']=sid+'-source.png';shutil.copy2(corpus/x['original'],p/x['source_file']);x['source_sha256']=sha(p/x['source_file']);sources[sid]=x;return x
for group in metadata['groups']:
 key=group['label'].split('/')[-1];shape=group['matched_shapes'][0];parts=shape['parts'];origin=[min(v[j] for a in parts for v in a['geometry_vertices']) for j in [0,1]];outparts=[]
 for a in parts:
  source(a['source_id']);uv=a['uv_vertices'];geom=a['geometry_vertices'];crop=[round(min(v[j] for v in uv)) for j in [0,1]]+[round(max(v[j] for v in uv)) for j in [0,1]];offset=[round(min(v[j] for v in geom)-origin[j]) for j in [0,1]];outparts.append(dict(source_id=a['source_id'],crop=crop,offset=offset));assert all(abs((max(v[j] for v in geom)-min(v[j] for v in geom))-(crop[j+2]-crop[j]))<.15 for j in [0,1])
 size=[max(a['offset'][j]+a['crop'][j+2]-a['crop'][j] for a in outparts) for j in [0,1]];groups.append(dict(key=key,label=labels[key],size=size,kind='paper',parts=outparts,placement=f'Complete textured parts of Shape{shape["shape"]}; integer texel reconstruction. Fractional UVs, live text and runtime transforms remain separate.'))
faithful=[('credits','1','Credits · EA Games mark'),('credits','12','Credits · Def Jam mark'),('credits','15','Credits · AKI mark'),('saveWarn','89','Memory card · diagram'),('saveWarn','93','Memory card · Nintendo diagram'),('conSetup','92','Controller diagram · GameCube'),('conSetup','102','Controller diagram · Xbox'),('conSetup','5','Controller diagram · PlayStation'),('barber','57','Barber · small paper swatch'),('clothing','106','Clothing · small paper swatch'),('wardrobe','76','Wardrobe · small paper swatch'),('barber','15','Barber · blue strip A'),('barber','60','Barber · blue strip B'),('clothing','112','Clothing · red strip A'),('clothing','64','Clothing · red strip B'),('jeweller','123','Jeweller · purple strip A'),('jeweller','73','Jeweller · purple strip B'),('wardrobe','50','Wardrobe · olive strip A'),('wardrobe','79','Wardrobe · olive strip B'),('charDec','108','Character details · soft light mask')]
for movie,name,label in faithful:
 row=next(x for x in rows if x['source'].endswith('::'+movie+'.xsh') and x['name'].strip()==name);x=source(row['id']);w,h=int(x['width']),int(x['height']);groups.append(dict(key=movie+'-'+name,label=label,size=[w,h],kind='faithful',parts=[dict(source_id=x['id'],crop=[0,0,w,h],offset=[0,0])],placement='Faithful HD full storage canvas; source padding/lettering/softness retained. Used crop and runtime placement are not claimed.'))
(p/'sources.json').write_text(json.dumps(list(sources.values()),indent=2)+'\n');(p/'groups.json').write_text(json.dumps(groups,indent=2)+'\n');(p/'before-hashes.json').write_text(json.dumps({str(f.relative_to(r)):sha(f) for f in r.rglob('*.png') if p not in f.parents},indent=2)+'\n')
for g in groups:
 if g['kind']!='paper':continue
 im=Image.new('RGBA',g['size'])
 for q in g['parts']:im.paste(Image.open(p/(q['source_id']+'-source.png')).convert('RGBA').crop(q['crop']),q['offset'])
 im=im.resize(tuple(v*3 for v in g['size']),Image.Resampling.LANCZOS);im.save(p/(g['key']+'-edit-input.png'))
board=Image.new('RGB',(1500,600),'#444');d=ImageDraw.Draw(board)
for i,g in enumerate(groups[:10]):
 im=Image.open(p/(g['key']+'-edit-input.png'));im.thumbnail((280,260));x=i%5*300;y=i//5*300;board.paste(im,(x+(300-im.width)//2,y+20),im);d.text((x,y+280),g['label'],fill='white')
board.save(p/'paper-input-overview.png');print(len(groups),'studies',len(sources),'sources')
