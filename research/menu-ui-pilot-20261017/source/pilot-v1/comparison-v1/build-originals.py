"""Render original-source-only counterparts for the existing layer studies.

No generated or faithful HD pixels enter these references. Native textures use
linear enlargement and the same nominal layer layout as the draft studies.
The original 4:3 composition is centered; absent wide art remains black.
"""
from pathlib import Path
import hashlib,json
import numpy as np
from PIL import Image

root=Path(__file__).resolve().parent
pilot=root.parent
batch=pilot/'batch2'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
paths={'skyline':pilot/'title-skyline-source.png','dark':pilot/'mode-wall-dark-source.png'}
paths.update({n:batch/(n+'-source.png') for n in ['title-middle','title-tower','mode-wall-lit','mode-shutter','mode-surround']})
expected={r['label']:r['sha256'] for r in json.loads((pilot/'reference-receipt.json').read_text()) if r['kind']=='source'}
expected.update({r['label']:r['variants']['source']['sha256'] for r in json.loads((batch/'references.json').read_text())['records']})
for label,p in paths.items():
    assert sha(p)==expected[{'skyline':'title-skyline','dark':'mode-wall-dark'}.get(label,label)]
def native(label,scale=3):
    im=Image.open(paths[label]).convert('RGBA')
    return im.resize((im.width*scale,im.height*scale),Image.Resampling.BILINEAR)

sky=Image.new('RGBA',(1920,1440),(0,0,0,255))
sky.alpha_composite(native('skyline').crop((0,402,1920,1350)),(0,0))
city=native('title-middle').crop((0,0,1920,930))
tower=native('title-tower').crop((0,0,1920,1338))
scenes={}
for label,layers in [('title-layers',[(city,(0,306)),(tower,(0,48))]),
                     ('title-middle',[(city,(0,306))]),('title-tower',[(tower,(0,48))])]:
    im=sky.copy()
    for layer,pos in layers:im.alpha_composite(layer,pos)
    scenes[label]=im.convert('RGB')

# Match the existing draft's documented nominal idle-layout approximation.
# Source geometry/alpha stay independent of the generated or restrained trials.
surround_sheet=native('mode-surround',4)
surround=Image.new('RGBA',(2050,1920))
surround.paste(surround_sheet.crop((0,0,1796,1920)),(0,0))
surround.paste(surround_sheet.crop((2048,0,2304,1920)),(1794,0))
shutter=native('mode-shutter',4).crop((0,0,920,1416))
for state in ['dark','lit']:
    scene=Image.new('RGBA',(3315,1920),(0,0,0,255))
    sheet=native('dark' if state=='dark' else 'mode-wall-lit',4)
    if state=='lit':wall=sheet.crop((0,0,1280,1920))
    else:
        wall=Image.new('RGBA',(1278,1920))
        wall.paste(sheet.crop((0,0,1024,1920)),(0,0))
        wall.paste(sheet.crop((1024,0,1280,1920)),(1022,0))
    scene.alpha_composite(wall,(-11,0 if state=='dark' else 2))
    scene.alpha_composite(shutter,(1377,390))
    scene.alpha_composite(surround,(1265,0))
    label='mode-environment'+('-lit' if state=='lit' else '')
    scenes[label]=scene.resize((2486,1440),Image.Resampling.LANCZOS).crop((0,0,1920,1440)).convert('RGB')

outputs=[]
for label,center in scenes.items():
    for ratio,width in [('4x3',1920),('16x10',2304),('16x9',2560),('21x9',3360),('32x9',5120)]:
        frame=Image.new('RGB',(width,1440))
        offset=(width-1920)//2
        frame.paste(center,(offset,0))
        p=root/(label+'-'+ratio+'-original.png');frame.save(p)
        pixels=np.array(frame)
        assert np.array_equal(pixels[:,offset:offset+1920],np.array(center))
        assert not pixels[:,:offset].any() and not pixels[:,offset+1920:].any()
        outputs.append(dict(study=label,aspect=ratio,path=p.name,size=list(frame.size),sha256=sha(p)))

approval=json.loads((pilot/'skyline-approval.json').read_text())
assert sha(pilot/'seam-v3/title-skyline-wide-master-v3.png')==approval['master']['sha256']
current_art={str(p.relative_to(pilot)):sha(p) for p in sorted(batch.glob('*-preview.png'))}
receipt=dict(schema=1,processor_sha256=sha(Path(__file__)),
    inputs=[dict(label=k,path=str(p),sha256=sha(p)) for k,p in paths.items()],
    generated_pixels_in_original=False,faithful_hd_pixels_in_original=False,
    sampling='Native source RGBA, linear enlargement, source active bounds; mode same nominal4x idle layout then3x. No invented wider scenery.',
    outputs=outputs,checks='25/25source centers exact, outside original4:3 black',
    current_art_sha256=current_art,approved_skyline_sha256=approval['master']['sha256'])
(root/'receipt.json').write_text(json.dumps(receipt,indent=2))
print('25source-only originals built; source hashes/center/black-side checks pass; current artwork untouched')
