from pathlib import Path
import json
root=Path(__file__).resolve().parent
descriptions={
'title-middle':'Layer of old industrial brick rooftops, streets, cables, windows and factory buildings. Keep every building, cable and silhouette fixed. Retain the source amber street lighting exactly; do not add a warmer grade. No skyline or sky should fill the transparent cutout above the buildings.',
'title-tower':'Foreground rooftop and a single large wooden water tower on the LEFT. Preserve the tower cylinder, roof, railing, legs, their exact positions and the sloping roof plane. Do not duplicate the tower. Preserve the transparent space behind/above the roof and tower.',
'mode-shutter':'Grimy horizontal metal rolling shutter. Preserve every horizontal slat, its spacing, scratches, grime distribution and the broad light falloff. No lettering/emblem; those are separate animated game layers. Do not straighten, relight or redesign the aged source.',
'mode-surround':'Brick wall and doorway surround with lamp at upper left and an existing dark diamond poster/emblem. Preserve the poster graphic, paper edges, lamp, doorframe, bricks and their exact locations. The doorway cutout and bottom/side padding are transparent or unused; do not fill them or paint green into them.'}
common='''Use case: precise-object-edit.
Asset: an upscaled source-faithful menu texture layer from Def Jam: Fight for NY.
Image1 is the exact source RGBA edit target; image2 is its faithful enlargement as reference. Return the same full canvas/aspect and coordinate registration, at higher useful detail. Preserve the composition exactly. Perform only restrained cleanup of compression stair steps and muddy surface texture; do not redesign or invent objects. Original hue/saturation, broad lighting, contrast and deliberate grit are the authority. Do not make it warmer/yellower or orange/sepia. Preserve any original warm light already present instead of neutralizing it. No new light, bloom or exposure boost. Keep lettering, logos and graphics exactly. Preserve alpha/transparency and black padding. No crop, shift, rotation or perspective change. No new text/watermark. Output will be technically assembled with exact protected original pixels and alpha; this is not permission to redraw protected features.
'''
for label,description in descriptions.items():
    (root/(label+'-restoration-prompt.txt')).write_text(common+'\nSpecific layer: '+description+'\n')
print(json.dumps(list(descriptions)))
