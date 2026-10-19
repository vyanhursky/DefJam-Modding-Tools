"""Private source-mapped menu-emblem references; no workshop or runtime writes."""
from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image,ImageOps,ImageDraw
p=Path(__file__).resolve().parent
r=json.loads((p/'emblem-geometry.json').read_text());refs={x['source_id']:x for x in json.loads((p/'references.json').read_text())}
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
records=[]
for s in r['shapes']:
 label='emblem-'+s['name'];im=Image.new('RGBA',tuple(s['source_preserving_canvas']),(0,0,0,0));hd=Image.new('RGBA',tuple(v*4 for v in s['source_preserving_canvas']),(0,0,0,0))
 for part in s['parts']:
  ref=refs[part['source_id']];assert ref['label']=='door-'+str(part['image'])
  orig=p/(ref['label']+'-source.png');faith=p/(ref['label']+'-faithful.png')
  assert sha(orig)==ref['source_sha256'] and sha(faith)==ref['faithful_sha256']
  actual=np.array(part['quantized_uv_pixels']);nominal=part['nominal_sample_uv'];assert abs(actual[:,0].min()-nominal[0])<.03 and abs(actual[:,1].min()-nominal[1])<.03
  assert abs(actual[:,0].max()-nominal[2])<.03 and abs(actual[:,1].max()-nominal[3])<.03
  x,y=map(int,part['assembled_origin']);assert [x,y]==part['assembled_origin']
  im.paste(Image.open(orig).convert('RGBA').crop(tuple(nominal)),(x,y))
  hd.paste(Image.open(faith).convert('RGBA').crop(tuple(v*4 for v in nominal)),(x*4,y*4))
 im.save(p/(label+'-source.png'));hd.save(p/(label+'-faithful.png'))
 bg=Image.new('RGBA',hd.size,(40,40,40,255));bg.alpha_composite(hd);bg.convert('RGB').save(p/(label+'-faithful-dark.png'))
 records.append({'label':label,'name':s['name'],'source_size':im.size,'size':hd.size,'active':s['active_size'],'parts':s['parts'],'source_sha256':sha(p/(label+'-source.png')),'faithful_sha256':sha(p/(label+'-faithful.png'))})
bg=Image.new('RGB',(1200,640),(35,35,35));d=ImageDraw.Draw(bg)
for i,row in enumerate(records):
 im=Image.open(p/(row['label']+'-faithful-dark.png'));im=ImageOps.contain(im,(280,280));x=i%4*300;y=i//4*320;bg.paste(im,(x+(300-im.width)//2,y+32));d.text((x+10,y+8),row['name'],fill='white')
bg.save(p/'assembled-emblems-contact.png')
(p/'assembled-references.json').write_text(json.dumps(records,indent=2)+'\n')
print('8 assemblies verified against native IDs/hashes and packed UV bounds;21source fragments retained')
