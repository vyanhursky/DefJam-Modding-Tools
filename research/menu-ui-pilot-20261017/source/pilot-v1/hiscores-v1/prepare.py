"""Native High Scores 640x512 mosaic and alpha-safe source references."""
from pathlib import Path
from PIL import Image
import json,hashlib,shutil
p=Path(__file__).resolve().parent;r=p.parent;sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();(p/'before-hashes.json').write_text(json.dumps({str(f.relative_to(r)):sha(f) for f in r.rglob('*.png') if p not in f.parents},indent=2)+'\n');shutil.copy2(r/'review.html',p/'review-before.html');m=json.loads((r.parent/'next-scope/hiscores-background-metadata.json').read_text())[0];parts=m['shapes'][0]['parts'];a=Image.new('RGBA',(640,512));refs=[]
for x in sorted(parts,key=lambda x:x['part']):
 f=Path(x['original']);im=Image.open(f).convert('RGBA');shutil.copy2(f,p/f'part-{x["part"]}-source.png');a.paste(im,(x['part']*512,0));refs.append(dict(part=x['part'],id=x['source_id'],original=str(f),sha256=sha(f),size=list(im.size)))
a.save(p/'hiscores-source.png');a.resize((2560,2048),Image.Resampling.LANCZOS).save(p/'hiscores-faithful.png');a.crop((0,0,640,480)).resize((1920,1440),Image.Resampling.BILINEAR).save(p/'hiscores-original-layout.png');(p/'references.json').write_text(json.dumps(dict(resource='screens/hiScores/hiScores.big',active=[640,480],stored=[640,512],parts=refs,alpha='opaque',root_placement=[0,0],shape=3,padding='last32storedrows',tile_seam=512),indent=2)+'\n');print('NativeHighScores640x480,opaque source,2tiles;oldartfingerprinted')
