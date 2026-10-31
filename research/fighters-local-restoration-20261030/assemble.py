"""Private immutable local-neural comparison stages. No live imports/approvals."""
from pathlib import Path
import json,hashlib,shutil
import numpy as np
from PIL import Image,ImageDraw
from defjam_tools import local_restoration,damage_detail,color_trial,fighter_scopes
W=Path('/Users/vlad/Code/defjam-data/hd-work/texture-workshop');R=W/'experiments/fighters-local-restoration-20261030';P=json.loads((R/'plan.json').read_text());sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();read=lambda p:json.loads(Path(p).read_text());rows=[];mains={}
def comp(out,imgs,labels,filename):
 sheet=Image.new('RGB',(512*len(imgs),536),'#171717');d=ImageDraw.Draw(sheet)
 for i,(im,label) in enumerate(zip(imgs,labels)):d.text((i*512+8,5),label,fill='white');sheet.paste(im.convert('RGB').resize((512,512),Image.Resampling.LANCZOS),(i*512,24))
 sheet.save(out/filename)
for p in P['textures']:
 key=p['key'];out=R/'assembled'/(key+'-v2');assert not out.exists();out.mkdir(parents=True);original=Image.open(p['original_path']).convert('RGBA');own=Image.open(p['faithful_path']).convert('RGBA');raw=Image.open(p['raw_local_path']).convert('RGB');assert sha(p['original_path'])==p['original_sha256'] and sha(p['faithful_path'])==p['faithful_sha256'];holds=[h['box'] if isinstance(h,dict) else h for h in p['source_holds']]
 if p['width']==512:
  g=read(p['geometry_path']);_,_,seams=fighter_scopes.scopes(g,512);result,report,masks=local_restoration.assemble(own,raw,512,holds,seams);mains[p['source_id']]=dict(path=str(out/'texture.png'),key=key);kind='main-state';cleanpath=None
  comp(out,[original,own,raw,result],['Original source','Faithful HD','Local RealESRNet raw RGB','Local detail / source palette'],'comparison.png')
  for j,f in enumerate(p.get('features',[])):
   box=f['source_box'];hd=[v*4 for v in box];imgs=[original.crop(box),own.crop(hd),result.crop(hd)];comp(out,imgs,['Original feature','Faithful','Local source-palette detail'],'feature-'+str(j+1)+'.png')
 else:
  box=p['clean_head_source_box'];hd=[v*4 for v in box];clean=Image.open(p['main_original_path']).convert('RGBA').crop(box);cf=Image.open(p['main_faithful_path']).convert('RGBA').crop(hd);mid=p['main_source_id'];cleanpath=mains[mid]['path'] if mid in mains else p['main_revision_path'];restored=Image.open(cleanpath).convert('RGBA').crop(hd)
  result,report,masks=damage_detail.restore(original,clean,own,cf,restored,raw,held_source_boxes=holds);report.update(detail_origin='local RealESRNet residual, zero new ImageGen calls',method='pinned clean detail + original state RGB delta + bounded local-model luminance',clean_reference_method='new own-source local restoration' if mid in mains else 'existing prior restored main reference');kind='injury-source';masks['baseline'].save(out/'continuity-baseline.png')
  comp(out,[original,own,restored,result],['Original state','Faithful HD','Pinned restored head reference','Local source-bound injury detail'],'comparison.png');comp(out,[own,masks['baseline'],result],['Faithful state','Continuity baseline','Local final'],'injury-detail.png')
  if p.get('previous_completion')=='partial-study':
   old=next(r for r in read(W/'experiments/fighters-completion108-20261030/delivery-ledger.json') if r['source_id']==p['source_id']);comp(out,[Image.open(old['output_path']),result],['Earlier incomplete study','New local clean-reference assembly'],'previous-study-comparison.png')
 result.save(out/'texture.png',compress_level=3)
 for n,a in masks.items():
  if isinstance(a,np.ndarray):Image.fromarray(a.astype('uint8')*255).save(out/(n+'.png'))
 checks=dict(own_alpha_exact=np.array_equal(np.array(result)[...,3],np.array(own)[...,3]),own_holds_exact=all(np.array_equal(np.array(result.crop([v*4 for v in b])),np.array(own.crop([v*4 for v in b]))) for b in holds));assert all(checks.values())
 receipt=dict(schema=1,key=key,source_id=p['source_id'],method='local conventional super-resolution comparison; no ImageGen requests',original_path=p['original_path'],original_sha256=sha(p['original_path']),faithful_path=p['faithful_path'],faithful_sha256=sha(p['faithful_path']),raw_local_path=p['raw_local_path'],raw_local_sha256=sha(p['raw_local_path']),raw_local_receipt_sha256=sha(Path(p['raw_local_path']).with_suffix('.json')),plan_sha256=sha(R/'plan.json'),source_holds=holds,clean_reference_path=cleanpath,clean_reference_sha256=sha(cleanpath) if cleanpath else None,geometry_sha256=sha(p['geometry_path']) if kind=='main-state' else None,output_sha256=sha(out/'texture.png'),output_size=result.size,assembly=report,checks=checks,processor_hashes={q.name:sha(q) for q in [Path(__file__),Path(local_restoration.__file__),Path(damage_detail.__file__),Path(color_trial.__file__),Path(fighter_scopes.__file__)]},imagegen_calls=0,approved=False,selected=False,game_verified=False)
 (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');row=dict(key=key,source_id=p['source_id'],output_path=str(out/'texture.png'),output_sha256=receipt['output_sha256'],source_holds=holds,receipt_path=str(out/'receipt.json'),kind=kind,status='assembled-pending-visual-QA',comparison_path=str(out/'comparison.png'));rows.append(row);(R/'results.json').write_text(json.dumps(rows,indent=2)+'\n');print(key,receipt['output_sha256'],report.get('changed_pixels',report.get('generated_detail_pixels')),flush=True)
for m in [local_restoration,damage_detail,color_trial,fighter_scopes]:shutil.copy2(m.__file__,R/'processors'/(Path(m.__file__).stem+'-v2.py'))
shutil.copy2(__file__,R/'processors/assemble-local-fighter14-v2.py')
