import test from 'node:test';
import assert from 'node:assert/strict';
import {zoomAt,panBy} from '../src/defjam_tools/resources/review_navigation.mjs';
test('zoom retains the texel under an off-center cursor',()=>{
 const s={z:2,x:-.25,y:-.8},p=[.23,.71],n=zoomAt(s,1.7,p);
 for(const [axis,i] of [['x',0],['y',1]])assert.ok(Math.abs((p[i]-s[axis])/s.z-(p[i]-n[axis])/n.z)<1e-12);
});
test('unequal panes pan to the same normalized location',()=>{
 const s={z:4,x:-1,y:-1};assert.deepEqual(panBy(s,20,10,200,100),panBy(s,40,20,400,200));
});
test('zoom clamps without drifting when already at a limit',()=>{
 const s={z:32,x:-4,y:-8};assert.deepEqual(zoomAt(s,10,[.1,.9]),s);
 assert.equal(zoomAt(s,.00001).z,1);
});
test('opposite zoom steps preserve framing',()=>{
 const s={z:1,x:0,y:0},p=[.23,.71];assert.deepEqual(zoomAt(zoomAt(s,4,p),.25,p),s);
});
