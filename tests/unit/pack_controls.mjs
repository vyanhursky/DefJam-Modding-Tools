import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const code=readFileSync(new URL('../../src/defjam_tools/resources/pack_controls.js',import.meta.url),'utf8');
const {PAGE_SIZES,pageSize,zoomAxis,scrollAxis,fitScale,InspectCamera}=await import('data:text/javascript;base64,'+Buffer.from(code).toString('base64'));
for(const n of PAGE_SIZES)assert.equal(pageSize(String(n)),n);
for(const invalid of [null,0,60,'bad',Infinity])assert.equal(pageSize(invalid),50);
const center=zoomAxis(256,300,250,2,3,100);
assert.equal(scrollAxis(256,300,3,center),425);
assert.equal((425+100)/3,(250+100)/2,'zoom must preserve the canvas point under the cursor');
assert.equal(zoomAxis(32,300,0,1,2,100),.5,'small axes remain centered');
assert.equal(scrollAxis(32,300,2,.1),0);
assert.equal(scrollAxis(256,300,3,2),468,'right edge is bounded');
assert.equal(fitScale([256,128],[280,152]),1);
const classes=()=>({add(){},remove(){},toggle(){}});
function port(){
  const image={style:{}};
  let left=0,top=0;
  return {clientWidth:300,clientHeight:220,clientLeft:0,clientTop:0,classList:classes(),
    get scrollLeft(){return left;},set scrollLeft(n){left=Math.max(0,Math.min(n,parseFloat(image.style.width||0)-300));},
    get scrollTop(){return top;},set scrollTop(n){top=Math.max(0,Math.min(n,parseFloat(image.style.height||0)-220));},
    querySelector(){return image;},closest(){return this;},getBoundingClientRect(){return {left:0,top:0};},
    focus(){},setPointerCapture(){},hasPointerCapture(){return true;},releasePointerCapture(){}};
}
const panes=[port(),port(),port()],events={};
const root={classList:classes(),contains:p=>panes.includes(p),querySelectorAll:()=>panes,addEventListener:(name,fn)=>{events[name]=fn;}};
let lastScale;
const camera=new InspectCamera(root,()=>[256,128],factor=>{lastScale=factor;});
camera.setScale(null);
const wheel={target:panes[1],deltaY:-400,deltaMode:0,clientX:150,clientY:110,preventDefault(){this.prevented=true;}};
events.wheel(wheel);
assert.ok(wheel.prevented);assert.ok(lastScale>1);assert.equal(lastScale,camera.factor);
const start=[panes[0].scrollLeft,panes[0].scrollTop];
events.pointerdown({target:panes[2],button:0,pointerId:1,clientX:200,clientY:100,preventDefault(){}});
events.pointermove({pointerId:1,clientX:170,clientY:80,preventDefault(){}});
for(const p of panes){assert.ok(Math.abs(p.scrollLeft-start[0]-30)<.001);assert.ok(Math.abs(p.scrollTop-start[1]-20)<.001);}
events.pointerup({pointerId:1});assert.equal(camera.drag,null);
panes.push(port());camera.layout();
for(const p of panes){assert.equal(p.scrollLeft,panes[0].scrollLeft);assert.equal(p.scrollTop,panes[0].scrollTop);assert.equal(p.querySelector().style.width,panes[0].querySelector().style.width);}
events.wheel({...wheel,target:panes[3],deltaY:-10000});assert.ok(camera.factor<=16);
events.dblclick({target:panes[3],preventDefault(){}});assert.equal(camera.factor,null);assert.equal(lastScale,null);
const empty=new InspectCamera({...root,querySelectorAll:()=>[]},()=>{throw new Error('No active texture');},()=>{});empty.layout();
console.log('Page sizes, cursor-anchored zoom, bounds, shared wheel/drag and late fourth pane pass');
