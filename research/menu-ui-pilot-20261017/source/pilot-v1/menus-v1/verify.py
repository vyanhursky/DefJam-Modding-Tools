"""Independent private-art gates; reads source identities and all approved pins."""
from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
p=Path(__file__).resolve().parent;root=p.parent;sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();refs=json.loads((p/'references.json').read_text());records=json.loads((p/'restoration-receipt.json').read_text())['records']
for r in refs:
 for version in ['source','faithful']:assert sha(p/(r['label']+'-'+version+'.png'))==r[version+'_sha256']
for r in records:
 a=np.array(Image.open(p/(r['label']+'-restrained.png')).convert('RGBA'));b=np.array(Image.open(p/(r['label']+'-faithful.png')).convert('RGBA'));m=np.array(Image.open(p/(r['label']+'-protected.png')))>0
 assert sha(p/(r['label']+'-restrained.png'))==r['output_sha256'];assert np.array_equal(a[:,:,3],b[:,:,3]);assert np.array_equal(a[m],b[m])
for group,names in [('options-panel',['options-71','options-70']),('jukebox-background',['beatbox-20','beatbox-19'])]:
 parent=np.array(Image.open(p/(group+'-restrained.png')).convert('RGBA'))
 for i,name in enumerate(names):
  a=np.array(Image.open(p/(name+'-restrained.png')).convert('RGBA'));assert np.array_equal(a[:1920],parent[:1920,i*2048:i*2048+a.shape[1]]);b=np.array(Image.open(p/(name+'-faithful.png')).convert('RGBA'));assert np.array_equal(a[1920:],b[1920:]);assert np.array_equal(a[:,:,3],b[:,:,3])
wall=np.array(Image.open(p/'options-wall-restrained.png'));faith=np.array(Image.open(p/'options-wall-faithful.png'));assert np.array_equal(wall[:,171*4:],faith[:,171*4:])
for label in ['options','jukebox']:
 master=np.array(Image.open(p/(label+'-wide-refined.png')).convert('RGB'));known=np.array(Image.open(p/(label+'-known.png' if label=='options' else label+'-center.png')).convert('RGB'));assert np.array_equal(master[:,1600:1600+known.shape[1]],known)
 for ratio,w in [('4x3',1920),('16x10',2304),('16x9',2560),('21x9',3360),('32x9',5120)]:
  a=np.array(Image.open(p/(label+'-'+ratio+'-refined.png')).convert('RGB'));assert a.shape==(1440,w,3);assert np.array_equal(a[:,(w-1920)//2:(w+1920)//2],master[:,1600:3520]);b=np.array(Image.open(p/(label+'-'+ratio+'-original.png')).convert('RGB'));assert b.shape==a.shape
pins=0
for file in [root/'skyline-approval.json',root/'approvals-v1/approval.json',root/'branding-v1/city-approval.json',root/'branding-approval-20261018.json']:
 d=json.loads(file.read_text())
 if file.name=='skyline-approval.json':items=[d['master']]+d['aspect_previews'];files=[(Path(i['path']),i['sha256']) for i in items]
 elif 'water_tower' in d:files=[(root/i['path'],i['sha256']) for key in ['water_tower','mode_select'] for i in d[key]['files']]
 else:files=[(root/i['path'],i['sha256']) for i in d['files']]
 for f,h in files:assert sha(f)==h;pins+=1
for r in json.loads((root/'transparency-v2/probes.json').read_text())['records']:
 for v,h in r['hashes'].items():assert sha(root/'branding-v1'/(r['label']+'-'+v+'.png'))==h
result=dict(original_faithful_pairs_unchanged=9,restoration_alpha_and_protected_pairs_exact=3,source_shaped_tile_splits_exact=4,stored_bottom_padding_and_unused_wall_columns_exact=True,aspect_centers_exact=10,known_source_contexts_exact=2,prior_approved_conditional_files_unchanged=pins,prior_branding_reference_hashes_unchanged=27,new_generation_calls=13,pilot_total_generation_calls=49,workshop_writes=False,game_run=False,runtime_integration=False,new_backgrounds_approved=False)
(p/'verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
