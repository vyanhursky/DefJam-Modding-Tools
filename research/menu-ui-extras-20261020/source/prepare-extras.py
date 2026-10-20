from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib,shutil
r=Path('logs/ui-restoration-20261017/pilot-v1');p=r/'extras-v1-20261020';p.mkdir(exist_ok=True);meta=json.loads(Path('logs/ui-restoration-20261020/extras-metadata.json').read_text())[0];sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();(p/'before-hashes.json').write_text(json.dumps({str(f.relative_to(r)):sha(f) for f in r.rglob('*.png') if p not in f.parents},indent=2)+'\n');shutil.copy2(r/'review.html',p/'review-before.html');labels={36:'list-paper',38:'note-37',43:'note-42',49:'note-48',53:'note-52',59:'ribbon-58'};records=[]
for s in meta['shapes']:
 label=labels[s['shape']];box=s['bbox'];aw,ah=round(box[2]-box[0]),round(box[3]-box[1]);parts=[]
 for a in sorted(s['parts'],key=lambda a:a['part']):
  f=Path(a['original']);im=Image.open(f).convert('RGBA');name=str(a['image']);shutil.copy2(f,p/('image-'+name+'-source.png'));x=round(-a['material_matrix'][12]-box[0]);y=round(-a['material_matrix'][13]-box[1]);uv=a['quantized_uv'];used=[round(min(v[0] for v in uv)),round(min(v[1] for v in uv)),round(max(v[0] for v in uv)),round(max(v[1] for v in uv))];parts.append(dict(image=a['image'],source_id=a['source_id'],source_sha256=sha(f),size=list(im.size),offset=[x,y],used_uv=used,material_matrix=a['material_matrix']))
 sw=max(a['offset'][0]+a['size'][0] for a in parts);sh=max(a['offset'][1]+a['size'][1] for a in parts);canvas=Image.new('RGBA',(sw,sh))
 for a in parts:canvas.paste(Image.open(p/f'image-{a["image"]}-source.png').convert('RGBA'),tuple(a['offset']))
 canvas.save(p/(label+'-stored-source.png'));active=canvas.crop((0,0,aw,ah));active.save(p/(label+'-source.png'));active.resize((aw*4,ah*4),Image.Resampling.LANCZOS).save(p/(label+'-faithful.png'));records.append(dict(label=label,shape=s['shape'],bbox=box,active=[aw,ah],stored=[sw,sh],parts=parts))
(p/'references.json').write_text(json.dumps(dict(movie='extras/extras',panels=records,metadata='logs/ui-restoration-20261020/extras-metadata.json',policy='Original paper panels and ribbon,not scenery;native authored positions/transforms remainlive.'),indent=2)+'\n');out=Image.new('RGB',(1440,900),'#333');d=ImageDraw.Draw(out)
for i,a in enumerate(records):
 im=Image.open(p/(a['label']+'-source.png'));im.thumbnail((450,390));bg=Image.new('RGBA',im.size,'#888');bg.alpha_composite(im);x=i%3*480;y=i//3*450;out.paste(bg.convert('RGB'),(x,y+25));d.text((x+3,y+3),a['label']+' '+str(a['active']),fill='white')
out.save(p/'source-contact.jpg');print('6Extraslayouts/9sourceIDs;',p)
