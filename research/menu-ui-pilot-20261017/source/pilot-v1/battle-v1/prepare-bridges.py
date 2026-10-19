from pathlib import Path
from PIL import Image,ImageDraw
import json
p=Path(__file__).resolve().parent;rows=[]
for label in ['cmtype','chooseF2','chooseF3','chooseF4']:
 im=Image.open(p/(label+'-wide-draft.png')).convert('RGB')
 for side in ['left','right']:
  left=side=='left';crop=(576,0,2112,1440) if left else (3008,0,4544,1440);target=im.crop(crop);d=ImageDraw.Draw(target);d.rectangle((512,0,1023,1439),fill='black');name=label+'-'+side+'-bridge';target.save(p/(name+'-target.png'));guide=target.copy();d=ImageDraw.Draw(guide);d.rectangle((512,0,1023,1439),outline='#ff40d0',width=5);d.line((1024 if left else 512,0,1024 if left else 512,1439),fill='#40ffff',width=4);guide.save(p/(name+'-guide.png'))
  material=('BRICK MASONRY ONLY in the gap. Extend each original brick/mortar course LEFT from x1024, matching its precise height,slope,brick size and surface color. The original brick-to-plaster corner is farther RIGHT inside fixed context; no extra corner/plastercolumn in gap. Continue upper teal beam y0..78. The lower brick slab extends offscreen downward toleft; do not invent a floor line.' if left else 'Blue-green plaster wall with upper teal beam and bottom floor line. Extend exact beam edges and wall/floor intersection from original LEFT512context, same height and perspective. No corner,column,pipe,light,posters.') if label=='cmtype' else 'Blue-green rough plaster ONLY. Absolutely no extra paper/photo frames,portraits,panels,logos,writing,objects. Follow local source stains/material softly through gap.'
  prompt=f'''Use case: precise-object-edit
Asset: focused {label} {side.upper()} original4:3 boundary repair.
Image1 EDIT TARGET1536x1440: ONLY middle512columns x512..1024 (black EMPTY GAP) need new paint. Image2 GUIDE ONLY pink gap,cyan original join. Image3 REFERENCE ONLY full original center.
Left512 and right512 of target are fixed context; preserve positions and original colors. {'RIGHT512 is authoritative original source; LEFT512 generated outer context' if left else 'LEFT512 is authoritative original source; RIGHT512 generated outer context'}. Fill gap connecting BOTH sides so no visual break,vertical stripe or band at x512 OR x1024. {material}
Match original local brightness/hue, diffuse lighting and mild optical blur. Added paint must be as soft as original: no crisp invented pores/grain beside smooth original. No sudden blur stripe,stretched vertical streak,mirrored/repeating source strip,edge-hold,duplicate stain,sharpness seam or dark/bright gradient border. Continue structural lines across fullheight, not just top. No warming/yellowing,whitebalance/exposure/contrast/saturation changes. Fill only gap; do not alter either context,crop,zoom,rotate,change perspective or addobjects. Full1536x1440sameaspect opaque output with NOguides. Final assembly retains both contexts exactly.'''
  rows.append(dict(label=name,menu=label,side=side,kind='boundary bridge',crop=list(crop),domain=[crop[0]+512,0,512,1440],prompt=prompt,referenced_image_paths=[str(p/(name+'-target.png')),str(p/(name+'-guide.png')),str(p/(label+'-center.png'))],transparent_background=False))
(p/'bridge-jobs.json').write_text(json.dumps(rows,indent=2)+'\n')
