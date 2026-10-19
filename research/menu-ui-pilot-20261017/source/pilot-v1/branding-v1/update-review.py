"""Add source/faithful/restrained/raw menu branding review without workshop writes."""
from pathlib import Path
p=Path(__file__).resolve().parent.parent/'review.html'
s=p.read_text()
assert 'id="brand-asset"' not in s
style='''
.brand-stage{background:#282828;border:1px solid #46503c;display:flex;align-items:center;justify-content:center;min-height:100px}
.brand-stage img{background:transparent;max-height:530px;object-fit:contain;width:100%;height:100%}
.brand-stage[data-bg="light"]{background:#e8e8e8}
.brand-stage[data-bg="checker"]{background-color:#333;background-image:linear-gradient(45deg,#555 25%,transparent 25%),linear-gradient(-45deg,#555 25%,transparent 25%),linear-gradient(45deg,transparent 75%,#555 75%),linear-gradient(-45deg,transparent 75%,#555 75%);background-size:24px 24px;background-position:0 0,0 12px,12px -12px,-12px 0}
.brand-stage[data-channel="alpha"]{background:#000}
#brand-panel .row{align-items:start}#brand-panel strong{display:block;margin-bottom:8px}
'''
s=s.replace('</style>',style+'</style>',1)
section='''
<section id="brand-panel">
<h2>Title logo &amp; menu emblems · new restoration drafts</h2>
<p>Nine new drafts: the title wordmark and eight selected-mode door emblems. Original colors, worn finish and silhouettes guide the restrained versions. These centered graphics use the same textures across aspect ratios. All new drafts await approval.</p>
<select id="brand-asset" aria-label="Branding asset"><option value="title-logo">Title · Def Jam Fight for NY wordmark</option><option value="emblem-story">Story · book</option><option value="emblem-battle">Battle · fist</option><option value="emblem-options">Options · speaker</option><option value="emblem-jukebox">Jukebox · headphones</option><option value="emblem-extras">Extras · disc</option><option value="emblem-high-scores">High Scores · trophy</option><option value="emblem-rewards">Rewards · open padlock</option><option value="emblem-credits">Credits · filmstrip</option></select>
<select id="brand-ref" aria-label="Branding reference"><option value="source">Original native textures</option><option value="faithful">Faithful HD baseline</option></select>
<select id="brand-version" aria-label="Branding version"><option value="restrained">Restrained restoration · unapproved</option><option value="raw">Raw AI proposal · unapproved</option></select>
<select id="brand-bg" aria-label="Branding background"><option value="dark">Dark</option><option value="light">Light</option><option value="checker">Checkerboard</option></select>
<select id="brand-channel" aria-label="Branding channel"><option value="rgba">Color + transparency</option><option value="alpha">Alpha coverage</option></select>
<div class="row"><div><strong id="brand-ref-label">Original native textures</strong><div class="brand-stage" data-bg="dark"><img id="brand-original" alt="Original menu branding texture"></div></div><div><strong id="brand-result-label">Restrained restoration · unapproved</strong><div class="brand-stage" data-bg="dark"><img id="brand-result" alt="Unapproved restored menu branding texture"></div></div></div>
<p id="brand-caption"></p>
<p><a id="brand-original-link" target="_blank" rel="noopener">Open original PNG</a> · <a id="brand-result-link" target="_blank" rel="noopener">Open candidate PNG</a></p>
<details><summary>Restoration records and original fragment mapping</summary><p>The actual door emblems use 21 source fragments. Their original alpha, strong lettering/stroke edges, tile joins and unused texels stay exact in the restrained candidates. Only bounded fine surface detail changes. Raw proposals can change framing, shapes and brightness; they are retained for comparison. Press Start fragments and the six separate support icons remain source references in this batch.</p><p><a href="branding-v1/generations.json">Exact prompts and raw provenance</a> · <a href="branding-v1/restoration-receipt.json">Color, alpha and protected-pixel checks</a> · <a href="branding-v1/emblem-geometry.json">Eight-mode source geometry</a> · <a href="branding-v1/city-approval.json">City approval</a> · <a href="branding-v1/original-restored-contact.jpg">All nine original/restored pairs</a></p></details>
</section>
'''
s=s.replace('<h2>Background studies · approval status by layer</h2>',section+'<h2>Background studies · approval status by layer</h2>',1)
js='''
const brandSizes={'title-logo':[2048,512],'emblem-story':[768,640],'emblem-battle':[768,768],'emblem-options':[576,576],'emblem-jukebox':[512,640],'emblem-extras':[768,512],'emblem-high-scores':[512,768],'emblem-rewards':[640,640],'emblem-credits':[640,768]};
function branding(){
 const a=document.querySelector('#brand-asset').value,ref=document.querySelector('#brand-ref').value,v=document.querySelector('#brand-version').value,channel=document.querySelector('#brand-channel').value,bg=document.querySelector('#brand-bg').value;
 const original='branding-v1/'+a+'-'+ref+'.png',result='branding-v1/'+a+'-'+v+'.png';
 document.querySelector('#brand-original').src=channel==='alpha'?original.replace('.png','-alpha.png'):original;
 document.querySelector('#brand-result').src=channel==='alpha'?result.replace('.png','-alpha.png'):result;
 document.querySelector('#brand-original-link').href=original;document.querySelector('#brand-result-link').href=result;
 document.querySelector('#brand-ref-label').textContent=document.querySelector('#brand-ref').selectedOptions[0].textContent;
 document.querySelector('#brand-result-label').textContent=document.querySelector('#brand-version').selectedOptions[0].textContent;
 for(const e of document.querySelectorAll('.brand-stage')){e.dataset.bg=bg;e.dataset.channel=channel;e.style.aspectRatio=brandSizes[a][0]+'/'+brandSizes[a][1];}
 document.querySelector('#brand-caption').textContent=document.querySelector('#brand-asset').selectedOptions[0].textContent+' · '+brandSizes[a].join('×')+' source-aligned candidate'+(v==='restrained'?' · original alpha and protected structure unchanged':' · raw proposal uses its returned canvas and needs registration; no game-ready mapping');
}
for(const id of ['brand-asset','brand-ref','brand-version','brand-bg','brand-channel'])document.getElementById(id).onchange=branding;
branding();
'''
s=s.replace('</script>',js+'</script>')
p.write_text(s)
print('Nine-asset branding comparison section added; older scenery/review controls preserved')
