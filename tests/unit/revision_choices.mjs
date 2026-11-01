import assert from 'node:assert/strict';
const {visibleCandidates,chooseRevision}=await import(new URL('../../src/defjam_tools/resources/revision_choices.js',import.meta.url));
const candidate=(id,tags=[],status='unreviewed',selected=false)=>({id,review:{tags,status,selected}});
const all=[candidate('left',['archived']),candidate('right',['archived']),candidate('target',['archived']),candidate('parent',['archived']),candidate('approved',['archived'],'approved'),candidate('selected',['archived'],'unreviewed',true),candidate('unrelated',['archived']),candidate('new')];
for (const showArchived of [true,false,true,false]) {
  const visible=visibleCandidates(all,{showArchived,pinned:['left','right','target','parent']});
  const ids=visible.map(c=>c.id);
  assert.equal(chooseRevision(ids,'left','new'),'left');
  assert.equal(chooseRevision(ids,'right','new'),'right');
  for(const pin of ['target','parent','approved','selected'])assert.ok(ids.includes(pin));
  assert.equal(ids.includes('unrelated'),showArchived);
}
assert.equal(chooseRevision(['original','new'],'deleted','original'),'original');
assert.equal(chooseRevision(['new'],'deleted'),'');
assert.equal(chooseRevision(['new',''],'','new'),''); // intentionally empty gallery lane
assert.deepEqual(visibleCandidates(all).map(c=>c.id),['approved','selected','new']);
assert.equal(all[0].review.status,'unreviewed'); // visibility never approves
