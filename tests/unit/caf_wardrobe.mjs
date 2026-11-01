import assert from 'node:assert/strict';
import {chooseSelection,findSelection,selectionForChoice} from '../../src/defjam_tools/resources/caf_wardrobe.js';
const selection=(item,style,color)=>({item,style,color,palette:'default'});
const garment={id:'77',colors:[
  {id:'0',fittings:[{id:'0',selection:selection('12:1',2,4)},{id:'2',selection:selection('12:3',1,4)}]},
  {id:'1',fittings:[{id:'0',selection:selection('12:1',2,7)},{id:'2',selection:selection('12:3',1,7)}]},
  {id:'2',fittings:[{id:'0',selection:selection('12:1',2,9)}]}
]};
const before=JSON.stringify(garment);
const chosen=chooseSelection(garment,'1','2');
assert.deepEqual(chosen.fitting.selection,selection('12:3',1,7));
assert.equal(findSelection([garment],chosen.fitting.selection).color.id,'1');
assert.equal(chooseSelection(garment,'2','2').fitting.id,'0'); // only available styles
assert.equal(chooseSelection(garment).color.id,'0');
assert.equal(chooseSelection({colors:[]}),null);
assert.equal(findSelection([garment],selection('12:3',0,7)),null);
const alias={...garment,id:'alias'};
assert.equal(findSelection([garment,alias],chosen.fitting.selection,'alias').garment.id,'alias');
assert.equal(findSelection([garment],{...chosen.fitting.selection,palette:'pl03'}).garment.id,'77');
assert.equal(JSON.stringify(garment),before);
const duplicate={id:'duplicate',colors:[{id:'0',fittings:[{id:'0',selection:selection('12:1',0,1),aliases:[selection('12:1',1,1)]}]}]};
assert.equal(findSelection([duplicate],selection('12:1',1,1)).garment.id,'duplicate');
const oldAlias={...selection('12:1',1,1),palette:'pl03'};
assert.equal(selectionForChoice(chooseSelection(duplicate),oldAlias),oldAlias);
assert.deepEqual(selectionForChoice(chosen,selection('12:1',2,4)),chosen.fitting.selection);
