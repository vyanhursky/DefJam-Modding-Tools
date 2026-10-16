import * as THREE from '/vendor/three.module.min.js';
import {OrbitControls} from '/vendor/controls/OrbitControls.js';
import {GLTFLoader} from '/vendor/loaders/GLTFLoader.js';

const $=id=>document.getElementById(id);
const state={ready:false,dirty:false,busy:false,syncing:false,hold:false,textureCache:new Map(),views:[]};
let viewTimer;
function error(e){$('error').textContent=e?.message||String(e);$('error').hidden=false;
  if(!state.ready){document.querySelectorAll('select,button,input,textarea').forEach(el=>el.disabled=el.id!=='fighter');$('download').removeAttribute('href');}}
async function api(path,body){
  const response=await fetch(path,body===undefined?{}:{method:'POST',headers:{'Content-Type':'application/json','X-Workshop-Token':state.config.token},body:JSON.stringify(body)});
  const data=await response.json();if(!response.ok)throw Error(data.error||'Local workshop request failed');return data;
}
async function exclusive(action){
  if(state.busy)return;state.busy=true;
  const controls=[...document.querySelectorAll('select,button,input,textarea')];controls.forEach(e=>e.disabled=true);
  try{return await action();}finally{state.busy=false;document.querySelectorAll('select,button,input,textarea').forEach(e=>e.disabled=!state.ready&&e.id!=='fighter');}
}
function textureLabel(rev){return rev==='original'?'Original':rev==='faithful'?'Faithful HD · Lanczos 4×':state.asset.candidates.find(c=>c.id===rev)?.label||rev;}
function groupLabel(raw){const base=raw.split('~')[0].replace('_MatAlph','');return ({emc1_eye:'Eyes',emc2_skin:'Skin',emc3_jewelry:'Jewelry',emc4_cloth:'Clothing',emc3_jewelry_ALPHA:'Jewelry · transparent',eyelid_ALPHA:'Eyelids · transparent',nospec:'Unlit',nospec_ALPHA:'Unlit · transparent'})[base]||base;}
function revisionTarget(){return ['original','faithful'].includes($('right').value)?'asset':$('right').value;}
function draftKey(){return 'defjam-3d-draft:'+state.config.workspace+':'+state.asset.id+':'+revisionTarget();}
function viewState(){return {position:state.views[0].camera.position.toArray(),target:state.views[0].controls.target.toArray(),left:$('left').value,right:$('right').value,lighting:$('lighting').value,wireframe:$('wireframe').checked,groups:[...document.querySelectorAll('#groups input:checked')].map(i=>i.value)};}
function rememberView(){
  if(!state.ready)return;
  clearTimeout(viewTimer);$('save-state').textContent='Saving view…';
  const fighter=state.fighter,view=viewState();
  viewTimer=setTimeout(()=>api('/api/model-view',{fighter,view}).then(()=>{$('save-state').textContent='View saved on this computer';state.saved.views[fighter]=view;}).catch(error),500);
}
function updateView(){
  const shown=new Set([...document.querySelectorAll('#groups input:checked')].map(i=>i.value));
  for(const v of state.views)if(v.root)v.root.traverse(o=>{if(o.isMesh){o.visible=shown.has(o.userData.group);o.material.wireframe=$('wireframe').checked;}});
  rememberView();
}
function syncCamera(origin){
  if(state.syncing)return;state.syncing=true;
  for(const v of state.views)if(v!==origin){v.camera.position.copy(origin.camera.position);v.controls.target.copy(origin.controls.target);v.controls.update();}
  state.syncing=false;rememberView();
}
function createViewport(side){
  const host=$('viewport-'+side),scene=new THREE.Scene();
  const renderer=new THREE.WebGLRenderer({antialias:true,alpha:true});
  renderer.setPixelRatio(Math.min(devicePixelRatio,2));renderer.outputColorSpace=THREE.SRGBColorSpace;
  renderer.setClearColor(0,0);renderer.toneMapping=THREE.NoToneMapping;
  renderer.domElement.setAttribute('aria-label',side==='left'?'Left model canvas':'Right model canvas');
  host.append(renderer.domElement);
  const camera=new THREE.PerspectiveCamera(35,1,.01,1000);camera.position.set(0,11,45);
  const controls=new OrbitControls(camera,renderer.domElement);controls.target.set(0,11,0);controls.minDistance=.3;controls.maxDistance=300;controls.update();
  scene.add(new THREE.HemisphereLight(0xffffff,0x626963,2));
  const key=new THREE.DirectionalLight(0xffffff,2);key.position.set(-10,25,20);scene.add(key);
  const rim=new THREE.DirectionalLight(0x9db6cf,.8);rim.position.set(10,15,-20);scene.add(rim);
  const grid=new THREE.GridHelper(40,20,0x59624d,0x354035);grid.position.y=-.025;scene.add(grid);
  const v={side,host,scene,renderer,camera,controls,root:null,generation:0};
  controls.addEventListener('change',()=>syncCamera(v));
  renderer.domElement.addEventListener('webglcontextlost',()=>error(Error('3D graphics context lost. Reload this view after saving notes.')));
  new ResizeObserver(()=>{const w=host.clientWidth,h=host.clientHeight;renderer.setSize(w,h,false);camera.aspect=w/h;camera.updateProjectionMatrix();}).observe(host);
  return v;
}
function preset(kind){
  const box=state.model.bounds,min=box[0],max=box[1],height=max[1]-min[1],width=max[0]-min[0];
  const center=new THREE.Vector3((min[0]+max[0])/2,(min[1]+max[1])/2,(min[2]+max[2])/2);
  const v=state.views[0];let distance=Math.max(height,width/v.camera.aspect)/2/Math.tan(THREE.MathUtils.degToRad(v.camera.fov/2))*1.15;
  let sign=kind==='back'?-1:1;
  if(kind==='chest'){center.set(0,height*.71,1);distance=11;}
  if(kind==='belt'){center.set(0,height*.535,1);distance=8;}
  v.controls.target.copy(center);v.camera.position.copy(center).add(new THREE.Vector3(0,0,distance*sign));v.controls.update();syncCamera(v);
}
async function getTexture(revision){
  const key=state.asset.id+':'+revision;
  if(!state.textureCache.has(key)){
    const promise=new THREE.TextureLoader().loadAsync('/api/image/'+state.asset.id+'/'+revision).then(texture=>{
      texture.flipY=false;texture.colorSpace=THREE.SRGBColorSpace;texture.wrapS=texture.wrapT=THREE.ClampToEdgeWrapping;
      texture.anisotropy=Math.min(8,state.views[0].renderer.capabilities.getMaxAnisotropy());return texture;
    }).catch(e=>{state.textureCache.delete(key);throw e;});
    state.textureCache.set(key,promise);
  }
  return state.textureCache.get(key);
}
async function paint(v){
  if(!v.root)return;
  const token=++v.generation,revision=v.side==='right'&&state.hold?'original':$(v.side).value;
  const texture=await getTexture(revision);if(token!==v.generation)return;
  v.root.traverse(o=>{if(!o.isMesh)return;
    const parameters={map:texture,transparent:o.userData.alpha,depthWrite:!o.userData.alpha,side:THREE.FrontSide,wireframe:$('wireframe').checked};
    const material=$('lighting').value==='studio'?new THREE.MeshStandardMaterial({...parameters,metalness:0,roughness:.8}):new THREE.MeshBasicMaterial(parameters);
    o.material.dispose();o.material=material;
  });
  $('label-'+v.side).textContent=textureLabel(revision)+' · '+texture.image.width+' × '+texture.image.height;
  if(v.side==='right'){
    $('download').href='/api/model/'+state.fighter+'/model.glb?revision='+encodeURIComponent($('right').value);
    $('download').download=state.fighter+'-'+$('right').value+'.glb';
    $('export-state').textContent='Self-contained mesh, UVs, source normals, material groups and the selected right texture.';
  }
  rememberView();
}
function loadReview(){
  const target=revisionTarget(),candidate=state.asset.candidates.find(c=>c.id===target);
  state.review=structuredClone(candidate?candidate.review:state.asset.review);state.dirty=false;state.reviewRevision=$('right').value;
  $('notes').value=state.review.notes;$('flag').checked=state.review.flag;
  $('review-label').textContent=textureLabel($('right').value);
  $('review-status').textContent='Saved notes loaded';$('restore-draft').hidden=!localStorage.getItem(draftKey());
}
function reviewChanged(){state.dirty=true;$('review-status').textContent='Unsaved · browser draft retained';localStorage.setItem(draftKey(),JSON.stringify({notes:$('notes').value,flag:$('flag').checked}));}
async function saveNotes(){
  if(!state.dirty)return;
  const target=revisionTarget(),payload={...state.review,notes:$('notes').value,flag:$('flag').checked};
  $('save-notes').disabled=true;
  try{
    const saved=await api('/api/review/'+state.asset.id+'/'+target,payload);state.review=saved;
    if(target==='asset')state.asset.review=saved;else state.asset.candidates.find(c=>c.id===target).review=saved;
    if($('notes').value===payload.notes&&$('flag').checked===payload.flag){state.dirty=false;localStorage.removeItem(draftKey());$('restore-draft').hidden=true;$('review-status').textContent='Notes saved to gallery';}
  }finally{$('save-notes').disabled=false;}
}
async function chooseFighter(fighter){
  if(state.busy)return;state.busy=true;
  const previous=state.fighter,previousView=state.ready?viewState():null;state.ready=false;
  const controls=[...document.querySelectorAll('select,button,input,textarea')];controls.forEach(e=>e.disabled=true);
  try{
    await saveNotes();clearTimeout(viewTimer);
    if(previousView){await api('/api/model-view',{fighter:previous,view:previousView});state.saved.views[previous]=previousView;}
    state.fighter=fighter;
    state.model=state.models.find(m=>m.id===fighter);state.asset=await api('/api/asset/'+state.model.source_id);
    const rich=state.asset.candidates.filter(c=>c.style==='faithful'),history=state.asset.candidates.filter(c=>c.style!=='faithful');
    const choices=[['original','Original'],['faithful','Faithful HD · Lanczos 4×'],...[...rich].reverse().map(c=>[c.id,c.label]),...[...history].reverse().map(c=>[c.id,c.label+' · history'])];
    for(const side of ['left','right'])$(side).replaceChildren(...choices.map(([value,label])=>new Option(label,value)));
    const saved=state.saved.views[fighter];
    $('left').value=choices.some(([v])=>v===saved?.left)?saved.left:'original';
    $('right').value=choices.some(([v])=>v===saved?.right)?saved.right:(rich.at(-1)?.id||'faithful');
    $('lighting').value=saved?.lighting||'unlit';$('wireframe').checked=saved?.wireframe||false;
    $('groups').replaceChildren(...state.model.groups.map(group=>{const label=document.createElement('label'),input=document.createElement('input');input.type='checkbox';input.disabled=true;input.value=group;input.checked=saved?saved.groups.includes(group):true;input.addEventListener('change',updateView);label.title=group;label.append(input,' '+groupLabel(group));return label;}));
    const gltf=await new GLTFLoader().loadAsync('/api/model/'+fighter+'/model.glb');
    for(const v of state.views){
      if(v.root){v.scene.remove(v.root);v.root.traverse(o=>{if(o.isMesh){o.geometry.dispose();o.material.dispose();}});}
      v.root=gltf.scene.clone(true);
      v.root.traverse(o=>{if(o.isMesh){o.geometry=o.geometry.clone();o.material=o.material.clone();o.userData={...o.userData,group:o.userData.group||o.parent?.userData.group,alpha:o.material.transparent};}});
      v.scene.add(v.root);
    }
    // Loader resources are cloned per pane so later fighter switches are safe.
    gltf.scene.traverse(o=>{if(o.isMesh){o.geometry.dispose();o.material.dispose();}});
    await Promise.all(state.views.map(paint));loadReview();
    $('stats').textContent=state.model.vertices.toLocaleString()+' source vertices · '+state.model.triangles.toLocaleString()+' triangles · '+state.model.parts+' mesh parts · '+state.model.groups.length+' material groups';
    $('provenance').textContent=JSON.stringify(state.model,null,2);
    if(saved){const v=state.views[0];v.camera.position.fromArray(saved.position);v.controls.target.fromArray(saved.target);v.controls.update();syncCamera(v);}else preset('front');
    state.ready=true;updateView();$('fighter').value=fighter;$('error').hidden=true;
  }finally{state.busy=false;document.querySelectorAll('select,button,input,textarea').forEach(e=>e.disabled=!state.ready&&e.id!=='fighter');}
}
async function init(){
  document.querySelectorAll('select,button,input,textarea').forEach(el=>el.disabled=true);
  state.config=await api('/api/config');const listing=await api('/api/models');state.models=listing.models;state.saved=listing.state;
  if(!state.models.length)throw Error('No fighter preview exported yet. Run scripts/defjam_model.py against your own dump.');
  $('fighter').replaceChildren(...state.models.map(m=>new Option(m.name,m.id)));
  state.views=['left','right'].map(createViewport);
  function render(){requestAnimationFrame(render);for(const v of state.views)v.renderer.render(v.scene,v.camera);}render();
  $('fighter').addEventListener('change',()=>chooseFighter($('fighter').value).catch(error));
  $('left').addEventListener('change',()=>paint(state.views[0]).catch(error));
  $('right').addEventListener('change',()=>exclusive(async()=>{
    const previous=state.reviewRevision;
    // The event already changed the select; save the previous review first.
    const next=$('right').value;
    try{if(previous){$('right').value=previous;await saveNotes();}$('right').value=next;await paint(state.views[1]);loadReview();state.reviewRevision=next;}catch(e){$('right').value=previous;error(e);}
  }).catch(error));
  $('lighting').addEventListener('change',()=>Promise.all(state.views.map(paint)).catch(error));$('wireframe').addEventListener('change',updateView);
  for(const kind of ['front','back','fit','chest','belt'])$(kind).addEventListener('click',()=>preset(kind));
  $('hold').addEventListener('pointerdown',e=>{e.preventDefault();$('hold').setPointerCapture(e.pointerId);state.hold=true;paint(state.views[1]).catch(error);});
  for(const name of ['pointerup','pointercancel','lostpointercapture'])$('hold').addEventListener(name,()=>{if(state.hold){state.hold=false;paint(state.views[1]).catch(error);}});
  $('hold').addEventListener('keydown',e=>{if(e.code==='Space'||e.code==='Enter'){e.preventDefault();state.hold=true;paint(state.views[1]).catch(error);}});
  $('hold').addEventListener('keyup',()=>{state.hold=false;paint(state.views[1]).catch(error);});
  $('notes').addEventListener('input',reviewChanged);$('flag').addEventListener('change',reviewChanged);$('save-notes').addEventListener('click',()=>exclusive(saveNotes).catch(error));
  $('restore-draft').addEventListener('click',()=>{const d=JSON.parse(localStorage.getItem(draftKey()));$('notes').value=d.notes;$('flag').checked=d.flag;reviewChanged();});
  addEventListener('beforeunload',e=>{if(state.dirty){e.preventDefault();e.returnValue='';}});
  addEventListener('pagehide',()=>{
    clearTimeout(viewTimer);
    if(state.ready)fetch('/api/model-view',{method:'POST',headers:{'Content-Type':'application/json','X-Workshop-Token':state.config.token},
      body:JSON.stringify({fighter:state.fighter,view:viewState()}),keepalive:true}).catch(()=>{});
  });
  await chooseFighter(state.models.some(m=>m.id===state.saved.fighter)?state.saved.fighter:state.models[0].id);
  state.reviewRevision=$('right').value;
}
init().catch(error);
