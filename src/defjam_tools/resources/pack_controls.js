// Shared camera geometry uses original-canvas coordinates, independent of PNG resolution.
export const PAGE_SIZES = [10, 25, 50, 100, 200];
export const pageSize = value => PAGE_SIZES.includes(Number(value)) ? Number(value) : 50;
export const clamp = (n, low, high) => Math.max(low, Math.min(high, n));
export const fitScale = (base, view) => Math.min(Math.max(1, view[0]-24)/base[0], Math.max(1, view[1]-24)/base[1]);
export function zoomAxis(base, view, scroll, before, after, pointer) {
  const oldSize=base*before, newSize=base*after;
  const anchor=clamp((pointer+scroll-Math.max(0,(view-oldSize)/2))/oldSize,0,1);
  const next=clamp(anchor*newSize-pointer,0,Math.max(0,newSize-view));
  return newSize<=view ? .5 : (next+view/2)/newSize;
}
export function scrollAxis(base, view, factor, center) {
  return clamp(center*base*factor-view/2,0,Math.max(0,base*factor-view));
}

export class InspectCamera {
  constructor(root, baseSize, onScale) {
    this.root=root; this.baseSize=baseSize; this.onScale=onScale;
    this.factor=null; this.center=[.5,.5]; this.expected=new WeakMap(); this.drag=null;
    if(typeof ResizeObserver!=='undefined')new ResizeObserver(()=>this.layout()).observe(root);
    root.addEventListener('wheel',event=>this.wheel(event),{passive:false});
    root.addEventListener('pointerdown',event=>this.down(event));
    root.addEventListener('pointermove',event=>this.move(event));
    for(const type of ['pointerup','pointercancel','lostpointercapture'])root.addEventListener(type,event=>this.up(event));
    root.addEventListener('scroll',event=>this.scrolled(event.target),true);
    root.addEventListener('dblclick',event=>{if(this.port(event.target)){event.preventDefault();this.setScale(null);this.onScale(null);}});
  }
  port(target) {
    const port=target.closest?.('.viewport');
    return port&&this.root.contains(port)&&port.querySelector('img') ? port : null;
  }
  ports() {return [...this.root.querySelectorAll('.viewport')].filter(p=>p.querySelector('img'));}
  setScale(factor, reset=false) {
    this.factor=factor===null?null:clamp(factor,.1,16);
    if(reset||factor===null)this.center=[.5,.5];
    this.layout();
  }
  layout() {
    if(!this.ports().length)return;
    const base=this.baseSize();
    for(const p of this.ports()) {
      const im=p.querySelector('img');p.classList.toggle('fit',this.factor===null);
      im.draggable=false;
      im.style.width=this.factor===null?'':base[0]*this.factor+'px';
      im.style.height=this.factor===null?'':base[1]*this.factor+'px';
      p.scrollLeft=this.factor===null?0:scrollAxis(base[0],p.clientWidth,this.factor,this.center[0]);
      p.scrollTop=this.factor===null?0:scrollAxis(base[1],p.clientHeight,this.factor,this.center[1]);
      this.expected.set(p,[p.scrollLeft,p.scrollTop]);
    }
  }
  scrolled(p, force=false) {
    if(this.factor===null||!this.ports().includes(p))return;
    const expected=this.expected.get(p);
    if(!force&&expected&&Math.abs(expected[0]-p.scrollLeft)<1&&Math.abs(expected[1]-p.scrollTop)<1)return;
    const base=this.baseSize();
    this.center=[p.clientWidth>=base[0]*this.factor ? .5 : (p.scrollLeft+p.clientWidth/2)/(base[0]*this.factor),
                 p.clientHeight>=base[1]*this.factor ? .5 : (p.scrollTop+p.clientHeight/2)/(base[1]*this.factor)];
    this.layout();
  }
  wheel(event) {
    const p=this.port(event.target);if(!p||!event.deltaY)return;
    event.preventDefault();
    const base=this.baseSize(),view=[p.clientWidth,p.clientHeight];
    const before=this.factor??fitScale(base,view);
    const units=event.deltaMode===1?16:event.deltaMode===2?p.clientHeight:1;
    const after=clamp(before*Math.exp(-clamp(event.deltaY*units,-600,600)*(event.ctrlKey ? .01 : .002)),.1,16);
    const rect=p.getBoundingClientRect();
    this.center=[zoomAxis(base[0],view[0],p.scrollLeft,before,after,event.clientX-rect.left-p.clientLeft),
                 zoomAxis(base[1],view[1],p.scrollTop,before,after,event.clientY-rect.top-p.clientTop)];
    this.factor=after;this.layout();this.onScale(after);
  }
  down(event) {
    const p=this.port(event.target);if(!p||event.button!==0)return;
    event.preventDefault();p.focus({preventScroll:true});p.setPointerCapture(event.pointerId);
    this.drag={p,id:event.pointerId,x:event.clientX,y:event.clientY,left:p.scrollLeft,top:p.scrollTop};
    this.root.classList.add('dragging');
  }
  move(event) {
    const d=this.drag;if(!d||event.pointerId!==d.id)return;
    event.preventDefault();d.p.scrollLeft=d.left+d.x-event.clientX;d.p.scrollTop=d.top+d.y-event.clientY;
    this.scrolled(d.p,true);
  }
  up(event) {
    if(!this.drag||event.pointerId!==this.drag.id)return;
    const {p,id}=this.drag;this.drag=null;this.root.classList.remove('dragging');
    if(p.hasPointerCapture(id))p.releasePointerCapture(id);
  }
}
