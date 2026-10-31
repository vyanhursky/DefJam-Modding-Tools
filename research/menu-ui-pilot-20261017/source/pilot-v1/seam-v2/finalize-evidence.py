"""Retain exact focused-edit provenance and derive read-only review crops."""
from pathlib import Path
import hashlib
import json
from PIL import Image, ImageDraw

root = Path(__file__).resolve().parent
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
parent = root.parent / 'title-skyline-wide-master-draft.png'
old = Image.open(parent).convert('RGB')
new = Image.open(root/'title-skyline-wide-master-refined.png').convert('RGB')
records = []
default_names = {'left':'exec-7d3ea2a9-3e60-4fd9-bda5-b08a221844ad.png',
                 'right':'exec-de7f8702-3e8e-4afa-be1a-861785e82315.png'}
for side,edge in [('left',1600),('right',3520)]:
    old.crop((edge-384,350,edge+384,800)).save(root/(side+'-before-close.png'))
    inputs = [root/(side+'-join-context.png'), root/(side+'-join-guide.png'), parent]
    prompt = root/(side+'-bridge-prompt.txt')
    raw = root/(side+'-bridge-raw.png')
    records.append(dict(side=side,tool='built-in image_gen.imagegen',
        prompt=prompt.read_text(),prompt_file=prompt.name,prompt_sha256=sha(prompt),
        referenced_image_paths=[str(p) for p in inputs],
        input_hashes=[sha(p) for p in inputs],transparent_background=False,
        raw_file=raw.name,raw_sha256=sha(raw),raw_dimensions=list(Image.open(raw).size),
        default_output='/Users/vlad/.codex/generated_images/01a14a0f-e9c4-74b3-843f-22f3d4aee508/'+default_names[side]))
(root/'generations.json').write_text(json.dumps(dict(schema=1,date='2026-10-17',
    purpose='Focused cloud continuity repair on final assembled skyline',
    calls=records,status='Unapproved private art refinement; two additional built-in calls'),indent=2))
sheet = Image.new('RGB',(1560,984),'#111310')
d = ImageDraw.Draw(sheet)
d.text((16,10),'INITIAL EXTENSION',fill='#e7e9df')
d.text((796,10),'REFINED CLOUD JOINS',fill='#e7e9df')
for y,side in [(42,'left'),(528,'right')]:
    d.text((16,y-16),side.upper()+' ORIGINAL 4:3 EDGE (midpoint of each crop)',fill='#d8e592')
    sheet.paste(Image.open(root/(side+'-before-close.png')),(8,y))
    sheet.paste(Image.open(root/(side+'-refined-close.png')),(788,y))
sheet.save(root/'cloud-joins-before-after.png')
print(json.dumps({'generations':len(records),'comparison':str(root/'cloud-joins-before-after.png')}))
