from pathlib import Path
from PIL import Image
import json,shutil,hashlib
r=Path('logs/ui-restoration-20261017/pilot-v1');p=r/'controls-v1-20261020';survey=json.loads((p/'survey.json').read_text());sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();corpus=Path('/Users/vlad/Library/Application Support/DefJamPR19-20/data/hd-work/setup-lanczos/b9aa783f1d66d41be59fb97ba25fb86e1e9f73d8ee041263b0ff5df85ceb26f0');selected=[i for i in range(27) if i in [0,3,4,6,7,8,9,10] or i>=16];sources=[survey[i] for i in selected]
for x in sources:shutil.copy2(corpus/x['original'],p/(x['id']+'-source.png'));x['source_file']=x['id']+'-source.png';x['source_sha256']=sha(p/x['source_file'])
byname={x['name'].strip():x for x in sources if 'gym.xsh' in x['source']};groups=[]
def part(x,crop,offset):return dict(source_id=x['id'],crop=crop,offset=offset)
groups.append(dict(key='gym-paper',label='Gym · four-tile folded paper',size=[337,454],kind='paper',parts=[part(byname['49'],[0,0,256,256],[0,0]),part(byname['48'],[0,0,81,256],[256,0]),part(byname['47'],[0,0,256,198],[0,256]),part(byname['46'],[0,0,81,198],[256,256])],placement='Shape50bounds7,25..344,479. Integertexelmosaic; fractional nativeUVs retained separately. Live text not baked.'))
groups.append(dict(key='gym-display',label='Gym · pale display and lower rail',size=[256,342],kind='faithful',parts=[part(byname['59'],[0,0,256,256],[0,0]),part(byname['57'],[0,0,256,86],[0,256])],placement='Shape60bounds-11,1..307,343: texturewidth256 maps318geometry; texel preview only. Softness and existing rail preserved.'))
groups.append(dict(key='gym-rail',label='Gym · separate metal rail',size=[256,87],kind='faithful',parts=[part(byname['63'],[0,0,256,87],[0,0])],placement='Shape64bounds-1,0..316,87; nearly fullsourcewidth. Separate layer, not joined to paper.'))
labels={'texP':'Shared popup · crumpled paper','texN':'Shared popup · dark strip N','texT':'Shared popup · dark strip T','texF':'Shared popup · dark strip F','11':'Menu button · Story','15':'Menu button · Online','19':'Menu button · Options','23':'Menu button · Jukebox','27':'Menu button · Extras','31':'Menu button · High Scores','37':'Menu button · Create Player','42':'Menu button · Battle'}
for x in sources:
 if 'gym.xsh' in x['source']:continue
 n=x['name'].strip();w,h=int(x['width']),int(x['height']);groups.append(dict(key='popup-'+n if n.startswith('tex') else 'button-'+n,label=labels[n],size=[w,h],kind='paper' if n=='texP' else 'faithful',parts=[part(x,[0,0,w,h],[0,0])],placement='Full storage canvas; UV/use unverified. Preserve padding/alpha/printed paths; no inferred placement.'))
(p/'sources.json').write_text(json.dumps(sources,indent=2)+'\n');(p/'groups.json').write_text(json.dumps(groups,indent=2)+'\n');(p/'before-hashes.json').write_text(json.dumps({str(f.relative_to(r)):sha(f) for f in r.rglob('*.png') if p not in f.parents},indent=2)+'\n')
for g in groups:
 if g['kind']!='paper':continue
 im=Image.new('RGBA',g['size'])
 for q in g['parts']:im.paste(Image.open(p/(q['source_id']+'-source.png')).convert('RGBA').crop(q['crop']),q['offset'])
 im=im.resize(tuple(v*3 for v in g['size']),Image.Resampling.LANCZOS);im.save(p/(g['key']+'-edit-input.png'))
print(len(groups),len(sources))
