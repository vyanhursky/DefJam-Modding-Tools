"""Build bounded 3:1 outpaint targets around final actual source pixels."""
from pathlib import Path
import hashlib,json
from PIL import Image,ImageDraw

root=Path(__file__).resolve().parent
scale=4
def load(label):return Image.open(root/(label+'-restrained.png')).convert('RGBA')
def crop_surround(sheet):
    out=Image.new('RGBA',(2050,1920))
    out.paste(sheet.crop((0,0,1796,1920)),(0,0))
    out.paste(sheet.crop((2048,0,2304,1920)),(1794,0))
    return out
def wall(sheet,lit=False):
    if lit:return sheet.crop((0,0,1280,1920))
    out=Image.new('RGBA',(1278,1920))
    out.paste(sheet.crop((0,0,1024,1920)),(0,0))
    out.paste(sheet.crop((1024,0,1280,1920)),(1022,0))
    return out
surround=crop_surround(load('mode-surround'))
shutter=load('mode-shutter').crop((0,0,920,1416))
for state in ['dark','lit']:
    scene=Image.new('RGBA',(3315,1920),(0,0,0,255))
    poster=(Image.open(root.parent/'mode-wall-dark-palette-constrained-trial.png').convert('RGBA') if state=='dark' else load('mode-wall-lit'))
    scene.alpha_composite(wall(poster,state=='lit'),(-11,0 if state=='dark' else 2))
    scene.alpha_composite(shutter,(1377,390))
    scene.alpha_composite(surround,(1265,0))
    scene.save(root/('mode-environment-'+state+'-layout4x.png'))
    scene.resize((2486,1440),Image.Resampling.LANCZOS).save(root/('mode-environment-'+state+'-known3x.png'))

records=[]
for label,height in [('title-middle',310),('title-tower',446),('mode-environment',480)]:
    # A3:1 proposal canvas, including lower padding. Final masters restore exact3x center.
    target=Image.new('RGBA',(3072,1024),(0,0,0,0))
    if label.startswith('title'):
        center=load(label).resize((1152,922),Image.Resampling.LANCZOS)
        target.paste(center,(960,0))
        protected=[960,0,1152,922]
        active=int(round(height*1.8))
        specifics=('Keep the existing industrial street/brick buildings at their exact scale. Extend rooftops, cables and streets naturally on both sides, with the same perspective and building heights. Preserve the alpha silhouette above roofs; no sky background.' if label=='title-middle' else
            'There is ONE water tower at the left of the original center. Continue its cropped LEFT circumference, railing and roof edge naturally into the left extension, then continue the rooftop plane. Do not duplicate or move that tower. On the right, extend only the sloping dark roof with the same perspective. Keep empty space above the roof transparent, no sky background.')
    else:
        known=Image.open(root/'mode-environment-dark-known3x.png').resize((1492,864),Image.Resampling.LANCZOS)
        target.paste(known,(960,0))
        protected=[960,0,1492,864]
        active=864
        specifics='Extend only the exposed aged brick/plaster wall at the LEFT and the retained offstage right wall at the RIGHT. The poster collage, lamp, doorway and shutter are all original protected center/context. NO new/duplicated posters, symbols, letters, doors or lamps. Continue masonry courses, mortar height, brick size, grime and the local dark olive lighting across both side boundaries. This output is an environment layout study; do not invent menu controls.'
    p=root/(label+'-outpaint-target.png');target.save(p)
    guide=target.copy();d=ImageDraw.Draw(guide)
    x,y,w,h=protected
    d.rectangle((x,y,x+w-1,y+h-1),outline='#55eaff',width=5)
    d.line((0,active,3071,active),fill='#ff65c0',width=4)
    guide.save(root/(label+'-outpaint-guide.png'))
    prompt=f'''Use case: precise-object-edit.
Asset: wide game-menu scenery layer; extend the supplied FINAL assembled target horizontally.
Image1 is the3072x1024 edit canvas with the real protected source already placed. Image2 is a guide only: cyan encloses protected context; pink marks the bottom of the active layer. Image3 is wider style context/reference; do not copy its sky into a transparent foreground layer.
Return the full3072x1024canvas, same framing/scale/registration. Protected original/context rectangle[x,y,width,height]={protected}; do not redraw or move it. Paint only the blank generated-side regions LEFT ofx{x} and RIGHT ofx{x+w}, above active height{active}. Keep the original padding below the active layer untouched. The left extension's RIGHT boundary meets the original's LEFT boundary; right extension's LEFT boundary meets retained original right context.
Continue the SAME existing structural features at their exact height, direction, curvature, thickness, scale, softness and local lighting through the joins. Follow the original roof edges, masonry courses, perspective lines and alpha silhouette through the ENTIRE active height, including lowest roof/haze/black transitions. No vertical cutoff, restarted texture field, flat blur band, mirrored or duplicated patterns, sudden color band or changed perspective. Use the real source in this canvas as fixed boundary conditions, not a generally similar replacement scene.
{specifics}
Keep restrained source detail and the accepted palette/lighting. No added warmth/yellowness, orange/sepia grade, exposure boost, bloom, contrast boost or new light source. Existing amber light remains at its original hue. No new text/watermark/objects beyond the necessary architectural continuation. Do not draw guide marks. Keep genuine alpha cutouts transparent and black opaque padding black. We will enforce exact protected pixels after generation, then inspect BOTH assembled joins full-height at every aspect; make the added content match that real protected context.
'''
    (root/(label+'-outpaint-prompt.txt')).write_text(prompt)
    records.append(dict(label=label,target=p.name,size=[3072,1024],protected=protected,active_height=active,
        final_scale='Normalize proposal to5120x1707 then crop top1536(title)/1440(menu); exact3x center/context copied back'))
(root/'outpaint-layout.json').write_text(json.dumps(dict(schema=1,records=records,
    menu_preview='Nominal idle transforms rounded to nearest4x pixel; full-strength dark/lit envelopes, no spotlight/text/mask/game raster claim'),indent=2))
