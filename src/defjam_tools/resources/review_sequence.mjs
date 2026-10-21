/* Texture navigation for the existing review selectors; no review-data writes. */
export function stepIndex(index, direction, length) {
  return length ? Math.max(0, Math.min(length - 1, index + direction)) : -1;
}
export function attachTextureSequences(root=document) {
  const seen=new WeakSet();
  function scan() {
    const selectors=root.querySelectorAll('select#asset,select#study,select#brand-asset,select[id$="-menu"],select[id$="-item"],select#next-texture');
    for(const select of selectors) {
      if(seen.has(select)||select.options.length<2)continue;seen.add(select);
      const bar=document.createElement('span');bar.className='review-sequence';bar.setAttribute('role','group');
      const label=select.getAttribute('aria-label')||select.id;bar.setAttribute('aria-label',label+' navigation');
      const prev=document.createElement('button'),next=document.createElement('button'),counter=document.createElement('output');
      prev.type=next.type='button';prev.textContent='← Previous';next.textContent='Next →';
      prev.setAttribute('aria-label','Previous texture');next.setAttribute('aria-label','Next texture');counter.setAttribute('aria-live','polite');
      bar.append(prev,counter,next);(select.closest('label')||select).after(bar);
      function sync(){counter.textContent=`${select.selectedIndex+1} / ${select.options.length}`;prev.disabled=select.disabled||select.selectedIndex<=0;next.disabled=select.disabled||select.selectedIndex>=select.options.length-1;}
      function step(direction){
        if(select.disabled)return;let index=select.selectedIndex;
        do {const candidate=stepIndex(index,direction,select.options.length);if(candidate===index)return;index=candidate;}while(select.options[index].disabled);
        select.selectedIndex=index;select.dispatchEvent(new Event('change',{bubbles:true}));sync();
      }
      prev.onclick=()=>step(-1);next.onclick=()=>step(1);
      function keys(e){if(e.altKey||e.ctrlKey||e.metaKey||e.shiftKey)return;if(e.key==='ArrowLeft'||e.key==='ArrowRight'){e.preventDefault();e.stopPropagation();step(e.key==='ArrowLeft'?-1:1);}}
      select.addEventListener('keydown',keys);bar.addEventListener('keydown',keys);select.addEventListener('change',sync);
      select.setAttribute('aria-description','Left and right arrow keys select the previous or next texture.');
      new MutationObserver(sync).observe(select,{childList:true,subtree:true,attributes:true,attributeFilter:['disabled']});sync();
    }
  }
  scan();const observer=new MutationObserver(scan);observer.observe(root,{childList:true,subtree:true});return{disconnect:()=>observer.disconnect()};
}
if(typeof document!=='undefined')attachTextureSequences();
