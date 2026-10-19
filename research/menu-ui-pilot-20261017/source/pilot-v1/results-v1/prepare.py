"""Assemble six paper layouts from actual APT/material tile offsets; originals immutable."""
from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib,shutil
p=Path(__file__).resolve().parent;r=p.parent;sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();(p/'before-hashes.json').write_text(json.dumps({str(f.relative_to(r)):sha(f) for f in r.rglob('*.png') if p not in f.parents},indent=2)+'\n');shutil.copy2(r/'review.html',p/'review-before.html');meta=json.loads((r.parent/'next-scope/result-panels-metadata.json').read_text());rows=[]
placements={'rematch':(184,233),'matchSm1':(194,66),'matchSm2':(50,60),'matchSm3':(43,65),'matchSm4':(44,66),'rewardun':(110.5,68)};wanted={'rematch':[1],'matchSm1':[11,10,9,8],'matchSm2':[18,17,16,19],'matchSm3':[21,19,18,20],'matchSm4':[15,14,13,16],'rewardun':[1]}
for m in meta:
 label=m['movie'];shape=m['shapes'][0];box=shape['bbox'];aw,ah=round(box[2]-box[0]),round(box[3]-box[1]);parts=[]
 for part in shape['parts']:
  if part['image'] not in wanted[label]:continue
  f=Path(part['original']);im=Image.open(f).convert('RGBA');name=label+'-'+str(part['image']);shutil.copy2(f,p/(name+'-source.png'));mat=part['material_matrix'];off=[round(-mat[12]-box[0]),round(-mat[13]-box[1])];uv=part['quantized_uv'];used=[round(min(q[0] for q in uv)),round(min(q[1] for q in uv)),round(max(q[0] for q in uv)),round(max(q[1] for q in uv))];parts.append(dict(name=name,image=part['image'],id=part['source_id'],original=str(f),original_sha256=sha(f),size=list(im.size),offset=off,used_uv=used))
 sw=max(a['offset'][0]+a['size'][0] for a in parts);sh=max(a['offset'][1]+a['size'][1] for a in parts);canvas=Image.new('RGBA',(sw,sh))
 for a in parts:canvas.paste(Image.open(p/(a['name']+'-source.png')).convert('RGBA'),a['offset'])
 canvas.save(p/(label+'-stored-source.png'));active=canvas.crop((0,0,aw,ah));active.save(p/(label+'-source.png'));active.resize((aw*4,ah*4),Image.Resampling.LANCZOS).save(p/(label+'-faithful.png'));active.getchannel('A').resize((aw*4,ah*4),Image.Resampling.LANCZOS).save(p/(label+'-faithful-alpha.png'));rows.append(dict(label=label,shape=shape['shape'],active=[aw,ah],stored=[sw,sh],stage_placement=placements[label],parts=parts,source_mosaic_sha256=sha(p/(label+'-source.png'))))
(p/'references.json').write_text(json.dumps(dict(stage=[640,480],panels=rows,policy='Panel art remains at native authored placement through all aspect ratios. Live text/icons/backdrop not flattened. Fractional rewardun x110.5 retained in metadata;3xpreviewrounding explicit.'),indent=2)+'\n');out=Image.new('RGB',(1440,1000),'#444');d=ImageDraw.Draw(out)
for i,a in enumerate(rows):
 im=Image.open(p/(a['label']+'-source.png')).convert('RGBA');im.thumbnail((460,450));bg=Image.new('RGBA',im.size,'#777');bg.alpha_composite(im);x=i%3*480;y=i//3*500;out.paste(bg.convert('RGB'),(x,y+24));d.text((x+5,y+4),a['label']+' '+str(a['active']),fill='white')
out.save(p/'native-contact.jpg');print('6panel layouts /',sum(len(a['parts']) for a in rows),'source tiles;active/stored/UV/root positions retained')
