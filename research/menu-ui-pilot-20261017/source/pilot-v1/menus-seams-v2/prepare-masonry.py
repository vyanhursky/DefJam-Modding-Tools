from pathlib import Path
from PIL import Image,ImageDraw
import json
p=Path(__file__).resolve().parent
ys={'left':[92,292,486,680,880,1080,1280],'right':[84,278,480,676,868,1070,1250]}
for side in ['left','right']:
 im=Image.open(p/('jukebox-'+side+'-target.png')).convert('RGB');join=1600 if side=='left' else 720;rect=(0,0,join,1440) if side=='left' else (join,0,2320,1440);im.paste((55,46,34),rect);im.save(p/('jukebox-'+side+'-blank-target.png'));guide=im.copy();d=ImageDraw.Draw(guide)
 for y in ys[side]:d.line((0 if side=='left' else join,y,join if side=='left' else 2319,y),fill='#ff55dd',width=3)
 d.line((join,0,join,1439),fill='cyan',width=4);guide.save(p/('jukebox-'+side+'-course-guide.png'))
(p/'course-landmarks.json').write_text(json.dumps(dict(approximate_visual_mortar_bed_anchors=ys,note='Guide trajectories, not measured acceptance metrics. Final fixed original edge governs every contour.'),indent=2)+'\n')
