from pathlib import Path
root=Path(__file__).resolve().parent
p=root.parent/'review.html'
s=p.read_text()
(root/'review-before-comparison.html').write_text(s)
css='''
.study-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px}
.study-card{min-width:0}.study-card strong{display:block;margin:0 0 9px}
#study-wipe{display:none;position:relative}.study-over{position:absolute;inset:0;clip-path:inset(0 0 0 50%)}
.study-divider{position:absolute;left:50%;top:0;bottom:0;border-left:2px solid #e4ed99;pointer-events:none}
.study-wipe-labels{position:absolute;top:10px;left:10px;right:10px;display:flex;justify-content:space-between;pointer-events:none}
.study-wipe-labels span{background:#111d;padding:6px 10px;border-radius:4px}
#study-comparison[data-mode="wipe"] .study-grid{display:none}
#study-comparison[data-mode="wipe"] #study-wipe{display:block}
#study-comparison[data-mode="draft"] .study-original-card{display:none}
#study-comparison[data-mode="draft"] .study-grid{grid-template-columns:1fr}
#wipe-controls{max-width:650px;margin:12px auto}#study-divider-input{width:100%;accent-color:#d8e592}
#wipe-controls label{display:block}#study-links a{margin-right:15px}
@media(max-width:750px){.study-grid{grid-template-columns:1fr}}
'''
s=s.replace('</style>',css+'</style>',1)
old='''<button id="study-bounds" aria-pressed="false">Show original4:3 area</button>
<div class="frame" id="study-frame"><img id="study-image" alt="Unapproved layered background study"><div class="safe" id="study-area"></div></div>
<p id="study-caption"></p>'''
new='''<select id="study-view" aria-label="Comparison view"><option value="side">Side by side</option><option value="wipe">Wipe comparison</option><option value="draft">Draft only</option></select>
<select id="study-framing" aria-label="Comparison framing"><option value="full">Full selected aspect</option><option value="center">Original4:3 center · close comparison</option></select>
<button id="study-bounds" aria-pressed="false">Show original4:3 area</button>
<p>Left: original native textures, enlarged with linear sampling in the same layer layout. Black side margins mark where the original4:3 image ends. Right: the current restoration and scenery draft. Choose the4:3 center to compare original detail at the same scale.</p>
<div id="study-comparison" data-mode="side">
<div class="study-grid">
<div class="study-card study-original-card"><strong>Original textures</strong><div class="frame" id="study-original-frame"><img id="study-original" alt="Original native textures in the matching layer layout"><div class="safe" id="study-original-area"></div></div></div>
<div class="study-card"><strong>Current draft</strong><div class="frame" id="study-frame"><img id="study-image" alt="Current layered background draft"><div class="safe" id="study-area"></div></div></div>
</div>
<div class="frame" id="study-wipe"><img id="study-wipe-original" alt="Original textures beneath comparison wipe"><img class="study-over" id="study-wipe-draft" alt="Current draft revealed by comparison wipe"><div class="study-divider" id="study-divider-line"></div><div class="safe" id="study-wipe-area"></div><div class="study-wipe-labels"><span>Original</span><span>Current draft</span></div></div>
<div id="wipe-controls" hidden><label for="study-divider-input">Original / current draft divider · <output id="study-divider-value">50%</output></label><input id="study-divider-input" type="range" min="0" max="100" value="50" aria-label="Original versus draft divider"></div>
</div>
<p id="study-caption"></p><p id="study-links"><a id="study-original-link" target="_blank" rel="noopener">Open original PNG</a><a id="study-draft-link" target="_blank" rel="noopener">Open current PNG</a> · <a href="comparison-v1/receipt.json">Original-reference provenance</a></p>'''
assert old in s;s=s.replace(old,new,1)
start=s.index('function study(){')
end=s.index('\ndocument.querySelector(\'#asset\').onchange',start)
s=s[:start]+'''function setStudyWipe(){
  const value=document.querySelector('#study-divider-input').value;
  document.querySelector('#study-wipe-draft').style.clipPath='inset(0 0 0 '+value+'%)';
  document.querySelector('#study-divider-line').style.left=value+'%';
  document.querySelector('#study-divider-value').value=value+'%';
}
function study(){
  const id=document.querySelector('#study').value,focus=document.querySelector('#study-framing').value==='center';
  const r=focus?'4x3':document.querySelector('#study-aspect').value;
  const original='comparison-v1/'+id+'-'+r+'-original.png',draft='batch2/'+id+'-'+r+'-preview.png';
  document.querySelector('#study-original').src=original;document.querySelector('#study-wipe-original').src=original;
  document.querySelector('#study-image').src=draft;document.querySelector('#study-wipe-draft').src=draft;
  document.querySelector('#study-original-link').href=original;document.querySelector('#study-draft-link').href=draft;
  document.querySelector('#study-aspect').disabled=focus;
  const pct=1920/sizes[r]*100;
  for(const id of ['study-area','study-original-area','study-wipe-area'])Object.assign(document.getElementById(id).style,{width:pct+'%',left:(100-pct)/2+'%'});
  const view=document.querySelector('#study-view').value;
  document.querySelector('#study-comparison').dataset.mode=view;document.querySelector('#wipe-controls').hidden=view!=='wipe';
  document.querySelector('#study-caption').textContent=document.querySelector('#study').selectedOptions[0].textContent+' · '+labels[r]+' · '+sizes[r]+'×1440'+(focus?' · matching original4:3 center':' · centered original versus wide draft')+' · layer-layout study';
  setStudyWipe();
}
for(const id of ['study','study-aspect','study-view','study-framing'])document.getElementById(id).onchange=study;
document.querySelector('#study-divider-input').oninput=setStudyWipe;
document.querySelector('#study-bounds').onclick=e=>{
  const show=!document.querySelector('#study-frame').classList.contains('show');
  for(const id of ['study-frame','study-original-frame','study-wipe'])document.getElementById(id).classList.toggle('show',show);
  e.target.setAttribute('aria-pressed',String(show));
};study();
''' +s[end:]
# The existing per-texture review should also offer the actual original source.
s=s.replace('<select id="version" aria-label="Generation revision">',
    '<select id="baseline-mode" aria-label="Texture reference"><option value="source">Original native texture</option><option value="faithful">Faithful HD baseline</option></select>\n<select id="version" aria-label="Generation revision">',1)
s=s.replace('<strong>Accepted faithful baseline</strong><img id="baseline"', '<strong id="baseline-label">Original native texture</strong><img id="baseline"',1)
s=s.replace("document.querySelector('#baseline').src=a+'-faithful.png';", "const ref=document.querySelector('#baseline-mode').value;document.querySelector('#baseline').src=a+'-'+ref+'.png';document.querySelector('#baseline-label').textContent=ref==='source'?'Original native texture':'Faithful HD baseline';",1)
s=s.replace("document.querySelector('#asset').onchange=comparison;", "document.querySelector('#baseline-mode').onchange=comparison;document.querySelector('#asset').onchange=comparison;",1)
p.write_text(s)
print('Original/draft side-by-side, wipe, center framing and native texture references added')

# Final label/alt-text refinement, retained with the original patch.
s=p.read_text().replace('Original4:3','Original 4:3').replace('original4:3','original 4:3')
s=s.replace('alt="Faithful original palette and composition"','alt="Original native texture reference"')
needle="document.querySelector('#baseline-label').textContent=ref==='source'?'Original native texture':'Faithful HD baseline';"
s=s.replace(needle,needle+"document.querySelector('#baseline').alt=ref==='source'?'Original native texture reference':'Faithful HD enlargement of original texture';")
p.write_text(s)
