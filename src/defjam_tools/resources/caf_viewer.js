import * as THREE from '/vendor/three.module.min.js';
import {OrbitControls} from '/vendor/controls/OrbitControls.js';

const $=id=>document.getElementById(id);
const state={catalog:null,stored:null,outfit:null,slot:null,asset:null,compare:null,views:[],scene:null,
  syncing:false,generation:0,hold:false,showA:false,write:Promise.resolve(),queueEntry:null,noteDirty:false,noteEdit:0};
let renderTimer,saveTimer;
const draftKey=()=>`defjam-caf-notes:${state.catalog?.corpus_id}:${state.queueEntry?.id}`;
function error(e){$('error').textContent=e.message||String(e);$('error').hidden=false;}
function clearError(){$('error').hidden=true;}
async function api(path,body){
  const r=await fetch(path,body===undefined?{}:{method:'POST',headers:{'Content-Type':'application/json','X-Workshop-Token':state.catalog.token},body:JSON.stringify(body)});
  const data=await r.json();if(!r.ok)throw Error(data.error||'CAF request failed');return data;
}
function save(action,body){
  body=structuredClone(body);
  const task=state.write.then(async()=>{
    $('save-status').textContent='Saving…';
    state.stored=await api('/api/caf/state',{action,version:state.stored.version,...body});
    $('save-status').textContent='Saved on this computer';renderOutfits();renderQueue();return state.stored;
  });
  state.write=task.catch(e=>{$('save-status').textContent='Not saved';error(e);});return task;
}
function cameraState(){const v=state.views[0];return {position:v.camera.position.toArray(),target:v.controls.target.toArray()};}
function remember(){
  clearTimeout(saveTimer);saveTimer=setTimeout(()=>save('session',{session:{outfit:state.outfit,camera:cameraState(),
    compare:state.compare,lighting:$('lighting').value,mode:$('mode').value,focus:state.slot}}).catch(()=>{}),600);
}
function groupFor(slot){return state.catalog.groups.find(g=>g.id===slot);}
function itemFor(slot){const selected=state.outfit.slots[slot];return selected&&groupFor(slot).items.find(i=>i.id===selected.item);}
function resourceFor(slot){
  const selected=state.outfit.slots[slot],item=itemFor(slot);if(!item?.styles.length)return null;
  const name=item.styles[selected.style].variants[selected.color];return state.catalog.resources[name.toLowerCase()];
}
function primaryAsset(item){
  const name=item.styles[0]?.variants[0];return name&&state.catalog.resources[name.toLowerCase()]?.records[0]?.asset;
}
function itemName(item){
  const name=item.model==='NON_GEOM'?(item.styles[0]?.variants[0]||item.model):item.model;
  const m=name.match(/^V2CP_(\d+)_(\d+)_/);return m?`${m[1]} / ${m[2]}`:name.replace('V2CP_','');
}
function imageURL(asset,revision){return `/api/caf/image/${encodeURIComponent(asset)}/${encodeURIComponent(revision)}`;}
function revisionLabel(asset,revision){return state.catalog.revisions[asset]?.find(r=>r.id===revision)?.label||revision;}
function renderOutfits(){
  const select=$('saved-outfit'),value=select.value;select.replaceChildren(new Option('Choose an outfit…',''));
  for(const name of Object.keys(state.stored.outfits))select.add(new Option(name,name));select.value=value;
}
function renderEquipped(){
  const container=$('equipped');container.replaceChildren();
  for(const slot of Object.keys(state.outfit.slots).sort((a,b)=>Number(a)-Number(b))){
    const item=itemFor(slot),button=document.createElement('button'),name=document.createElement('strong'),detail=document.createElement('span');
    name.textContent=groupFor(slot).label;detail.textContent=itemName(item);button.append(name,detail);
    button.onclick=()=>focusSlot(slot);container.append(button);
  }
}
function renderCategories(){
  const host=$('categories'),query=$('search').value.trim().toLowerCase();
  const opened=new Set([...host.querySelectorAll('details[open]')].map(x=>x.dataset.slot));host.replaceChildren();
  for(const section of ['Clothing','Hair & grooming','Jewelry','Tattoos','Body & face']){
    const groups=state.catalog.groups.filter(g=>g.section===section && !['Template','Palette','BlendShape'].includes(g.kind));
    const heading=document.createElement('h3');heading.className='category-section';heading.textContent=section;host.append(heading);
    for(const group of groups){
      const items=group.items.filter(item=>{
        if(!query)return true;
        const names=item.styles.flatMap(s=>s.variants);const ids=names.flatMap(n=>state.catalog.resources[n.toLowerCase()]?.records.map(r=>r.asset)||[]);
        return [group.label,item.model,...names,...ids].join(' ').toLowerCase().includes(query);
      });
      if(!items.length)continue;
      const details=document.createElement('details'),summary=document.createElement('summary'),list=document.createElement('div');
      details.className='category';details.dataset.slot=group.id;summary.textContent=`${group.label} · ${items.length}`;list.className='item-list';
      let shown=0;
      function addPage(){
        list.querySelector('.more')?.remove();
        for(const item of items.slice(shown,shown+30)){
          const button=document.createElement('button'),text=document.createElement('div'),title=document.createElement('strong'),meta=document.createElement('small');
          button.className='item-card';button.classList.toggle('active',state.outfit.slots[group.id]?.item===item.id);button.dataset.item=item.id;
          const asset=primaryAsset(item);
          if(asset){const img=document.createElement('img');img.src=imageURL(asset,'original');img.loading='lazy';img.alt='';button.append(img);}
          title.textContent=itemName(item);meta.textContent=item.styles.length?`${item.styles.length} designs · ${item.styles.reduce((n,s)=>n+s.variants.length,0)} resources`:'Original body geometry';
          text.append(title,meta);button.append(text);button.title=item.model==='NON_GEOM'?(item.styles[0]?.variants[0]||item.model):item.model;
          button.disabled=Boolean(item.limitation);if(item.limitation)meta.textContent=item.limitation;
          button.onclick=()=>equip(group.id,item.id);list.append(button);
        }
        shown+=30;
        if(shown<items.length){const more=document.createElement('button');more.className='more';more.textContent=`Show more (${items.length-shown})`;more.onclick=addPage;list.append(more);}
      }
      details.addEventListener('toggle',()=>{if(details.open&&!shown)addPage();});details.append(summary,list);host.append(details);
      details.open=Boolean(query)||opened.has(group.id)||state.slot===group.id;
    }
  }
}
function equip(slot,id){
  const current=state.outfit.slots[slot];
  if(!current||current.item!==id)state.outfit.slots[slot]={item:id,style:0,color:0,palette:'default'};
  focusSlot(slot);renderCategories();renderEquipped();scheduleRender();
}
function focusSlot(slot,preferredAsset=null,preferredRevision=null){
  state.slot=slot;state.asset=null;state.compare=null;
  const item=itemFor(slot),selected=state.outfit.slots[slot],group=groupFor(slot);
  if(!item){$('item-controls').hidden=true;return;}
  $('item-title').textContent=group.label+' · '+itemName(item);$('item-resource').textContent=item.model==='NON_GEOM'?'Skin decal · '+(item.styles[0]?.variants[0]||''):item.model;
  $('item-controls').hidden=false;
  $('style').replaceChildren();
  for(const [i,style] of item.styles.entries()){
    const name=style.variants[0].replace(/^V2CP_\d+_\d+_/,'');$('style').add(new Option(`Design ${i+1} · ${name}`,String(i)));
  }
  $('style').disabled=!item.styles.length;$('style').value=String(selected.style);
  $('color').replaceChildren();const style=item.styles[selected.style];
  for(const [i,name] of (style?.variants||[]).entries())$('color').add(new Option(`Color ${i+1} · ${name.split('_').slice(-2).join('_')}`,String(i)));
  $('color').disabled=!style;$('color').value=String(selected.color);
  const resource=resourceFor(slot);
  $('palette').replaceChildren(new Option('Authored RGB / default source palette','default'));
  for(const p of resource?.palettes||[])$('palette').add(new Option(p,p));$('palette').value=selected.palette;
  $('palette').disabled=!resource?.palettes.length;
  const texture=$('texture');texture.replaceChildren();
  for(const record of resource?.records||[]){
    if(!record.asset)continue;
    const label=`${record.name} · ${record.width}×${record.height}`+(record.placement?'':' · auxiliary map');texture.add(new Option(label,record.asset));
  }
  texture.disabled=!texture.options.length;
  if(preferredAsset&&[...texture.options].some(o=>o.value===preferredAsset))texture.value=preferredAsset;
  state.asset=texture.value||null;
  textureChanged(preferredRevision);renderEquipped();remember();
}
function textureChanged(preferredRevision=null){
  state.asset=$('texture').value||null;
  const choices=state.catalog.revisions[state.asset]||[];
  for(const id of ['revision-a','revision-b']){$(id).replaceChildren();for(const r of choices)$(id).add(new Option(r.label+(r.sha256?' · '+r.id.slice(-8):''),r.id));$(id).disabled=!choices.length;}
  if(choices.length){
    $('revision-a').value='original';$('revision-b').value=preferredRevision||state.outfit.revisions[state.asset]||'faithful';
    if(!$('revision-b').value)$('revision-b').value='original';
  }
  updateComparison();
  for(const id of ['send-inspection','apply-revision'])$(id).disabled=!state.asset;
}
function clearSelection(){
  state.slot=null;state.asset=null;state.compare=null;$('item-controls').hidden=true;
  $('item-title').textContent='Choose a part';$('item-resource').textContent='Select an item from the wardrobe.';
  for(const id of ['texture','revision-a','revision-b']){$(id).replaceChildren();$(id).disabled=true;}
  updateComparison();
}
function updateComparison(){
  state.compare=state.asset?{asset:state.asset,a:$('revision-a').value,b:$('revision-b').value}:null;
  $('comparison-label').textContent=state.asset?`${groupFor(state.slot).label} · ${itemName(itemFor(state.slot))} · map ${$('texture').selectedOptions[0]?.textContent}`:'Source body assembly';
  $('label-a').textContent=state.asset?revisionLabel(state.asset,$('revision-a').value):'Equipped textures';
  $('label-b').textContent=state.asset?revisionLabel(state.asset,$('revision-b').value):'Equipped textures';
  $('source-id').textContent=state.asset?`Source ${state.asset}`:'This body part uses the shared skin atlas.';
  for(const side of ['a','b']){
    const quick=$('quick-'+side);quick.replaceChildren(...[...$('revision-'+side).options].map(o=>new Option(o.text,o.value)));
    quick.disabled=!state.asset;quick.value=$('revision-'+side).value;
  }
  $('inspection-notes').hidden=!(state.queueEntry?.asset===state.asset&&state.queueEntry?.revision===$('revision-b').value);
  for(const side of ['a','b']){
    const image=$('thumb-'+side),link=$('image-'+side);link.hidden=!state.asset;
    if(state.asset){image.src=imageURL(state.asset,$('revision-'+side).value);link.href=image.src;}
    else image.removeAttribute('src');
  }
  scheduleRender();remember();
}
function scheduleRender(){state.generation++;$('viewports').classList.add('pending');clearTimeout(renderTimer);renderTimer=setTimeout(()=>renderScene().catch(error),130);}
function createViewport(side){
  const host=$('viewport-'+side),scene=new THREE.Scene();
  const renderer=new THREE.WebGLRenderer({antialias:true,alpha:true});renderer.setPixelRatio(Math.min(devicePixelRatio,2));
  renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.toneMapping=THREE.NoToneMapping;renderer.setClearColor(0,0);
  host.append(renderer.domElement);renderer.domElement.setAttribute('aria-label',side==='a'?'Version A fighter canvas':'Version B fighter canvas');
  const camera=new THREE.PerspectiveCamera(35,1,.01,1000);camera.position.set(0,11,47);
  const controls=new OrbitControls(camera,renderer.domElement);controls.target.set(0,11,0);controls.minDistance=.3;controls.maxDistance=250;controls.update();
  scene.add(new THREE.HemisphereLight(0xffffff,0x647358,2));
  const key=new THREE.DirectionalLight(0xffffff,2);key.position.set(-10,25,20);scene.add(key);
  const rim=new THREE.DirectionalLight(0xa7b8d4,1);rim.position.set(10,15,-20);scene.add(rim);
  scene.add(new THREE.GridHelper(36,18,0x5b684c,0x303e2c));
  const v={side,host,scene,renderer,camera,controls,root:null,textures:null};
  controls.addEventListener('change',()=>{
    if(state.syncing)return;state.syncing=true;
    for(const other of state.views)if(other!==v){other.camera.position.copy(camera.position);other.controls.target.copy(controls.target);other.controls.update();}
    state.syncing=false;paint();remember();
  });
  new ResizeObserver(()=>{
    const w=host.clientWidth,h=host.clientHeight;if(!w||!h)return;
    renderer.setSize(w,h,false);camera.aspect=w/h;camera.updateProjectionMatrix();paint();
  }).observe(host);
  renderer.domElement.addEventListener('webglcontextlost',e=>{e.preventDefault();error(Error('3D context lost. Save inspection notes, then reload this viewer.'));});
  return v;
}
function disposeRoot(v){
  if(v.root){v.scene.remove(v.root);v.root.traverse(o=>{if(o.isMesh){o.geometry.dispose();o.material.dispose();}});}
  if(v.textures)for(const t of Object.values(v.textures))t.dispose();
}
function material(texture,mesh){
  const options={map:texture,transparent:mesh.transparent,side:THREE.FrontSide,wireframe:$('wireframe').checked};
  return $('lighting').value==='unlit'?new THREE.MeshBasicMaterial(options):new THREE.MeshStandardMaterial({...options,roughness:.85,metalness:0});
}
function paint(){
  const baseline=state.hold||state.showA;
  for(const v of state.views){
    if(v.root)v.root.traverse(o=>{if(o.isMesh){
      o.visible=!$('isolate').checked||o.userData.slot===state.slot;
      o.material.map=v.textures[(v.side==='b'&&baseline?'a':v.side)+o.userData.atlas];o.material.wireframe=$('wireframe').checked;
    }});
    if(v.host.clientWidth&&v.host.clientHeight)v.renderer.render(v.scene,v.camera);
  }
  if(state.asset)$('label-b').textContent=revisionLabel(state.asset,$(baseline?'revision-a':'revision-b').value);
  $('toggle').textContent=baseline?'Showing A':'Showing B';$('toggle').setAttribute('aria-pressed',String(baseline));$('hold').setAttribute('aria-pressed',String(state.hold));
}
async function renderScene(){
  const generation=++state.generation;$('render-status').textContent='Composing source atlases…';clearError();
  $('viewports').classList.add('pending');
  try{
  const result=await api('/api/caf/scene',{outfit:state.outfit,compare:state.compare,scale:4});
  if(generation!==state.generation)return;
  const textures={},loader=new THREE.TextureLoader();
  await Promise.all(['a','b'].flatMap(side=>Object.entries(result.textures[side]).map(async([atlas,url])=>{
    const texture=await loader.loadAsync(url);texture.flipY=false;texture.colorSpace=THREE.SRGBColorSpace;
    texture.wrapS=texture.wrapT=THREE.ClampToEdgeWrapping;texture.anisotropy=4;textures[side+atlas]=texture;
  })));
  if(generation!==state.generation){Object.values(textures).forEach(t=>t.dispose());return;}
  const first=!state.scene;state.scene=result;
  for(const v of state.views){
    disposeRoot(v);v.root=new THREE.Group();
    // Each view owns textures so disposal on a later render cannot invalidate its partner.
    v.textures=Object.fromEntries(Object.entries(textures).map(([name,t])=>[name,t.clone()]));
    for(const mesh of result.meshes){
      const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(mesh.positions.flat(),3));
      g.setAttribute('normal',new THREE.Float32BufferAttribute(mesh.normals.flat(),3));g.setAttribute('uv',new THREE.Float32BufferAttribute(mesh.uv.flat(),2));g.setIndex(mesh.indices);
      const o=new THREE.Mesh(g,material(v.textures[v.side+mesh.atlas],mesh));o.userData={slot:mesh.slot,atlas:mesh.atlas,group:mesh.group};v.root.add(o);
    }
    v.scene.add(v.root);
  }
  Object.values(textures).forEach(t=>t.dispose());
  $('render-status').textContent=`${result.vertices.toLocaleString()} vertices · ${result.triangles.toLocaleString()} triangles · source build ${state.outfit.build}`;
  $('scene-notices').textContent=result.notices.join('\n');
  if(state.compare&&!result.compared_on_model)error(Error('This texture is not currently mapped onto the equipped geometry. Choose its matching item/color resource.'));
  $('viewports').classList.remove('pending','stale');
  if(state.pendingPreset){const kind=state.pendingPreset;state.pendingPreset=null;preset(kind);}
  else if(first&&!state.restoredCamera)preset('fit');paint();remember();
  }catch(e){if(generation===state.generation){error(e);$('render-status').textContent='Selected outfit could not be rendered · previous image dimmed';$('viewports').classList.add('stale');}}
  finally{if(generation===state.generation)$('viewports').classList.remove('pending');}
}
function preset(kind){
  if(!state.scene||$('viewports').classList.contains('pending')){state.pendingPreset=kind;return;}
  let box=state.scene.bounds;
  if(kind==='focus'&&state.slot){
    let points=state.scene.meshes.filter(m=>m.slot===state.slot).flatMap(m=>m.positions);
    if(!points.length){
      const placement=resourceFor(state.slot)?.records.find(r=>r.asset===state.asset)?.placement;
      const record=resourceFor(state.slot)?.records.find(r=>r.asset===state.asset);
      if(placement&&record){
        const [x,y]=placement.origin;
        points=state.scene.meshes.filter(m=>m.atlas===placement.atlas).flatMap(m=>m.positions.filter((p,i)=>{
          const [u,v]=m.uv[i];return u>=x/256&&u<=(x+record.width)/256&&v>=y/256&&v<=(y+record.height)/256;
        }));
      }
    }
    if(points.length)box=[0,1].map(side=>[0,1,2].map(axis=>(side?Math.max:Math.min)(...points.map(p=>p[axis]))));
  }
  const min=box[0],max=box[1],height=max[1]-min[1],width=max[0]-min[0];
  const center=new THREE.Vector3(...min.map((n,i)=>(n+max[i])/2)),direction=new THREE.Vector3(0,0,kind==='back'?-1:1);
  let h=height,w=width;
  const detail={face:[.92,.22,.22],chest:[.73,.31,.5],pants:[.31,.56,.4],shoes:[.065,.2,.35]}[kind];
  if(detail){const full=state.scene.bounds,H=full[1][1]-full[0][1];center.set(0,full[0][1]+H*detail[0],0);h=H*detail[1];w=H*detail[2];if(kind==='shoes')direction.set(0,.22,1).normalize();}
  const aspect=Math.min(...state.views.filter(v=>v.host.clientWidth).map(v=>v.camera.aspect));
  const distance=Math.max(h,w/(aspect||1),max[2]-min[2])/(2*Math.tan(THREE.MathUtils.degToRad(35/2)))*1.18;
  state.syncing=true;for(const v of state.views){v.camera.position.copy(center).addScaledVector(direction,Math.max(distance,1));v.controls.target.copy(center);v.controls.update();}state.syncing=false;paint();remember();
}
function renderQueue(){
  $('queue-count').textContent=state.stored.queue.length;const host=$('queue-list');host.replaceChildren();
  if(!state.stored.queue.length){const p=document.createElement('p');p.className='hint';p.textContent='Send a texture revision here for closer model inspection. Items remain queued after reload.';host.append(p);}
  for(const entry of state.stored.queue){
    const b=document.createElement('button'),img=document.createElement('img'),text=document.createElement('div'),title=document.createElement('strong'),meta=document.createElement('small');
    b.className='item-card';img.src=imageURL(entry.asset,entry.revision);img.alt='';img.loading='lazy';title.textContent=revisionLabel(entry.asset,entry.revision);
    meta.textContent=`${entry.status.replace('_',' ')} · ${entry.asset.slice(0,12)}`;text.append(title,meta);b.append(img,text);b.onclick=()=>openInspection(entry).catch(error);host.append(b);
  }
}
function locateAsset(asset){
  const matches=[];
  for(const group of state.catalog.groups)for(const item of group.items)for(const [styleIndex,style] of item.styles.entries())for(const [colorIndex,name] of style.variants.entries()){
    if(state.catalog.resources[name.toLowerCase()]?.records.some(r=>r.asset===asset))matches.push({slot:group.id,item:item.id,style:styleIndex,color:colorIndex,palette:'default'});
  }
  // Keep the current equipped use when a source has several explicit aliases.
  return matches.find(m=>state.outfit.slots[m.slot]?.item===m.item)||matches[0];
}
async function flushNotes(){
  if(!state.noteDirty||!state.queueEntry)return;
  const id=state.queueEntry.id,notes=$('notes').value,status=$('inspection-status').value,key=draftKey(),edit=state.noteEdit;
  await save('inspection',{id,notes,status});
  state.queueEntry=state.stored.queue.find(e=>e.id===id);
  if(state.noteEdit===edit){state.noteDirty=false;localStorage.removeItem(key);}else await flushNotes();
}
async function openInspection(entry){
  await flushNotes();entry=state.stored.queue.find(e=>e.id===entry.id);
  if(!entry)throw Error('This inspection entry is no longer available. Refresh the queue.');
  const match=locateAsset(entry.asset);
  if(!match)throw Error('No explicit model/resource relationship for this source; it stays in the queue for atlas inspection.');
  state.outfit.slots[match.slot]={item:match.item,style:match.style,color:match.color,palette:'default'};
  focusSlot(match.slot,entry.asset,entry.revision);state.queueEntry=entry;
  $('inspection-notes').hidden=false;$('queued-revision').textContent=`${entry.revision} · SHA-256 ${entry.sha256}`;
  $('notes').value=entry.notes;$('inspection-status').value=entry.status;
  const draft=localStorage.getItem(draftKey());
  if(draft){const d=JSON.parse(draft);$('notes').value=d.notes;$('inspection-status').value=d.status;state.noteDirty=true;$('save-status').textContent='Recovered unsaved inspection draft';}
  renderEquipped();renderCategories();scheduleRender();
}
function setTab(queue){$('categories').hidden=queue;$('queue-list').hidden=!queue;$('search').hidden=queue;$('wardrobe-tab').setAttribute('aria-pressed',String(!queue));$('queue-tab').setAttribute('aria-pressed',String(queue));}
function noteChanged(){state.noteDirty=true;state.noteEdit++;try{localStorage.setItem(draftKey(),JSON.stringify({notes:$('notes').value,status:$('inspection-status').value}));}catch(e){error(Error('Browser draft storage unavailable. Save these inspection notes before leaving.'));}}

async function main(){
  state.catalog=await api('/api/caf/catalog');state.stored=state.catalog.state;
  state.outfit=structuredClone(state.stored.session.outfit||state.catalog.default);
  for(const build of state.catalog.builds)$('build').add(new Option(build.label,build.id));$('build').value=state.outfit.build;
  for(let i=1;i<=8;i++)$('skin').add(new Option(`Skin palette ${i}`,`pl0${i}`));$('skin').value=state.outfit.skin;
  for(const text of state.catalog.limitations){const li=document.createElement('li');li.textContent=text;$('limits').append(li);}
  state.views=['a','b'].map(createViewport);
  const saved=state.stored.session;
  if(saved.camera){state.syncing=true;for(const v of state.views){v.camera.position.fromArray(saved.camera.position);v.controls.target.fromArray(saved.camera.target);v.controls.update();}state.syncing=false;state.restoredCamera=true;}
  if(['unlit','studio'].includes(saved.lighting))$('lighting').value=saved.lighting;
  if(['single','split'].includes(saved.mode))$('mode').value=saved.mode;
  else if(document.documentElement.clientWidth<1120)$('mode').value='single';
  $('viewports').classList.toggle('single',$('mode').value==='single');
  renderCategories();renderEquipped();renderOutfits();renderQueue();
  if(saved.focus&&state.outfit.slots[saved.focus])focusSlot(saved.focus,saved.compare?.asset,saved.compare?.b);
  if(saved.compare&&state.compare&&saved.compare.asset===state.compare.asset){$('revision-a').value=saved.compare.a;updateComparison();}
  $('save-status').textContent='Production workshop is read-only';
  $('search').addEventListener('input',renderCategories);
  $('build').onchange=()=>{state.outfit.build=$('build').value;scheduleRender();remember();};
  $('skin').onchange=()=>{state.outfit.skin=$('skin').value;scheduleRender();remember();};
  $('style').onchange=()=>{const s=state.outfit.slots[state.slot];s.style=Number($('style').value);s.color=0;s.palette='default';focusSlot(state.slot);};
  $('color').onchange=()=>{const s=state.outfit.slots[state.slot];s.color=Number($('color').value);s.palette='default';focusSlot(state.slot);};
  $('palette').onchange=()=>{state.outfit.slots[state.slot].palette=$('palette').value;scheduleRender();remember();};
  $('texture').onchange=()=>textureChanged();
  for(const id of ['revision-a','revision-b'])$(id).onchange=updateComparison;
  for(const side of ['a','b'])$('quick-'+side).onchange=()=>{$('revision-'+side).value=$('quick-'+side).value;updateComparison();};
  $('apply-revision').onclick=()=>{if(state.asset)state.outfit.revisions[state.asset]=$('revision-b').value;remember();$('save-status').textContent='B kept on this outfit';};
  $('remove-item').onclick=()=>{delete state.outfit.slots[state.slot];clearSelection();renderEquipped();renderCategories();};
  $('reset-outfit').onclick=()=>{state.outfit=structuredClone(state.catalog.default);$('build').value=state.outfit.build;$('skin').value=state.outfit.skin;clearSelection();renderEquipped();renderCategories();};
  $('save-outfit').onclick=()=>save('outfit',{name:$('outfit-name').value.trim(),outfit:structuredClone(state.outfit)}).catch(error);
  $('saved-outfit').onchange=()=>{const o=state.stored.outfits[$('saved-outfit').value];if(!o)return;state.outfit=structuredClone(o);$('build').value=o.build;$('skin').value=o.skin;clearSelection();renderEquipped();renderCategories();};
  $('lighting').onchange=()=>{for(const v of state.views)if(v.root)v.root.traverse(o=>{if(o.isMesh){const previous=o.material;o.material=material(previous.map,{transparent:previous.transparent});previous.dispose();}});paint();remember();};
  for(const id of ['wireframe','isolate'])$(id).onchange=paint;
  $('mode').onchange=()=>{$('viewports').classList.toggle('single',$('mode').value==='single');remember();};
  $('toggle').onclick=()=>{state.showA=!state.showA;paint();};
  const hold=value=>{state.hold=value;paint();};
  $('hold').addEventListener('pointerdown',e=>{e.preventDefault();$('hold').setPointerCapture(e.pointerId);hold(true);});
  for(const event of ['pointerup','pointercancel','lostpointercapture'])$('hold').addEventListener(event,()=>hold(false));
  $('hold').onkeydown=e=>{if(['Space','Enter'].includes(e.code)){e.preventDefault();hold(true);}};$('hold').onkeyup=()=>hold(false);
  window.addEventListener('blur',()=>hold(false));
  for(const b of document.querySelectorAll('[data-preset]'))b.onclick=()=>preset(b.dataset.preset);
  $('wardrobe-tab').onclick=()=>setTab(false);$('queue-tab').onclick=()=>setTab(true);
  $('send-inspection').onclick=async()=>{try{await save('queue',{asset:state.asset,revision:$('revision-b').value});setTab(true);await openInspection(state.stored.queue.find(e=>e.asset===state.asset&&e.revision===$('revision-b').value));}catch(e){error(e);}};
  $('notes').oninput=noteChanged;$('inspection-status').onchange=noteChanged;$('save-notes').onclick=()=>flushNotes().catch(error);
  $('refresh-revisions').onclick=async()=>{try{
    await flushNotes();await state.write;const a=$('revision-a').value,b=$('revision-b').value;
    const fresh=await api('/api/caf/catalog');state.catalog=fresh;state.stored=fresh.state;
    if(state.asset){textureChanged(b);$('revision-a').value=a;updateComparison();}
    renderQueue();renderOutfits();$('save-status').textContent='Texture revisions refreshed';
  }catch(e){error(e);}};
  $('download-state').onclick=()=>{const url=URL.createObjectURL(new Blob([JSON.stringify(state.stored,null,2)],{type:'application/json'})),a=document.createElement('a');a.href=url;a.download='caf-inspection-backup.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);};
  window.addEventListener('beforeunload',e=>{if(state.noteDirty){e.preventDefault();e.returnValue='';}});
  const params=new URLSearchParams(location.search),asset=params.get('asset'),revision=params.get('revision')||'original';
  if(asset){await save('queue',{asset,revision});setTab(true);await openInspection(state.stored.queue.find(e=>e.asset===asset&&e.revision===revision));}
  document.querySelector('main').inert=false;document.querySelector('main').setAttribute('aria-busy','false');
  clearTimeout(renderTimer);await renderScene();
}
main().catch(error);
