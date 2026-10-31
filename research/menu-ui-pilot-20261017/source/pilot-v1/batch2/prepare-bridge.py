from pathlib import Path
import json
from PIL import Image,ImageDraw
root=Path(__file__).resolve().parent
defs=[dict(label='title-tower-right',parent='title-tower-assembled-proposal.png',crop=[2752,512,4288,1536],size=[1536,1024],edge=768,side='right',active=826),
      dict(label='mode-environment-left',parent='mode-environment-assembled-proposal.png',crop=[880,0,2320,1440],size=[1024,1024],edge=512,side='left',active=1024)]
for row in defs:
    image=Image.open(root/row['parent']).convert('RGBA').crop(tuple(row['crop'])).resize(tuple(row['size']),Image.Resampling.LANCZOS)
    image.save(root/(row['label']+'-bridge-target.png'))
    guide=image.copy();d=ImageDraw.Draw(guide)
    x0,x1=(768,1280) if row['side']=='right' else (0,512)
    d.rectangle((x0,0,x1-1,row['active']-1),outline='#ff65c0',width=4)
    d.line((row['edge'],0,row['edge'],row['size'][1]-1),fill='#55eaff',width=3)
    guide.save(root/(row['label']+'-bridge-guide.png'))
    if row['side']=='right':
        task='''Repair the stepped ROOF OUTLINE on the RIGHT of the source boundary. The existing roof slopes downward to the right and currently jumps UP at x768 because the generated panel did not follow its height. Continue the exact roof edge from the original LEFT side through the RIGHT editable band, at the same entering height, tangent and downward slope, then curve naturally into the retained outer roof at x1280. Keep the roof surface below that contour opaque and the space above it genuinely transparent. Do not add sky, buildings or objects. Keep only the original roof's perspective, dark texture and color. Do not move or redraw any original roof pixel LEFT ofx768. Edit only x768..1280, y0..826, preserving the rest. This repair includes the entire active roof height; avoid a new step or vertical alpha edge at either end.'''
    else:
        task='''Remove ALL duplicated poster/text fragments LEFT of x512 (the original boundary). They were generated outside the protected real menu. Replace those fragments only with the continuation of the adjacent aged brick/plaster wall and restrained blank/torn paper at the real collage edge; NO added symbols, graphics, letters, poster copies, doors or lamps. The RIGHT half x512..1024 is the actual protected original and must stay unchanged. Edit only LEFT half x0..512 across the full1024height. At x512 continue masonry rows, brick scale, grime and the original local dark fade smoothly into the blank side; keep the original poster collage on the right exactly where it is. A narrow blank paper edge may naturally continue the existing cropped collage, but do not repeat any recognizable original poster. Match retained outer wall at x0. No visible vertical cutoff, sudden brightness/perspective change or blur stripe.'''
    prompt=f'''Use case: precise-object-edit.
Image1 is the exact final assembled edit target {row['size'][0]}x{row['size'][1]}. Image2 is an annotation guide only: cyan is the original boundary, pink is the allowed generated-side edit region. Return image1's full canvas at exactly the same size, registration, scale and crop. Do not output guide marks. Do not recompose or redraw the original protected context.
{task}
Keep the accepted source dark olive/brown palette and grain. No added warmth/yellow/orange, new light, exposure/contrast boost or bloom. Preserve fixed features/alpha, black padding and all outside context. This is a focused seam/duplicate repair, not a new panorama. Match exact boundary shapes and local lighting, not a broadly similar texture.
'''
    (root/(row['label']+'-bridge-prompt.txt')).write_text(prompt)
(root/'bridge-layout.json').write_text(json.dumps(dict(schema=1,records=defs),indent=2))
