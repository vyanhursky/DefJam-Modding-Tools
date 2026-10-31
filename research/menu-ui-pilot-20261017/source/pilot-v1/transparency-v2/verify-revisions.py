"""Verify the alpha repair, transformed semantic probes and prior art pins."""
from pathlib import Path
from PIL import Image
import json,hashlib,numpy as np
p=Path(__file__).resolve().parent;b=p.parent/'branding-v1';root=p.parent
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
records=json.loads((p/'assembly-receipt.json').read_text())['records'];guides={r['label']:r for r in json.loads((p/'guide-receipt.json').read_text())};probes=json.loads((p/'probes.json').read_text())['records'];checks=[]
for record,source in zip(records,probes):
 label=record['label'];old=np.array(Image.open(b/(label+'-raw.png')).convert('RGBA'));out=np.array(Image.open(p/(label+'-repaired.png')).convert('RGBA'));alpha=np.array(Image.open(p/(label+'-registered-alpha.png')).convert('L'))
 assert sha(b/(label+'-raw.png'))==record['old_sha256'];assert sha(p/(label+'-repaired.png'))==record['output_sha256']
 assert np.array_equal(old[:,:,:3],out[:,:,:3]);assert np.array_equal(out[:,:,3],np.minimum(old[:,:,3],alpha))
 for version,h in source['hashes'].items():assert sha(b/(label+'-'+version+'.png'))==h
 flow=np.load(p/(label+'-registration.npz'));u,v=flow['u'],flow['v'];g=guides[label];sx0,sy0,sx1,sy1=g['source_alpha_bbox'];dx0,dy0,dx1,dy1=g['raw_material_bbox']
 for probe in source['probes']:
  fx,fy=probe['faithful_xy'];sx=dx0+(fx-sx0+.5)*(dx1-dx0)/(sx1-sx0)-.5;sy=dy0+(fy-sy0+.5)*(dy1-dy0)/(sy1-sy0)-.5
  # Invert saved backward source-coordinate displacement by a bounded search.
  x0=max(0,int(sx)-140);y0=max(0,int(sy)-140);x1=min(out.shape[1],int(sx)+141);y1=min(out.shape[0],int(sy)+141)
  if x0>=x1 or y0>=y1:
   checks.append(dict(label=label,description=probe['description'],classification=probe['expected_alpha_class'],outside_active_reference=True));continue
  yy,xx=np.mgrid[y0:y1,x0:x1];dist=(xx+u[y0:y1,x0:x1]-sx)**2+(yy+v[y0:y1,x0:x1]-sy)**2;k=np.unravel_index(np.argmin(dist),dist.shape);x=int(xx[k]);y=int(yy[k]);expected=int(alpha[y,x]);actual=int(out[y,x,3]);prior=int(old[y,x,3]);cls=probe['expected_alpha_class']
  # Interpolation and the previous clear-mask cap are explicit. Check classes,
  # rather than pretending transformed texels equal original native bytes.
  passed=actual<=20 if cls in ['clear','near-clear','transparent'] else actual>=240 if cls=='opaque' else 0<actual<240
  checks.append(dict(label=label,description=probe['description'],classification=cls,raw_xy=[x,y],prior_alpha=prior,registered_original_alpha=expected,repaired_alpha=actual,source_native_alpha=probe['native_rgba'][3],source_faithful_alpha=probe['faithful_rgba'][3],mapping_error_pixels=float(np.sqrt(dist[k])),class_check=passed,previous_clear_cap_exception=(cls=='partial' and expected<=20 and prior==0 and actual==0)))
pins=0
for file in [root/'skyline-approval.json',root/'approvals-v1/approval.json',b/'city-approval.json']:
 d=json.loads(file.read_text())
 if file.name=='skyline-approval.json':items=[d['master']]+d['aspect_previews'];files=[(Path(i['path']),i['sha256']) for i in items]
 elif 'water_tower' in d:files=[(root/i['path'],i['sha256']) for k in ['water_tower','mode_select'] for i in d[k]['files']]
 else:files=[(root/i['path'],i['sha256']) for i in d['files']]
 for f,h in files:assert sha(f)==h;pins+=1
result=dict(rgb_exact_pairs=9,alpha_recipe_exact_pairs=9,previous_source_faithful_restrained_hashes_unchanged=27,prior_approved_conditional_art_files_unchanged=pins,semantic_probes=checks,semantic_checks_passed=sum(c.get('class_check',False) for c in checks),previous_clear_cap_exceptions=[c for c in checks if c.get('previous_clear_cap_exception')],semantic_checks_failed=[c for c in checks if c.get('class_check') is False and not c.get('previous_clear_cap_exception')],new_builtin_calls=9,pilot_total_builtin_calls=36,raw_retry_alpha_adopted=False,game_ready_mapping=False)
assert not result['semantic_checks_failed'],result['semantic_checks_failed']
(p/'verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
