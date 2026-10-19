"""Add local-lighting v4; retain v3/v2/v1 and approved fighter paths."""
from pathlib import Path
p=Path(__file__).resolve().parent;s=(p/'review-before.html').read_text()
s=s.replace('<option value="v3">Current · setup v3 / approved fighters</option>','<option value="v4">Current · setup v4 / approved fighters</option><option value="v3">Previous · setup v3</option>',1)
s=s.replace('Battle match setup v3 is a new review draft: its full left brick continuation is regenerated from the native material and calibrated to the original border. Its original center and complete v2 right side are unchanged.','Battle match setup v4 refines only the upper-right ceiling and wall illumination. The improved v3 left brickwork, original 4:3 center, ceiling geometry and lower right wall are retained. It remains a review draft.',1)
i=s.index('<details id="battle-left-material">');s=s[:i]+'''<details id="battle-right-light"><summary>Battle setup · upper-right lighting before / after</summary><div class="row"><div><strong>Previous · v3 lighting</strong><img src="battle-right-light-v4/right-light-before.png" alt="V3 upper-right lighting before correction"></div><div><strong>Current · v4 lighting</strong><img src="battle-right-light-v4/right-light-current.png" alt="V4 upper-right lighting correction"></div></div><p><a href="battle-right-light-v4/full-right-light-proof.png">Full upper-right continuation</a> · <a href="battle-right-light-v4/generations.json">Lighting prompt and reference</a> · <a href="battle-right-light-v4/assembly-receipt.json">Lighting-only recipe</a> · <a href="battle-right-light-v4/verification.json">Preservation checks</a></p><p>Existing texture detail and geometry are retained. Only broad illumination beyond the right original 4:3 boundary changes; the left and original center retain exact pixels.</p></details>
'''+s[i:]
s=s.replace('Current · v3 left join','V3 left join · retained in v4',1)
a=s.index('function battleMenu(){');b=s.index("\nfor(const id of ['battle-menu'",a);f=s[a:b]
f=f.replace("revsel.value='v3'","revsel.value='v4'")
f=f.replace("latest=a==='cmtype'&&rev==='v3',","light=a==='cmtype'&&rev==='v4',latest=a==='cmtype'&&rev==='v3',")
f=f.replace("base=(latest?","base=(light?'battle-right-light-v4/':latest?")
f=f.replace("(latest?'-v3.png'","(light?'-v4.png':latest?'-v3.png'")
f=f.replace("latest?'Battle setup v3 · awaiting feedback'","light?'Battle setup v4 · awaiting feedback':latest?'Battle setup v3 · previous draft'")
f=f.replace("['battle-ceiling','battle-left-material']","['battle-ceiling','battle-left-material','battle-right-light']")
f=f.replace("latest?'setup v3 · review draft'","light?'setup v4 · review draft':latest?'setup v3 · history'")
s=s[:a]+f+s[b:];(p.parent/'review.html').write_text(s);print('V4 current;V3/V2/V1 history;fighter paths retained')
