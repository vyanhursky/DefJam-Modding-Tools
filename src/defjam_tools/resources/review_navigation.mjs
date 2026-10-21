/* Linked 2D review navigation. Normalized offsets keep unequal responsive panes aligned. */
export function zoomAt(state, factor, point = [.5, .5]) {
  const z = Math.max(1, Math.min(32, state.z * factor));
  if(z === state.z) return {...state};
  const ratio = z / state.z;
  return {z, x: point[0] - (point[0] - state.x) * ratio,
    y: point[1] - (point[1] - state.y) * ratio};
}
export function panBy(state, dx, dy, width, height) {
  return {...state, x: state.x + dx / width, y: state.y + dy / height};
}
export function attachReviewNavigation(root = document) {
  const groups = new Map(), seen = new WeakSet();
  function groupFor(key) {
    if (groups.has(key)) return groups.get(key);
    const g = {state:{z:1,x:0,y:0}, views:[], key}; groups.set(key,g);
    const bar = document.createElement('div'); bar.className='review-nav';
    bar.setAttribute('role','group'); bar.setAttribute('aria-label','Image navigation');
    const hint=document.createElement('span'); hint.textContent='Scroll to zoom · drag to pan · linked comparison'; bar.append(hint);
    const status=document.createElement('output');status.textContent='1×';
    for(const [label,action] of [['−',()=>zoom(.8)],['+',()=>zoom(1.25)],['Fit',()=>reset(g)]]) {
      const b=document.createElement('button');b.type='button';b.textContent=label;
      b.setAttribute('aria-label',label==='Fit'?'Fit images':label==='+'?'Zoom in':'Zoom out');b.onclick=action;bar.append(b);
    }
    function zoom(f){g.state=zoomAt(g.state,f);paint(g);}
    g.status=status;bar.append(status);key.before(bar);return g;
  }
  function paint(g) {
    for(const {viewport,content} of g.views) {
      const {z,x,y}=g.state;content.style.transform=`translate(${x*100}%,${y*100}%) scale(${z})`;
      viewport.dataset.zoom=String(z);viewport.dataset.pan=`${x},${y}`;
    }
    g.status.textContent=`${g.state.z.toFixed(2).replace(/\.00$/,'')}×`;
  }
  function reset(g){g.state={z:1,x:0,y:0};paint(g);}
  function scan() {
    for(const img of root.querySelectorAll('img:not([data-no-navigation])')) {
      if(seen.has(img)||img.closest('.review-viewport'))continue;seen.add(img);
      // A wipe's two overlapping images and bounds overlay move as one layer.
      const wipe=img.closest('.frame,[class$="-frame"]') || img.closest('[class*="-wipe"],.wipe');
      let viewport=wipe || (img.parentElement.classList.contains('frame')?img.parentElement:null);
      if(!viewport){viewport=document.createElement('div');img.before(viewport);viewport.append(img);}
      if(viewport.classList.contains('review-viewport'))continue;
      const key=viewport.closest('[id$="-comparison"]') || viewport.closest('.row,[class$="-grid"]') || viewport;
      const g=groupFor(key),content=document.createElement('div');content.className='review-content';
      content.append(...viewport.childNodes);viewport.append(content);viewport.classList.add('review-viewport');
      viewport.tabIndex=0;viewport.setAttribute('aria-label','Zoomable image: '+(img.alt||'texture'));
      const entry={viewport,content};g.views.push(entry);paint(g);
      let drag=null;
      viewport.addEventListener('wheel',e=>{
        e.preventDefault();const b=viewport.getBoundingClientRect();if(!b.width||!b.height)return;
        const delta=e.deltaY*(e.deltaMode===1?16:e.deltaMode===2?b.height:1);
        g.state=zoomAt(g.state,Math.exp(-Math.max(-500,Math.min(500,delta))*.002),[(e.clientX-b.left)/b.width,(e.clientY-b.top)/b.height]);paint(g);
      },{passive:false});
      viewport.addEventListener('pointerdown',e=>{
        if(e.button!==0&&e.button!==2)return;e.preventDefault();viewport.setPointerCapture(e.pointerId);
        drag={id:e.pointerId,x:e.clientX,y:e.clientY};viewport.classList.add('dragging');
      });
      viewport.addEventListener('pointermove',e=>{
        if(!drag||drag.id!==e.pointerId)return;const b=viewport.getBoundingClientRect();
        if(b.width&&b.height)g.state=panBy(g.state,e.clientX-drag.x,e.clientY-drag.y,b.width,b.height);
        drag.x=e.clientX;drag.y=e.clientY;paint(g);
      });
      const stop=()=>{drag=null;viewport.classList.remove('dragging');};
      for(const name of ['pointerup','pointercancel','lostpointercapture'])viewport.addEventListener(name,stop);
      viewport.addEventListener('contextmenu',e=>e.preventDefault());
      viewport.addEventListener('dblclick',()=>reset(g));
      viewport.addEventListener('keydown',e=>{
        if(e.key==='0'||e.key==='Home'){e.preventDefault();reset(g);}
        else if(e.key==='+'||e.key==='='||e.key==='-'){e.preventDefault();g.state=zoomAt(g.state,e.key==='-'?.8:1.25);paint(g);}
        else if(['ArrowLeft','ArrowRight','ArrowUp','ArrowDown'].includes(e.key)){
          e.preventDefault();g.state=panBy(g.state,e.key==='ArrowLeft'?-24:e.key==='ArrowRight'?24:0,e.key==='ArrowUp'?-24:e.key==='ArrowDown'?24:0,viewport.clientWidth,viewport.clientHeight);paint(g);
        }
      });
      for(const image of content.querySelectorAll('img')) {
        seen.add(image);image.draggable=false;
        // Source/aspect changes start at Fit; palette/background/view toggles retain framing.
        new MutationObserver(records=>{if(records.some(r=>r.oldValue!==image.getAttribute('src')))reset(g);}).observe(image,{attributes:true,attributeFilter:['src'],attributeOldValue:true});
      }
    }
  }
  scan();const observer=new MutationObserver(scan);observer.observe(root,{childList:true,subtree:true});
  return {disconnect:()=>observer.disconnect()};
}
if(typeof document!=='undefined')attachReviewNavigation();
