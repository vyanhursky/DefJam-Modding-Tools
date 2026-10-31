from pathlib import Path
import json
p=Path(__file__).resolve().parent
scenes={'cmtype':'Blue-green industrial plaster/brick room, rusty overhead pipe, fluorescent tube, faded posters, graffiti, small lower pipe and floor. Preserve all existing words and poster marks; never invent legible text.', 'chooseF2':'Two large worn paper portrait backing frames on blue-green plaster. Preserve exactly TWO frames, every slant, black inset, paper silhouette and spacing. Do not add portraits or lettering.', 'chooseF3':'Three narrower worn paper portrait backing frames on blue-green plaster. Preserve exactly THREE frames, every slant, black inset, paper silhouette and spacing. Do not add portraits or lettering.', 'chooseF4':'Four worn paper portrait backing frames on blue-green plaster. Preserve exactly FOUR frames, every slant, black inset, paper silhouette and spacing. Do not add portraits or lettering.'}
jobs=[]
for label,scene in scenes.items():
 prompt=f'''Use case: precise-object-edit
Asset type: Def Jam Fight for NY menu texture, Rich Original Detail restoration.
Image1 is the native EDIT TARGET640x512. Restore/upscale the same full canvas with restrained compression cleanup. {scene}
Keep exact camera/layout/geometry and existing edge softness, deliberate wear, marks, dark areas and broad lighting. Preserve blue-green/cyan-gray plaster and original cream paper, original local color accuracy; NO warming/yellowing, neutralizing cool room, white balance/exposure/contrast/saturation shift. No invented sharp grain, outlines, bevel, halo, clean white paper or glossy material. Source lower32rows are stored padding, not extra scene. No cropping/reframing/zoom/perspective/rotation. Preserve all transparency/alpha; do not substitute black for translucent parts. Return full same5:4canvas at higher resolution. Final source-aligned assembly will keep original alpha, protected frame/lettering graphics, padding, tile join and broad spatial colors; only tiny fine brightness detail may be adopted.'''
 jobs.append(dict(label=label,kind='restoration',prompt=prompt,referenced_image_paths=[str(p/(label+'-source.png'))],transparent_background=label=='cmtype'))
(p/'restoration-jobs.json').write_text(json.dumps(jobs,indent=2)+'\n')
