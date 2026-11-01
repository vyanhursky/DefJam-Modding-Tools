"""Synthetic clothing palette checks; no game pixels or geometry."""
import numpy as np
from PIL import Image
import pytest
from defjam_tools import material_palette as m


def mesh(group,x0,y0,x1,y1):
    return dict(group=group,uv=[[x0,y0],[x1,y0],[x0,y1],[x1,y1]],indices=[0,1,2,1,3,2])


def test_holds_shared_skin_and_neighbor_guard():
    g=dict(schema=1,meshes=[mesh('emc4_cloth',.1,.1,.9,.9),mesh('emc2_skin',.4,.1,.6,.9)])
    editable,held,coverage=m.clothing_mask(g,64)
    assert coverage[20,32] and held[20,32] and not editable[20,32]
    assert not editable[20,24] and editable[20,12]


@pytest.mark.parametrize('color',[(190,30,25),(25,40,170),(18,18,18)])
def test_removes_red_blue_and_neutral_drift_with_exact_skin_and_alpha(color):
    source=np.empty((128,128,4),np.uint8);source[:]=[*color,255]
    source[...,3]=np.arange(128,dtype=np.uint8)[None,:]
    raw=source.copy();raw[:,:,:3]=np.clip(np.array(color)+[20,8,12],0,255)
    g=dict(schema=1,meshes=[mesh('emc4_cloth',.1,.1,.45,.9),mesh('emc2_skin',.55,.1,.9,.9)])
    result,report,mask=m.match(Image.fromarray(source),Image.fromarray(raw),g,64,radius=3)
    out=np.asarray(result);editable=np.asarray(mask)>0
    assert np.array_equal(out[~editable],raw[~editable])
    assert np.array_equal(out[...,3],source[...,3])
    assert report['median_Lab_distance_after']<report['median_Lab_distance_before']*.1
    assert all(report['checks'].values())


def test_fine_weave_survives_palette_matching():
    ref=Image.new('RGBA',(128,128),(100,100,100,255));raw=np.array(ref)
    raw[:,:,:3]=140;raw[::2,::2,:3]=160
    g=dict(schema=1,meshes=[mesh('emc4_cloth',.1,.1,.9,.9)])
    result,report,_=m.match(ref,Image.fromarray(raw),g,64,3)
    out=np.array(result)
    assert out[50:70,50:70,0].std()>5
    assert report['median_Lab_distance_after']<2


def test_identical_source_stays_exact():
    rng=np.random.default_rng(2);raw=rng.integers(0,256,(128,128,4),dtype=np.uint8)
    im=Image.fromarray(raw);g=dict(schema=1,meshes=[mesh('emc4_cloth',.1,.1,.9,.9)])
    result,_,_=m.match(im,im,g,64,3)
    assert np.array_equal(np.asarray(result),raw)


def test_rejects_alpha_changes_and_missing_cloth():
    im=Image.new('RGBA',(128,128),(100,100,100,255));raw=im.copy();raw.putalpha(100)
    g=dict(schema=1,meshes=[mesh('emc4_cloth',.1,.1,.9,.9)])
    with pytest.raises(ValueError,match='alpha'):m.match(im,raw,g,64,3)
    with pytest.raises(ValueError,match='No source clothing'):m.match(im,im,dict(schema=1,meshes=[]),64,3)
