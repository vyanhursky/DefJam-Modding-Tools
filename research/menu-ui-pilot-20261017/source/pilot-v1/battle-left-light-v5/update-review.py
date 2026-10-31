"""Current v5 corrects requested side; v4 is retained as wrong-side history."""
from pathlib import Path
p=Path(__file__).resolve().parent;s=(p/'review-before.html').read_text()
s=s.replace('<option value="v4">Current · setup v4 / approved fighters</option>','<option value="v5">Current · setup v5 / approved fighters</option><option value="v4">History · v4 right lighting, reverted</option>',1)
s=s.replace('Battle match setup v4 refines only the upper-right ceiling and wall illumination. The improved v3 left brickwork, original 4:3 center, ceiling geometry and lower right wall are retained. It remains a review draft.','Battle match setup v5 corrects the upper-left lighting, following the clarified feedback. The improved brick texture is retained, and the entire right side is restored to its pre-v4 appearance. The original 4:3 center is unchanged. This remains a review draft.',1)
s=s.replace('<details id="battle-right-light"><summary>Battle setup · upper-right lighting before / after</summary>','<details id="battle-right-light"><summary>History · v4 right-side lighting edit, reverted in v5</summary>',1)
s=s.replace('Current · v4 lighting','History · v4 lighting (reverted)',1)
i=s.index('<details id="battle-right-light">');s=s[:i]+'''<details id="battle-left-light"><summary>Battle setup · upper-left lighting before / after</summary><div class="row"><div><strong>Previous · v3 left lighting</strong><img src="battle-left-light-v5/left-light-before.png" alt="Upper-left lighting before refinement"></div><div><strong>Current · v5 left lighting</strong><img src="battle-left-light-v5/left-light-current.png" alt="Upper-left lighting refined with existing brick texture"></div></div><p><a href="battle-left-light-v5/full-left-light-proof.png">Full upper-left context</a> · <a href="battle-left-light-v5/generations.json">Exact lighting prompt and reference</a> · <a href="battle-left-light-v5/assembly-receipt.json">Lighting-only recipe</a> · <a href="battle-left-light-v5/verification.json">Preservation checks</a></p><p>Only broad illumination on added upper-left artwork changes. Original brick detail is retained. The original center and entire pre-v4 right side match exactly.</p></details>
'''+s[i:]
s=s.replace('V3 left join · retained in v4','V3 material · before v5 lighting',1)
s=s.replace('Only added left artwork changes. The original center, full right side and approved fighter backgrounds retain their exact pixels. Previous setup revisions remain available above.','This panel records the v3 material repair. V5 retains that texture detail with a separate upper-left lighting adjustment; compare the current lighting panel above. Earlier setup revisions remain available.',1)
a=s.index('function battleMenu(){');b=s.index("\nfor(const id of ['battle-menu'",a);f=s[a:b]
f=f.replace("revsel.value='v4'","revsel.value='v5'")
f=f.replace("light=a==='cmtype'&&rev==='v4',","leftlight=a==='cmtype'&&rev==='v5',light=a==='cmtype'&&rev==='v4',")
f=f.replace("base=(light?","base=(leftlight?'battle-left-light-v5/':light?")
f=f.replace("(light?'-v4.png'","(leftlight?'-v5.png':light?'-v4.png'")
f=f.replace("light?'Battle setup v4 · awaiting feedback'","leftlight?'Battle setup v5 · awaiting feedback':light?'Battle setup v4 · reverted right edit'")
f=f.replace("'battle-right-light']","'battle-right-light','battle-left-light']")
f=f.replace("light?'setup v4 · review draft'","leftlight?'setup v5 · review draft':light?'setup v4 · reverted history'")
s=s[:a]+f+s[b:];(p.parent/'review.html').write_text(s);print('V5 current;v4 clearly reverted history;v3/v2/v1 retained')
