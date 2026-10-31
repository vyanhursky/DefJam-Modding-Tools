import numpy as np
from PIL import Image, ImageDraw
import pytest
from defjam_tools import menu_native as n


def test_joined_materials_share_exact_transformed_pixels():
    raw=Image.new('RGBA',(20,8));ImageDraw.Draw(raw).rectangle((2,2,17,5),fill=(180,40,30,255))
    rendered,_=n.fit_canvas(raw,(10,4),(1,1,9,3),scale=4)
    parts=[]
    for x0,x1 in [(0,5),(5,10)]:
        atlas=Image.new('RGBA',(20,16),(10,20,30,0))
        parts.append(n.material_patch(atlas,rendered,[0,0,5,4],[x0,0,x1,4]))
    joined=Image.new('RGBA',rendered.size);joined.paste(parts[0],(0,0));joined.paste(parts[1],(20,0))
    assert joined.tobytes()==rendered.tobytes()


def test_patch_keeps_unrelated_pixels_and_rejects_wrong_extent():
    atlas=Image.new('RGBA',(16,16),(50,60,70,255));render=Image.new('RGBA',(8,8),(9,19,29,100))
    out=n.material_patch(atlas,render,[1,1,3,3],[0,0,2,2])
    assert out.getpixel((0,0))==atlas.getpixel((0,0))
    assert out.crop((4,4,12,12)).tobytes()==render.tobytes()
    with pytest.raises(ValueError):n.material_patch(atlas,render,[0,0,4,4],[0,0,2,2])


def test_repeated_guard_requires_identical_source_pixels():
    source=Image.new('RGBA',(5,5),(0,0,0,0));a=np.array(source);a[1:4,1:4]=(10,20,30,255);a[1:4,4]=(10,20,30,255);a[0,2]=(99,22,33,255);source=Image.fromarray(a)
    atlas=source.resize((20,20),Image.Resampling.NEAREST);canvas=np.array(atlas);canvas[4:16,4:16]=(150,160,170,255)
    out,_=n.repeated_guard(source,Image.fromarray(canvas),[1,1,4,4])
    assert out.getpixel((17,8))==(150,160,170,255)
    assert out.getpixel((8,0))==(99,22,33,255)


def page(positions,size):
    im=Image.new('RGBA',size);d=ImageDraw.Draw(im)
    for box in positions:d.rectangle(box,fill=(200,190,180,255))
    return im


def test_glyph_registration_restores_individual_cells():
    source=page([(2,2,4,6),(9,3,12,6),(2,11,5,14),(12,10,14,15)],(20,20))
    raw=page([(3,2,12,18),(24,4,34,18),(5,32,15,43),(30,29,38,47)],(50,55))
    out,receipt=n.register_glyph_page(source,raw,scale=4)
    assert receipt['row_counts']==[2,2] and receipt['glyph_count']==4
    actual=n.glyph_cells(out);expected=n.glyph_cells(source)
    assert [len(row) for row in actual]==[len(row) for row in expected]
    assert max(abs(a-b*4) for ar,er in zip(actual,expected) for ab,eb in zip(ar,er) for a,b in zip(ab,eb))<=1
    assert out.size==(80,80)
    with pytest.raises(ValueError,match='mismatch'):n.register_glyph_page(source,Image.new('RGBA',(20,20)))


def test_protected_gray_marks_are_exact_and_other_pixels_unchanged():
    source=Image.new('RGBA',(3,2));source.putpixel((1,0),(127,127,127,255));source.putpixel((2,1),(127,127,127,128))
    atlas=Image.new('RGBA',(12,8),(4,5,6,200));out,count=n.preserve_gray_marks(source,atlas)
    assert count==16 and out.getpixel((4,0))==(127,127,127,255)
    assert out.getpixel((8,4))==(4,5,6,200)
