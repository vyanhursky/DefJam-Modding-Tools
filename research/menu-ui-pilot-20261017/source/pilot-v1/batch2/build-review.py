from pathlib import Path
import hashlib,json
from PIL import Image
root=Path(__file__).resolve().parent
pilot=root.parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
records=[]
for label in ['title-middle','title-tower','mode-shutter','mode-surround']:
    records.append(dict(label=label,kind='restoration',tool='built-in image_gen.imagegen',
        prompt=(root/(label+'-restoration-prompt.txt')).read_text(),
        inputs=[dict(path=label+'-'+k+'.png',sha256=sha(root/(label+'-'+k+'.png'))) for k in ['source','faithful']],
        raw=label+'-raw.png',raw_sha256=sha(root/(label+'-raw.png')),
        raw_dimensions=list(Image.open(root/(label+'-raw.png')).size),transparent_background=label!='mode-shutter'))
for label in ['title-middle','title-tower','mode-environment']:
    extra=pilot/'seam-v3/title-skyline-wide-master-v3.png' if label.startswith('title') else root/'mode-environment-dark-known3x.png'
    inputs=[root/(label+'-outpaint-target.png'),root/(label+'-outpaint-guide.png'),extra]
    records.append(dict(label=label,kind='outpaint',tool='built-in image_gen.imagegen',
        prompt=(root/(label+'-outpaint-prompt.txt')).read_text(),inputs=[dict(path=str(p),sha256=sha(p)) for p in inputs],
        raw=label+'-outpaint-raw.png',raw_sha256=sha(root/(label+'-outpaint-raw.png')),
        raw_dimensions=list(Image.open(root/(label+'-outpaint-raw.png')).size),transparent_background=label.startswith('title')))
for label in ['title-tower-right','mode-environment-left']:
    records.append(dict(label=label,kind='focused bridge',tool='built-in image_gen.imagegen',
        prompt=(root/(label+'-bridge-prompt.txt')).read_text(),
        inputs=[dict(path=label+'-bridge-'+k+'.png',sha256=sha(root/(label+'-bridge-'+k+'.png'))) for k in ['target','guide']],
        raw=label+'-bridge-raw.png',raw_sha256=sha(root/(label+'-bridge-raw.png')),
        raw_dimensions=list(Image.open(root/(label+'-bridge-raw.png')).size),transparent_background=label.startswith('title')))
(root/'generations.json').write_text(json.dumps(dict(schema=1,calls=records,count=len(records),
    note='Nine additional private built-in calls;18pilot total. Lit wall is derived deterministically, not a separate generation.'),indent=2))
p=pilot/'review.html'
s=p.read_text()
(root/'review-before-batch2.html').write_text(s)
s=s.replace('Private draft study. Nothing here is approved, installed or a game capture.',
    'The isolated skyline v3 is owner-approved artwork. The new background studies below are unapproved. Nothing is installed or presented as a game capture.')
s=s.replace('<h2>Wide skyline · choose aspect</h2>', '<h2>Approved skyline reference · choose aspect</h2>')
section='''<h2>Next background studies · unapproved</h2>
<p>New city and water-tower/roof layers, plus the mode-select environment. Original alpha and padding are protected in the restoration trials; generated side alpha needs art review. Title studies omit the shield, title logo and Press Start sticker. Mode-select is an approximate authored idle layout with dark/lit lighting envelopes, without its animated spotlight, selected-mode emblem or menu text.</p>
<select id="study" aria-label="Background study"><option value="title-layers">Title · skyline + city + water tower</option><option value="title-middle">Title · city over approved skyline</option><option value="title-tower">Title · tower over approved skyline</option><option value="mode-environment">Mode select · dark wall envelope</option><option value="mode-environment-lit">Mode select · lit wall envelope</option></select>
<select id="study-aspect" aria-label="Study aspect"><option value="32x9">32:9</option><option value="21x9">21:9</option><option value="16x9">16:9</option><option value="16x10">16:10</option><option value="4x3">4:3</option></select>
<button id="study-bounds" aria-pressed="false">Show original4:3 area</button>
<div class="frame" id="study-frame"><img id="study-image" alt="Unapproved layered background study"><div class="safe" id="study-area"></div></div>
<p id="study-caption"></p>
<details><summary>Full-height boundary checks and production records</summary>
<p>The approved skyline is unchanged. Center checks pass for all five aspects in each study. The roof's generated right contour was registered to the source plane; the mode wall's duplicated side posters were removed before this preview. Mode-select reuses original offstage wall art through logical x828.63, so16:9's right extension can use original scenery.</p>
<p><a href="skyline-approval.json">Skyline approval and pinned hashes</a> · <a href="batch2/menu-art-workflow.md">Complete approved recipe and reusable production rules</a> · <a href="batch2/generations.json">All nine new prompts, inputs and raw outputs</a> · <a href="batch2/restoration-receipt.json">Restoration color/alpha checks</a> · <a href="batch2/wide-receipt.json">Wide assembly and protected-context checks</a></p>
<p>Full-height PNGs: <a href="batch2/title-middle-left-full-height.png">City left</a> · <a href="batch2/title-middle-right-full-height.png">City right</a> · <a href="batch2/title-tower-left-full-height.png">Tower left</a> · <a href="batch2/title-tower-right-full-height.png">Tower right</a> · <a href="batch2/mode-environment-left-full-height.png">Mode left</a> · <a href="batch2/mode-environment-right-full-height.png">Mode right</a></p>
</details>
'''
s=s.replace('<h2>Approved skyline reference',section+'<h2>Approved skyline reference',1)
new_options=''.join('<option value="batch2/'+a+'">'+label+'</option>' for a,label in [
    ('title-middle','Title city layer'),('title-tower','Title water-tower layer'),('mode-wall-lit','Mode lit wall · shared detail'),('mode-shutter','Mode rolling shutter'),('mode-surround','Mode door surround')])
s=s.replace('<option value="mode-wall-dark">Mode-select dark poster wall</option>', '<option value="mode-wall-dark">Mode-select dark poster wall</option>'+new_options)
s=s.replace('<option value="v1">Initial raw draft1</option>', '<option value="v1">Initial raw draft1</option><option value="batchraw" disabled>Raw new-batch generation</option>')
start=s.index('function comparison(){')
end=s.index('\ndocument.querySelector(\'#asset\').onchange',start)
s=s[:start]+'''function comparison(){const a=document.querySelector('#asset').value,sel=document.querySelector('#version'),batch=a.startsWith('batch2/');for(const o of sel.options)o.disabled=o.value==='batchraw'?(!batch||a.endsWith('mode-wall-lit')):batch&&o.value!=='palette';if(sel.selectedOptions[0].disabled)sel.value='palette';const v=sel.value;document.querySelector('#baseline').src=a+'-faithful.png';document.querySelector('#draft').src=batch?a+(v==='batchraw'?'-raw.png':'-restrained.png'):a+(v==='palette'?'-palette-constrained-trial.png':'-raw-'+v+'.png');document.querySelector('#draft-label').textContent=v==='palette'?'Unapproved source-palette trial':'Unapproved raw imagegen draft';const d=data?.[a+(v==='palette'?'-palette':v==='v2'?'-v2':'')];document.querySelector('#metrics').textContent=d?'Median ΔLab: '+d.median_Lab_drift.map(n=>(n>=0?'+':'')+n.toFixed(2)).join(' / '):''}
function study(){const id=document.querySelector('#study').value,r=document.querySelector('#study-aspect').value;document.querySelector('#study-image').src='batch2/'+id+'-'+r+'-preview.png';const pct=1920/sizes[r]*100;Object.assign(document.querySelector('#study-area').style,{width:pct+'%',left:(100-pct)/2+'%'});document.querySelector('#study-caption').textContent=document.querySelector('#study').selectedOptions[0].textContent+' · '+labels[r]+' · '+sizes[r]+'×1440 · unapproved art study'}
document.querySelector('#study').onchange=study;document.querySelector('#study-aspect').onchange=study;document.querySelector('#study-bounds').onclick=e=>{const show=document.querySelector('#study-frame').classList.toggle('show');e.target.setAttribute('aria-pressed',String(show))};study();
''' +s[end:]
s=s.replace("fetch('palette-proof-receipt.json').then(r=>r.json())]).then(([d,p])=>{data=d;for(const row of p.records)data[row.label+'-palette']=row;comparison()}",
    "fetch('palette-proof-receipt.json').then(r=>r.json()),fetch('batch2/restoration-receipt.json').then(r=>r.json())]).then(([d,p,b])=>{data=d;for(const row of p.records)data[row.label+'-palette']=row;for(const row of b.records)data['batch2/'+row.label+'-palette']={median_Lab_drift:row.median_Lab};comparison()}")
p.write_text(s)
print('Review updated; skyline approval and new studies distinguished')
