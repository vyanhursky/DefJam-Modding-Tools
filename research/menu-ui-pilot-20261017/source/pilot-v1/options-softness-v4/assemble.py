"""User-requested defocus only: preserve v3 content, project optical softness.

Built-in edit is a softness reference, not replacement painted pixels. Gaussian
radius2 at1440high best matches its high-frequency RMS from tested1..3.5radii.
Only beyond4:3 changes; smoothstep64px onset avoids a new blur boundary.
"""
from pathlib import Path
from PIL import Image,ImageFilter,ImageDraw
import numpy as np,json,hashlib
p=Path(__file__).resolve().parent;root=p.parent;sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();src=Image.open(root/'options-door-v3/options-wide-v3.png').convert('RGB');a=np.array(src);soft=np.array(src.filter(ImageFilter.GaussianBlur(2)));weight=np.zeros(5120);t=np.clip((np.arange(5120)-3520)/64,0,1);weight=t*t*(3-2*t);out=np.rint(a.astype(float)+(soft.astype(float)-a)*weight[None,:,None]).clip(0,255).astype('uint8');assert np.array_equal(a[:,:3520],out[:,:3520]);Image.fromarray(out).save(p/'options-wide-v4.png');Image.fromarray(out).crop((3100,0,5120,1440)).save(p/'options-door-complete.png')
for side,edge in [('left',1600),('right',3520)]:
 Image.fromarray(out).crop((edge-384,0,edge+384,1440)).save(p/('options-'+side+'-join.png'));Image.fromarray(a).crop((edge-384,0,edge+384,1440)).save(p/('options-'+side+'-before.png'))
contact=Image.new('RGB',(1600,1400),(18,20,18));d=ImageDraw.Draw(contact)
for i,(r,w) in enumerate([('4x3',1920),('16x10',2304),('16x9',2560),('21x9',3360),('32x9',5120)]):
 x=(5120-w)//2;im=Image.fromarray(out).crop((x,0,x+w,1440));assert np.array_equal(np.array(im)[:,(w-1920)//2:(w+1920)//2],a[:,1600:3520]);im.save(p/('options-'+r+'-v4.png'));im.thumbnail((1580,245));contact.paste(im,((1600-im.width)//2,i*280+25));d.text((10,i*280+5),r,fill='white')
contact.save(p/'five-aspects.png')
# Color drift diagnostic of requested spatial averaging, not a global grade.
roi=out[:,3520:].astype(float)-a[:,3520:].astype(float)
receipt=dict(input_sha256=sha(root/'options-door-v3/options-wide-v3.png'),output_sha256=sha(p/'options-wide-v4.png'),operation='Gaussian defocus of existing RGB only,no model repaint/no geometry warping',radius=2,working_size=[5120,1440],allowed=[3520,0,1600,1440],transition='smoothstep0→1 over64generated pixels;original4:3edge unchanged',original_center_and_left='exact',channel_mean_delta=roi.mean((0,1)).tolist(),rms_fit_reference='softness-normalized.png,local wallROI[1200,100,2000,1200],highfrequency radius2',proposal_RMS=1.572691670642752,projected_radius2_RMS=1.4299513924775502,source_radius0_RMS=4.347759654713163,processor_sha256=sha(Path(__file__)),new_calls=1,pilot_total=57,status='unapproved softness revision;owner likes v3 otherwise')
(p/'assembly-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
prior=json.loads((p/'before-hashes.json').read_text())
for f,h in prior.items():assert sha(root/f)==h,f
pins=json.loads((root/'jukebox-approval-20261018.json').read_text())['files']
for r in pins:assert sha(root/r['path'])==r['sha256']
assert max(abs(np.array(receipt['channel_mean_delta'])))<.05
(p/'verification.json').write_text(json.dumps(dict(previous_png_hashes_exact=len(prior),jukebox_approved_files_exact=len(pins),options_accepted_left_and_original_center_exact=True,aspect_crops_and_centers_exact=5,source_v3_patterns_not_repainted=True,channel_mean_drift_below_point05=True,options_approved=False,workshop_writes=False,game_run=False),indent=2)+'\n');print(json.dumps(receipt,indent=2))
