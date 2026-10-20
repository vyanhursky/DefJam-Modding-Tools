"""Complete full gym shapes60/64 after full-part audit; retain partial survey history."""
from pathlib import Path
import json,csv,hashlib,shutil
p=Path('logs/ui-restoration-20261017/pilot-v1/controls-v1-20261020');sources=json.loads((p/'sources.json').read_text());groups=json.loads((p/'groups.json').read_text());rows=list(csv.DictReader(Path('logs/ui-restoration-20261017/all-menu-texture-aliases.csv').open()));corpus=Path('/Users/vlad/Library/Application Support/DefJamPR19-20/data/hd-work/setup-lanczos/b9aa783f1d66d41be59fb97ba25fb86e1e9f73d8ee041263b0ff5df85ceb26f0');sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();history=p/'partial-survey-history';history.mkdir(exist_ok=False)
for name in ['groups.json','assembly-receipt.json','verification.json','review-items.json']+[f'{k}-{s}.png' for k in ['gym-display','gym-rail'] for s in ['source','faithful','draft','source-alpha','draft-alpha']]:shutil.copy2(p/name,history/name)
by={}
for n in ['58','56','62']:
 x=next(x for x in rows if 'story/gym.big' in x['source'] and x['name'].strip()==n);x['source_file']=x['id']+'-source.png';shutil.copy2(corpus/x['original'],p/x['source_file']);x['source_sha256']=sha(p/x['source_file']);sources.append(x);by[n]=x
for key in ['gym-display','gym-rail']:
 g=next(g for g in groups if g['key']==key)
 if key=='gym-display':g['size']=[318,342];g['parts']+=[dict(source_id=by['58']['id'],crop=[0,0,62,256],offset=[256,0]),dict(source_id=by['56']['id'],crop=[0,0,62,86],offset=[256,256])];g['placement']='Complete Shape60four-part display:318x342integertexelmosaic, nativebounds-11,1..307,343. Native fractional UVs remain separate; no invented stretch.'
 else:g['size']=[317,87];g['parts'].append(dict(source_id=by['62']['id'],crop=[0,0,61,87],offset=[256,0]));g['placement']='Complete Shape64two-part rail:317x87integertexelmosaic, nativebounds-1,0..316,87. Separate UI layer; fractional UVs retained.'
(p/'sources.json').write_text(json.dumps(sources,indent=2)+'\n');(p/'groups.json').write_text(json.dumps(groups,indent=2)+'\n');f=p/'assemble.py';s=f.read_text().replace('19 native4x tiles','22 native4x tiles').replace('source_tiles=19','source_tiles=22').replace('19tiles15studies','22tiles15studies');f.write_text(s)
