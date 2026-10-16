'use strict';
const $ = id => document.getElementById(id);
const state = {config:null, asset:null, target:'asset', review:null, page:0, total:0,
  images:[null,null,null,null], lanes:{faithful:'',remaster:''}, pan:[0,0], marking:false,
  pendingRegion:null, dirty:false, saving:null, saveTimer:null, imageToken:0, blink:false};
const canvases = ['canvas-original','canvas-faithful','canvas-a','canvas-b'].map($);
let sessionTimer, searchTimer, resizeObserver;

function message(text, error=false) { const el=$(error?'error':'notice');el.textContent=text;el.hidden=!text; }
function saveStatus(text, failed=false) { $('save-status').textContent=text;$('save-status').classList.toggle('failed',failed); }
async function api(path, body) {
  const response=await fetch(path,body===undefined?{}:{method:'POST',headers:{'Content-Type':'application/json','X-Workshop-Token':state.config.token},body:JSON.stringify(body)});
  const answer=await response.json(); if(!response.ok)throw Error(answer.error||'The workshop could not save this change.');return answer;
}
function draftKey(){return 'defjam-workshop:'+state.config.workspace+':'+state.config.corpus_id+':'+state.asset.id+':'+state.target;}
async function exclusive(action){
  if(state.busy)return;
  state.busy=true;
  const surfaces=[document.querySelector('main'),document.querySelector('.library'),document.querySelector('.sidebar'),document.querySelector('header')];
  surfaces.forEach(el=>el.inert=true);
  try{return await action();}finally{state.busy=false;surfaces.forEach(el=>el.inert=false);}
}
function rememberDraft(){try{localStorage.setItem(draftKey(),JSON.stringify(state.review));}catch(e){message('Browser draft backup unavailable. Disk autosave is still active.',true);}}
function getDraft(){try{return JSON.parse(localStorage.getItem(draftKey())||'null');}catch{return null;}}
function saveSession(){clearTimeout(sessionTimer);sessionTimer=setTimeout(()=>{
  api('/api/session',captureSession()).catch(e=>message('View settings were not saved: '+e.message,true));
},300);}
function captureSession(){return {scope:$('scope').value,fighter:$('fighter').value,category:$('category').value,
  status:$('review-filter').value,q:$('search').value,page:state.page,asset:state.asset?.id,
  target:state.target,lanes:state.lanes,zoom:$('zoom').value,channel:$('channel').value,
  background:$('background').value,pan:state.pan};}
function captureReview(){if(!state.review)return;Object.assign(state.review,{
  notes:$('notes').value,tags:$('tags').value.split(',').map(t=>t.trim()).filter(Boolean),
  flag:$('flag').checked,status:$('verdict').value,face_reviewed:$('face-reviewed').checked,
  channels_reviewed:$('channels-reviewed').checked,game_verified:$('game-verified').checked,
  selected:$('selected').checked,mip_policy:$('mip-policy').value});}
function changed(){captureReview();state.dirty=true;rememberDraft();saveStatus('Saving…');
  clearTimeout(state.saveTimer);state.saveTimer=setTimeout(()=>flush().catch(()=>{}),450);}
async function flush(){
  clearTimeout(state.saveTimer);
  if(state.saving)await state.saving;
  if(!state.dirty||!state.asset)return;
  const ident=state.asset.id,target=state.target,payload=structuredClone(state.review);
  state.dirty=false;
  state.saving=api('/api/review/'+ident+'/'+target,payload).then(saved=>{
    if(state.asset.id===ident&&state.target===target){state.review.version=saved.version;
      state.review.updated=saved.updated;$('review-saved').textContent='Saved '+new Date(saved.updated).toLocaleTimeString();
      if(!state.dirty){localStorage.removeItem(draftKey());$('draft-recovery').hidden=true;}}
    if(state.asset.id===ident){
      if(target==='asset'){state.asset.review=saved;$('asset-flag').setAttribute('aria-pressed',String(saved.flag));}
      else{const c=state.asset.candidates.find(c=>c.id===target);if(c)c.review=saved;
        if(saved.selected)for(const other of state.asset.candidates){if(other.id!==target&&other.review.selected){other.review.selected=false;other.review.version++;}}}
    }
    saveStatus(state.dirty?'Saving…':'All changes saved');message('',true);
  }).catch(e=>{state.dirty=true;rememberDraft();saveStatus('Not saved · draft retained',true);message(e.message,true);throw e;})
    .finally(()=>{state.saving=null;});
  await state.saving;
  if(state.dirty)await flush();
}
function currentCandidate(style){return state.asset?.candidates.find(c=>c.id===state.lanes[style]);}
function targetReview(target){return target==='asset'?state.asset.review:state.asset.candidates.find(c=>c.id===target)?.review;}
function setReview(target){
  if(!targetReview(target))target='asset';state.target=target;state.review=structuredClone(targetReview(target));
  const r=state.review;$('review-target').value=target;$('notes').value=r.notes;$('tags').value=r.tags.join(', ');
  $('flag').checked=r.flag;$('verdict').value=r.status;$('face-reviewed').checked=r.face_reviewed;
  $('channels-reviewed').checked=r.channels_reviewed;$('game-verified').checked=r.game_verified;
  $('selected').checked=r.selected;$('mip-policy').value=r.mip_policy;
  $('candidate-checks').hidden=target==='asset';
  const c=state.asset.candidates.find(c=>c.id===target);
  $('review-title').textContent=c?c.label:'Texture notes';
  $('review-saved').textContent=r.updated?'Saved '+new Date(r.updated).toLocaleString():'';
  const draft=getDraft();$('draft-recovery').hidden=!draft;
  $('asset-flag').setAttribute('aria-pressed',String(state.asset.review.flag));
  renderRegions();draw();saveSession();
}
function renderRegions(){
  $('region-count').textContent=state.review.regions.length;const list=$('regions');list.replaceChildren();
  for(const region of state.review.regions){const row=document.createElement('div');row.className='region-row';
    const content=document.createElement('div'),kind=document.createElement('small'),note=document.createElement('p');
    kind.textContent=region.kind==='protect'?'Protect · unchanged':region.kind==='reference'?'Needs a reference':'Revision request';
    note.textContent=region.note;content.append(kind,note);
    const focus=document.createElement('button');focus.textContent='Locate';focus.onclick=()=>{
      state.pan=[0,0];$('zoom').value='fit';draw();document.querySelector('.comparison').scrollIntoView({behavior:'smooth',block:'start'});};
    const remove=document.createElement('button');remove.textContent='Remove';remove.setAttribute('aria-label','Remove regional note');
    remove.onclick=()=>{state.review.regions=state.review.regions.filter(r=>r.id!==region.id);changed();renderRegions();draw();};
    row.append(content,focus,remove);list.append(row);
  }
}
function filters(){return {scope:$('scope').value,fighter:$('fighter').value,category:$('category').value,
  status:$('review-filter').value,q:$('search').value,page:String(state.page)};}
async function refreshCatalog(){
  const token=(state.catalogToken||0)+1;state.catalogToken=token;
  const data=await api('/api/catalog?'+new URLSearchParams(filters()));if(token!==state.catalogToken)return data;state.total=data.total;
  if(state.page>0&&state.page*30>=data.total){state.page=0;return refreshCatalog();}
  $('count').textContent=data.total.toLocaleString()+' textures';
  $('page-info').textContent=data.total?'Page '+(state.page+1)+' / '+Math.ceil(data.total/30):'';
  $('prev-page').disabled=!state.page;$('next-page').disabled=(state.page+1)*30>=data.total;
  const list=$('asset-list');list.replaceChildren();
  for(const a of data.assets){const button=document.createElement('button');button.className='asset-card';button.dataset.asset=a.id;
    button.classList.toggle('active',state.asset?.id===a.id);
    const img=document.createElement('img');img.src=a.thumbnail;img.alt='';img.loading='lazy';
    const text=document.createElement('div'),title=document.createElement('strong'),meta=document.createElement('small'),badges=document.createElement('small');
    title.textContent=a.fighter?(a.fighter+' · '+a.variant):a.label;
    meta.textContent=a.width+' × '+a.height+' · '+(a.fighter?(a.role.startsWith('Primary')?'Main atlas':'Secondary map'):a.browse_categories[0]);
    badges.textContent=[a.flag?'⚑ Flagged':'',a.notes?'Notes':'',a.candidates?a.candidates+' revisions':'',a.selected?'Selected':''].filter(Boolean).join(' · ');
    if(a.flag)badges.className='flag-indicator';text.append(title,meta,badges);button.append(img,text);
    button.onclick=()=>openAsset(a.id).catch(e=>message(e.message,true));list.append(button);
  }
  if(!data.assets.length){const p=document.createElement('p');p.className='muted small';p.textContent='No textures match these filters.';list.append(p);}
  saveSession();return data;
}
async function openAsset(ident,options={}){return exclusive(()=>loadAsset(ident,options));}
async function loadAsset(ident,options={}){
  await flush();const a=await api('/api/asset/'+ident);state.asset=a;state.pan=options.pan||[0,0];
  $('empty').hidden=true;$('detail').hidden=false;$('asset-kicker').textContent=a.fighter?'PILOT / '+a.fighter.toUpperCase():a.browse_categories[0].toUpperCase();
  $('asset-title').textContent=a.label;$('asset-meta').textContent=a.width+' × '+a.height+' source · '+a.candidates.length+' candidate revisions';
  $('source-size').textContent=a.width+' × '+a.height+' · original pixels';
  $('original-link').href=a.original;$('faithful-link').href=a.faithful;
  const reviewSelect=$('review-target');reviewSelect.replaceChildren(new Option('Texture / original','asset'));
  const parent=$('import-parent');parent.replaceChildren(new Option('Original / faithful baseline',''));
  for(const c of a.candidates){reviewSelect.add(new Option(c.label,c.id));parent.add(new Option(c.label,c.id));}
  for(const style of ['faithful','remaster']){const select=$('candidate-'+style),items=a.candidates.filter(c=>c.style===style);
    select.replaceChildren(new Option(items.length?'Choose revision':'No candidate imported',''));
    for(const c of [...items].reverse())select.add(new Option(c.label+(c.review.selected?' · selected':''),c.id));
    const wanted=options.lanes?.[style]||state.lanes[style];state.lanes[style]=items.some(c=>c.id===wanted)?wanted:(items.at(-1)?.id||'');select.value=state.lanes[style];
  }
  $('source-info').textContent='Original source ID: '+a.id+'\nDecoded ID: '+(a.decoded_id||'unavailable')+'\n\n'+
    a.aliases.map(r=>r.source+' [slot '+r.index+', '+r.name+']').join('\n')+'\n\n'+
    a.candidates.map(c=>c.label+' · '+c.style+' · '+c.width+'×'+c.height+'\nRevision '+c.id+'\nSHA-256 '+c.sha256+'\nParent '+(c.parent||'original/baseline')+'\n'+
      (c.assembly?'Assembly: raw '+c.assembly.raw_size.join('×')+' → '+c.width+'×'+c.height+'; baseline alpha '+(c.assembly.preserve_alpha?'restored':'not restored')+'; '+c.assembly.protected_regions.length+' protected region(s) copied exactly.\n'+
        (c.assembly.edited_regions?.length?'Regional revision: '+c.assembly.edited_regions.length+' edit box(es); remaining pixels retained from parent, with the explicit baseline alpha/protection above.\nParent SHA-256 '+c.assembly.parent_sha256+'\n':'')+'Raw SHA-256 '+c.assembly.raw_sha256+'\n':'')+c.prompt).join('\n\n');
  setReview(options.target||'asset');await loadImages();
  document.querySelectorAll('.asset-card').forEach(b=>b.classList.toggle('active',b.dataset.asset===ident));
}
async function loadImages(){
  const version=++state.imageToken,channel=$('channel').value,a=state.asset;
  const candidateA=currentCandidate('faithful'),candidateB=currentCandidate('remaster');
  const paths=[a.original,a.faithful,candidateA?.image,candidateB?.image];
  $('missing-a').hidden=!!candidateA;$('missing-b').hidden=!!candidateB;
  for(const [id,c]of [['a',candidateA],['b',candidateB]]){const link=$('candidate-link-'+id);link.hidden=!c;if(c)link.href=c.image;}
  const loaded=await Promise.all(paths.map(path=>path?new Promise(resolve=>{const im=new Image();im.onload=()=>resolve(im);
    im.onerror=()=>{message('A texture preview failed to load. The saved review is intact.',true);resolve(null);};im.src=path+'?channel='+channel;}):null));
  if(version!==state.imageToken)return;state.images=loaded;draw();saveSession();
}
function transform(canvas){
  const w=canvas.clientWidth,h=canvas.clientHeight,sourceW=state.asset.width,sourceH=state.asset.height;
  const fit=Math.min(...canvases.map(c=>Math.min(c.clientWidth/sourceW,c.clientHeight/sourceH)));
  const scale=$('zoom').value==='fit'?fit*.96:Number($('zoom').value)*4;
  return {w,h,x:(w-sourceW*scale)/2+state.pan[0],y:(h-sourceH*scale)/2+state.pan[1],rw:sourceW*scale,rh:sourceH*scale};
}
function draw(){if(!state.asset)return;
  canvases.forEach((canvas,index)=>{const t=transform(canvas),dpr=devicePixelRatio||1;canvas.width=Math.round(t.w*dpr);canvas.height=Math.round(t.h*dpr);
    const ctx=canvas.getContext('2d');ctx.setTransform(dpr,0,0,dpr,0,0);
    const bg=$('background').value;ctx.fillStyle=bg==='light'?'#e8e8dd':'#151813';ctx.fillRect(0,0,t.w,t.h);
    if(bg==='checker'){for(let y=0;y<t.h;y+=16)for(let x=0;x<t.w;x+=16){ctx.fillStyle=((x+y)/16)%2?'#282d25':'#1e231c';ctx.fillRect(x,y,16,16);}}
    const im=state.blink?state.images[0]:state.images[index];
    if(im){ctx.imageSmoothingEnabled=index!==0;ctx.drawImage(im,t.x,t.y,t.rw,t.rh);}
    for(const [n,region]of (state.review?.regions||[]).entries()){
      const [x,y,w,h]=region.rect;ctx.strokeStyle=region.kind==='protect'?'#cce58a':region.kind==='reference'?'#99c6f0':'#efb67d';ctx.lineWidth=1.5;
      ctx.strokeRect(t.x+x*t.rw,t.y+y*t.rh,w*t.rw,h*t.rh);ctx.fillStyle=ctx.strokeStyle;
      ctx.fillRect(t.x+x*t.rw,t.y+y*t.rh,19,18);ctx.fillStyle='#141813';ctx.font='11px system-ui';ctx.fillText(String(n+1),t.x+x*t.rw+5,t.y+y*t.rh+13);
    }
    if(state.pendingRegion){const [x,y,w,h]=state.pendingRegion;ctx.strokeStyle='#e0f4a4';ctx.setLineDash([5,3]);ctx.strokeRect(t.x+x*t.rw,t.y+y*t.rh,w*t.rw,h*t.rh);ctx.setLineDash([]);}
    canvas.style.cursor=state.marking?'crosshair':'grab';
  });
}
function point(canvas,event){const b=canvas.getBoundingClientRect(),t=transform(canvas);return [Math.max(0,Math.min(1,(event.clientX-b.left-t.x)/t.rw)),Math.max(0,Math.min(1,(event.clientY-b.top-t.y)/t.rh))];}
for(const canvas of canvases){let drag=null;
  canvas.addEventListener('pointerdown',event=>{if(!state.asset)return;canvas.setPointerCapture(event.pointerId);
    drag={start:point(canvas,event),last:[event.clientX,event.clientY],mark:state.marking};});
  canvas.addEventListener('pointermove',event=>{if(!drag)return;
    if(drag.mark){const p=point(canvas,event);state.pendingRegion=[Math.min(p[0],drag.start[0]),Math.min(p[1],drag.start[1]),Math.abs(p[0]-drag.start[0]),Math.abs(p[1]-drag.start[1])];}
    else{state.pan[0]+=event.clientX-drag.last[0];state.pan[1]+=event.clientY-drag.last[1];drag.last=[event.clientX,event.clientY];}draw();});
  canvas.addEventListener('pointerup',()=>{if(!drag)return;const marked=drag.mark;drag=null;
    if(marked&&state.pendingRegion&&state.pendingRegion[2]>.003&&state.pendingRegion[3]>.003){$('region-note').value='';$('region-dialog').returnValue='';$('region-dialog').showModal();}
    else state.pendingRegion=null;draw();saveSession();});
  canvas.addEventListener('pointercancel',()=>{drag=null;state.pendingRegion=null;draw();});
}
$('region-dialog').addEventListener('close',()=>{if($('region-dialog').returnValue==='save'&&state.pendingRegion){
  state.review.regions.push({id:crypto.randomUUID(),rect:state.pendingRegion,note:$('region-note').value.trim(),kind:$('region-kind').value});changed();renderRegions();}
  state.pendingRegion=null;state.marking=false;$('mark-region').setAttribute('aria-pressed','false');draw();});
$('mark-region').onclick=()=>{state.marking=!state.marking;$('mark-region').setAttribute('aria-pressed',String(state.marking));draw();};
$('reset-view').onclick=()=>{state.pan=[0,0];$('zoom').value='fit';draw();saveSession();};
for(const id of ['zoom','background'])$(id).onchange=()=>{draw();saveSession();};
$('channel').onchange=()=>loadImages().catch(e=>message(e.message,true));
function stopBlink(){state.blink=false;draw();}
$('blink').onpointerdown=()=>{state.blink=true;draw();};$('blink').onpointerup=$('blink').onpointerleave=stopBlink;
$('blink').onkeydown=e=>{if(e.code==='Space'){state.blink=true;draw();}};$('blink').onkeyup=stopBlink;
for(const id of ['notes','tags'])$(id).oninput=changed;
for(const id of ['flag','verdict','face-reviewed','channels-reviewed','game-verified','selected','mip-policy'])$(id).onchange=()=>{
  if(id!=='selected'&&($('verdict').value!=='approved'||!$('face-reviewed').checked||!$('channels-reviewed').checked))$('selected').checked=false;
  changed();};
$('review-target').onchange=()=>exclusive(async()=>{const wanted=$('review-target').value;try{await flush();setReview(wanted);}catch{$('review-target').value=state.target;}});
document.querySelectorAll('.review-pane').forEach(button=>button.onclick=()=>exclusive(async()=>{try{await flush();const target=button.dataset.target||state.lanes[button.dataset.lane];
  if(!target){message('Import a candidate in this direction before reviewing it.');return;}setReview(target);$('notes').focus();}catch(e){message(e.message,true);}}));
for(const style of ['faithful','remaster'])$('candidate-'+style).onchange=()=>{state.lanes[style]=$('candidate-'+style).value;loadImages().catch(e=>message(e.message,true));};
$('asset-flag').onclick=()=>exclusive(async()=>{try{await flush();const review=structuredClone(state.asset.review);review.flag=!review.flag;
  state.asset.review=await api('/api/review/'+state.asset.id+'/asset',review);if(state.target==='asset')setReview('asset');
  $('asset-flag').setAttribute('aria-pressed',String(state.asset.review.flag));await refreshCatalog();}catch(e){message(e.message,true);}});
$('restore-draft').onclick=()=>exclusive(async()=>{const draft=getDraft();if(!draft)return;
  const fresh=await api('/api/asset/'+state.asset.id),target=state.target;
  const current=target==='asset'?fresh.review:fresh.candidates.find(c=>c.id===target)?.review;
  if(!current)return;state.review={...draft,version:current.version};
  const restored=structuredClone(state.review);if(target==='asset')state.asset.review=restored;else state.asset.candidates.find(c=>c.id===target).review=restored;
  setReview(target);state.dirty=true;rememberDraft();await flush();
}).catch(e=>message(e.message,true));
$('discard-draft').onclick=()=>{localStorage.removeItem(draftKey());$('draft-recovery').hidden=true;};
for(const id of ['scope','fighter','category','review-filter'])$(id).onchange=async()=>{try{await flush();state.page=0;await refreshCatalog();}catch(e){message(e.message,true);}};
$('search').oninput=()=>{clearTimeout(searchTimer);searchTimer=setTimeout(()=>{state.page=0;refreshCatalog().catch(e=>message(e.message,true));},220);};
$('prev-page').onclick=()=>{state.page--;refreshCatalog().catch(e=>message(e.message,true));};
$('next-page').onclick=()=>{state.page++;refreshCatalog().catch(e=>message(e.message,true));};
function download(data,filename){const url=URL.createObjectURL(new Blob([JSON.stringify(data,null,2)],{type:'application/json'}));const a=document.createElement('a');a.href=url;a.download=filename;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}
$('download-review').onclick=()=>exclusive(async()=>{try{await flush();download(await api('/api/export-review'),'defjam-texture-review.json');}catch(e){message(e.message,true);}});
$('export-pack').onclick=()=>exclusive(async()=>{try{await flush();const result=await api('/api/export-pack',{});message('Exported '+result.assets+' selected textures. Test pack saved at:\n'+result.path+'\nIt has not been installed.');}catch(e){message(e.message,true);}});
function briefText(){let text=state.asset.briefs[$('brief-style').value];const parent=state.asset.candidates.find(c=>c.id===state.target);
  if(parent)text=text.replace('Input: original texture atlas as edit target; faithful HD as comparison.',
    'Input: selected candidate revision '+parent.id+' as edit target; original atlas and faithful HD as references.\nParent SHA-256: '+parent.sha256);
  return text+(state.review.regions.length?'\nRegional notes:\n'+state.review.regions.map((r,i)=>(i+1)+'. '+r.kind+': '+r.note+' '+JSON.stringify(r.rect)).join('\n'):'')+'\nRequested revision: '+($('brief-note').value||state.review.notes);}
function updateBrief(){$('brief-preview').textContent=briefText();}
$('prepare-brief').onclick=()=>exclusive(async()=>{try{await flush();$('brief-note').value=state.review.notes;const c=state.asset.candidates.find(c=>c.id===state.target);
  $('brief-style').value=c?.style||'faithful';updateBrief();$('brief-dialog').showModal();}catch(e){message(e.message,true);}});
$('brief-note').oninput=$('brief-style').onchange=updateBrief;
$('copy-brief').onclick=()=>navigator.clipboard.writeText(briefText()).then(()=>{$('copy-brief').textContent='Copied';setTimeout(()=>$('copy-brief').textContent='Copy brief',1500);}).catch(e=>message(e.message,true));
$('close-brief').onclick=()=>$('brief-dialog').close();
$('queue-brief').onclick=async()=>{try{const request=await api('/api/request',{asset:state.asset.id,revision:state.target,style:$('brief-style').value,note:$('brief-note').value});
  state.config.queued++;$('queue-count').textContent=state.config.queued;$('brief-dialog').close();message('Saved '+request.label+' to the Codex queue. The request is ready for image generation in chat.');}catch(e){message(e.message,true);}};
$('open-import').onclick=()=>exclusive(async()=>{try{await flush();$('import-form').reset();$('import-error').hidden=true;
  const c=state.asset.candidates.find(c=>c.id===state.target);$('import-parent').value=c?.id||'';$('import-style').value=c?.style||'faithful';$('import-dialog').showModal();}catch(e){message(e.message,true);}});
$('close-import').onclick=()=>$('import-dialog').close();
$('import-form').onsubmit=event=>{event.preventDefault();return exclusive(async()=>{const file=$('import-file').files[0];if(!file)return;
  const job={asset:state.asset.id,label:$('import-label').value,style:$('import-style').value,parent:$('import-parent').value,prompt:$('import-prompt').value};
  $('submit-import').disabled=true;try{if(file.size>24*1024*1024)throw Error('Choose a PNG smaller than 24 MiB.');
    const encoded=await new Promise((resolve,reject)=>{const reader=new FileReader();reader.onload=()=>resolve(reader.result.split(',')[1]);reader.onerror=()=>reject(Error('Unable to read PNG'));reader.readAsDataURL(file);});
    const c=await api('/api/import',{...job,image:encoded});
    $('import-dialog').close();state.lanes[job.style]=c.id;await loadAsset(job.asset,{target:c.id,lanes:state.lanes});await refreshCatalog();message('Imported a new revision. Earlier candidates and review notes are preserved.');
  }catch(e){$('import-error').textContent=e.message;$('import-error').hidden=false;}finally{$('submit-import').disabled=false;}});};
let queuedRequests=[];
$('show-queue').onclick=()=>exclusive(async()=>{try{await flush();const data=await api('/api/export-review');queuedRequests=data.requests;const list=$('queue-items');list.replaceChildren();
  if(!queuedRequests.length){const p=document.createElement('p');p.textContent='No requests yet. Choose a texture and prepare an imagegen brief.';list.append(p);}
  for(const q of queuedRequests){const row=document.createElement('div');row.className='queue-item';const title=document.createElement('strong'),meta=document.createElement('p'),pre=document.createElement('pre');
    title.textContent=q.label;meta.textContent=state.config.styles[q.style]+' · '+q.status+' · '+new Date(q.created).toLocaleString()+(q.error?' · '+q.error:'');pre.textContent=q.prompt;row.append(title,meta,pre);list.append(row);}
  $('queue-dialog').showModal();}catch(e){message(e.message,true);}});
$('close-queue').onclick=()=>$('queue-dialog').close();$('download-queue').onclick=()=>download(queuedRequests,'defjam-imagegen-queue.json');
window.addEventListener('beforeunload',event=>{
  if(state.config&&state.asset){clearTimeout(sessionTimer);fetch('/api/session',{method:'POST',headers:{'Content-Type':'application/json','X-Workshop-Token':state.config.token},body:JSON.stringify(captureSession()),keepalive:true}).catch(()=>{});}
  if(state.dirty&&state.asset){rememberDraft();
  fetch('/api/review/'+state.asset.id+'/'+state.target,{method:'POST',headers:{'Content-Type':'application/json','X-Workshop-Token':state.config.token},body:JSON.stringify(state.review),keepalive:true}).catch(()=>{});
  event.preventDefault();event.returnValue='';}
});
window.addEventListener('resize',()=>{if(state.asset)draw();});
(async()=>{try{
  state.config=await api('/api/config');$('workspace').textContent=state.config.workspace;$('queue-count').textContent=state.config.queued;
  for(const category of state.config.categories)$('category').add(new Option(category,category));
  const s=state.config.session;for(const [id,key]of [['scope','scope'],['fighter','fighter'],['category','category'],['review-filter','status'],['search','q'],['zoom','zoom'],['channel','channel'],['background','background']]){
    if(s[key]!==undefined)$(id).value=s[key];}
  state.page=Number(s.page)||0;state.lanes=s.lanes||{faithful:'',remaster:''};
  const result=await refreshCatalog();if(s.asset){try{await openAsset(s.asset,{target:s.target,pan:s.pan,lanes:s.lanes});}catch{if(result.assets[0])await openAsset(result.assets[0].id);}}
  else if(result.assets[0])await openAsset(result.assets[0].id);
  saveStatus('All changes saved');
}catch(e){saveStatus('Workshop unavailable',true);message(e.message,true);}})();
