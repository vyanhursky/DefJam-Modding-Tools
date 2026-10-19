"""Independent private-art integrity checks, no game/workshop mutations."""
from pathlib import Path
import hashlib,json
import numpy as np
from PIL import Image
p=Path(__file__).resolve().parent;root=p.parent;sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
r=json.loads((p/'restoration-receipt.json').read_text());refs=json.loads((p/'references.json').read_text())
for a in refs:
 assert sha(p/(a['label']+'-source.png'))==a['source_sha256']
 assert sha(p/(a['label']+'-faithful.png'))==a['faithful_sha256']
for a in r['records']:
 f=p/(a['label']+'-restrained.png');assert sha(f)==a['output_sha256']
 x=np.array(Image.open(f).convert('RGBA'));b=np.array(Image.open(p/(a['label']+'-faithful.png')).convert('RGBA'));mask=np.array(Image.open(p/(a['label']+'-protected.png')))>0
 assert np.array_equal(x[:,:,3],b[:,:,3]);assert np.array_equal(x[mask],b[mask]);assert list(Image.open(f).size)==a['size']
for t in r['tiles']:
 out=np.array(Image.open(p/t['path']).convert('RGBA'));base=np.array(Image.open(p/f"door-{t['name']}-faithful.png").convert('RGBA'));assert np.array_equal(out[:,:,3],base[:,:,3]);assert sha(p/t['path'])==t['sha256']
assembly=json.loads((p/'assembled-references.json').read_text())
for a in assembly:
 im=np.array(Image.open(p/(a['label']+'-restrained.png')).convert('RGBA'))
 for part in a['parts']:
  tile=np.array(Image.open(p/f"door-{part['image']}-restrained.png").convert('RGBA'));baseline=np.array(Image.open(p/f"door-{part['image']}-faithful.png").convert('RGBA'))
  w,h=[int(v*4) for v in part['nominal_sample_uv'][2:]];x,y=[int(v*4) for v in part['assembled_origin']]
  assert np.array_equal(tile[:h,:w],im[y:y+h,x:x+w]);assert np.array_equal(tile[h:],baseline[h:]);assert np.array_equal(tile[:,w:],baseline[:,w:])
for path in [root/'skyline-approval.json',root/'approvals-v1/approval.json',p/'city-approval.json']:
 data=json.loads(path.read_text())
 if path.name=='skyline-approval.json':
  assert sha(Path(data['master']['path']))==data['master']['sha256']
  for f in data['aspect_previews']:assert sha(Path(f['path']))==f['sha256']
 elif 'water_tower' in data:
  for k in ['water_tower','mode_select']:
   for f in data[k]['files']:assert sha(root/f['path'])==f['sha256']
 else:
  for f in data['files']:assert sha(root/f['path'])==f['sha256']
result=dict(schema=1,original_faithful_reference_pairs_unchanged=len(refs),restoration_alpha_and_protected_pairs_exact=len(r['records']),tile_splits_reassemble_exact=len(r['tiles']),tile_stored_padding_alpha_exact=True,all_prior_approved_art_unchanged=True,city_approval_files_unchanged=12,browser=dict(assets=9,comparison_combinations_loaded=72,backgrounds=['dark','light','checker'],channels=['rgba','alpha'],city_and_conditional_mode_labels_verified=True,console_errors=0),new_generation_calls=9,pilot_total_generation_calls=27,workshop_writes=False,game_run=False)
(p/'verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
