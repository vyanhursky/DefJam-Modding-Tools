import './review_navigation.mjs';
const $=id=>document.getElementById(id);
async function start(){const response=await fetch('native-playtest-rc2/data.json');if(!response.ok)throw Error('Native receipts unavailable');const data=await response.json();$('notes').textContent=data.notes;
for(const [i,run] of data.runs.entries())$('run').add(new Option(run.label,String(i)));
function paint(){const r=data.runs[Number($('run').value)],f=r.images[Number($('frame').value)];$('image').src=f.path;$('caption').textContent=r.label+' · '+f.label;$('receipt').textContent=r.revision+' · '+r.log+' · save restored: '+r.save_ok+' · runtime fault checks: '+(r.faults.length?r.faults.join(', '):'none');$('prev').disabled=$('frame').selectedIndex===0;$('next').disabled=$('frame').selectedIndex===$('frame').length-1;}
function load(){const r=data.runs[Number($('run').value)];$('frame').replaceChildren();for(const [i,im] of r.images.entries())$('frame').add(new Option(im.label,String(i)));const preferred=r.images.findIndex(im=>im.label==='1.5s');$('frame').selectedIndex=Math.max(0,preferred);paint();}
function step(delta){$('frame').selectedIndex=Math.max(0,Math.min($('frame').length-1,$('frame').selectedIndex+delta));paint();}
$('run').onchange=load;$('frame').onchange=paint;$('prev').onclick=()=>step(-1);$('next').onclick=()=>step(1);$('frame').onkeydown=e=>{if(e.key==='ArrowLeft'||e.key==='ArrowRight'){e.preventDefault();step(e.key==='ArrowLeft'?-1:1);}};
const best=data.runs.findIndex(r=>r.route==='loading'&&r.aspect==='32x9'&&r.mode==='all');$('run').selectedIndex=Math.max(0,best);load();}
start().catch(e=>$('error').textContent=e.message);
