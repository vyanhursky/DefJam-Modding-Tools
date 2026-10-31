from pathlib import Path
from PIL import Image

root=Path(__file__).resolve().parent
p=root.parent/'review.html'
old=p.read_text()
(root/'review-before-v3.html').write_text(old)
for side,edge in [('left',1600),('right',3520)]:
    Image.open(root.parent/'title-skyline-wide-master-draft.png').crop((edge-384,350,edge+384,1024)).save(root/(side+'-initial-close.png'))
new=old.replace('<option value="refined">Refined cloud joins</option><option value="initial">Initial extension</option>',
    '<option value="refined">Refined cloud joins · full height</option><option value="previous">Previous repair · upper sky</option><option value="initial">Initial extension</option>')
new=new.replace('The refined version repairs cloud flow in two narrow bands on the generated sides.',
    'The current version keeps the accepted left join and extends the right repair through the lower clouds and horizon haze.')
new=new.replace('<option value="left">Left edge of original4:3</option><option value="right">Right edge of original4:3</option>',
    '<option value="right">Right edge of original4:3</option><option value="left">Left edge of original4:3</option>')
new=new.replace('refined?\'seam-v2/title-skyline-\'+id+\'-refined.png\':\'title-skyline-\'+id+\'-layer-preview.png\'',
    'refined?\'seam-v3/title-skyline-\'+id+\'-v3.png\':document.querySelector(\'#wide-version\').value===\'previous\'?\'seam-v2/title-skyline-\'+id+\'-refined.png\':\'title-skyline-\'+id+\'-layer-preview.png\'')
new=new.replace("(refined?'Refined cloud joins':'Initial extension')",
    "document.querySelector('#wide-version').selectedOptions[0].textContent")
new=new.replace("'seam-v2/'+side+'-before-close.png'","'seam-v3/'+side+'-initial-close.png'")
new=new.replace("'seam-v2/'+side+'-refined-close.png'","'seam-v3/'+side+'-current-close.png'")
new=new.replace("a.href='seam-v2/title-skyline-'+id+'-refined.png'","a.href='seam-v3/title-skyline-'+id+'-v3.png'")
new=new.replace('<a href="seam-v2/title-skyline-wide-master-refined.png">Refined5120×1536 texture master</a>',
    '<a href="seam-v3/title-skyline-wide-master-v3.png">Current5120×1536 texture master</a> · <a href="seam-v3/receipt.json">Full-height right repair: prompt and checks</a> · <a href="seam-v3/right-join-before-after.png">Previous/current right join</a>')
assert new!=old
p.write_text(new)
