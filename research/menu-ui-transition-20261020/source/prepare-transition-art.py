"""Prepare texel-space continuous t1 art study. Not a runtime geometry patch."""
from pathlib import Path
from PIL import Image
import json,hashlib,shutil
r=Path('logs/ui-restoration-20261017/pilot-v1');p=r/'transition-v1-20261020';m=json.loads(Path('logs/ui-restoration-20261020/transition-metadata.json').read_text())[0];sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();parts={a['image']:a for a in m['shapes'][0]['parts']};core=Image.new('RGBA',(641,2533));refs=[]
(p/'before-hashes.json').write_text(json.dumps({str(f.relative_to(r)):sha(f) for f in r.rglob('*.png') if p not in f.parents},indent=2)+'\n');shutil.copy2(r/'review.html',p/'review-before.html')
for row,(left,right) in enumerate([(9,8),(10,7),(6,5),(4,3),(2,1)]):
 for name,x,width in [(left,0,512),(right,512,129)]:
  a=parts[name];src=Path(a['original']);dest=p/f'image-{name}-source.png';shutil.copy2(src,dest);im=Image.open(src).convert('RGBA');height=min(512,2533-row*512);core.paste(im.crop((0,0,width,height)),(x,row*512));refs.append(dict(image=name,source_id=a['source_id'],source_sha256=sha(src),size=list(im.size),texel_master_offset=[x,row*512],used_uv=[0,0,width,height],runtime_part=a['part'],runtime_positions=a['quantized_positions'],runtime_matrix=a['material_matrix']))
core.save(p/'scene-source.png');core.resize((1923,7599),Image.Resampling.BILINEAR).save(p/'scene-native-preview.png');faith=core.resize((2564,10132),Image.Resampling.LANCZOS);faith.save(p/'scene-faithful.png')
# Full-height extension canvas at native density; tool output is normalized later.
target=Image.new('RGB',(1707,2533),'#686868');target.paste(core.convert('RGB'),(533,0));target.save(p/'wide-target.png');core.convert('RGB').save(p/'source-reference.png')
(p/'references.json').write_text(json.dumps(dict(movie='trans/t1',study='Continuous texel-space source reconstruction,not a runtime render',source_size=[641,2533],viewport_native=[0,0,640,480],extension_target=[1707,2533],target_original_origin=[533,0],parts=refs,runtime_exception='Bitmap9/part1 decodes at x512..1024,y512..1024 while material translation is0,0; baseline trace agrees. Texel study places its image at top-left by visual source continuity,not as proof of runtime placement. No geometry repair or registration until runtime verified.',fractional_uv_note='Other row coordinates include ~.042native-px accumulation; study uses integer source texels. Preserve exact runtime matrices independently.'),indent=2)+'\n');print('Prepared continuous641x2533source;1707x2533extensiontarget;tenoriginaltiles retained')
