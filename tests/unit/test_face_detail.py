"""Synthetic post-imagegen patch invariants, with no game artwork."""
import numpy as np
from PIL import Image
import pytest
from defjam_tools.face_detail import merge


def test_palette_matching_preserves_alpha_exterior_held_tiles_and_seams():
    source=np.empty((80,80,4),np.uint8);source[:]=[145,103,75,255]
    source[...,3]=np.arange(80,dtype=np.uint8)[None,:]
    parent=source.copy();parent[60:,:,:3]=[20,30,40]
    generated=np.empty((40,40,3),np.uint8);generated[:]=[175,125,70]
    guard=np.zeros((80,80));guard[20:25,20:60]=1
    result,report=merge(Image.fromarray(source),Image.fromarray(parent),Image.fromarray(generated),
                        (20,20,60,60),[(12,12,20,20)],guard,strength=.7,radius=3,edge=4)
    out=np.asarray(result)
    assert all(report['checks'].values())
    assert np.array_equal(out[...,3],parent[...,3])
    assert np.array_equal(out[:20],parent[:20])
    assert np.array_equal(out[60:],parent[60:])
    assert np.array_equal(out[32:40,32:40],parent[32:40,32:40])
    assert np.array_equal(out[20:25,20:60],parent[20:25,20:60])
    assert np.max(abs(out[45:50,45:50,:3].astype(int)-source[45:50,45:50,:3]))<=1


def test_new_fine_detail_survives_without_changing_outer_border():
    ref=Image.new('RGBA',(80,80),(145,103,75,230))
    raw=np.full((40,40,3),130,np.uint8);raw[::2,::2]=170
    result,report=merge(ref,ref,Image.fromarray(raw),(20,20,60,60),radius=3,edge=4)
    assert report['edited_pixels']>0
    assert np.array_equal(np.asarray(result)[20,20:60],np.asarray(ref)[20,20:60])


@pytest.mark.parametrize('damage',['aspect','alpha','guard','held'])
def test_incompatible_patch_inputs_are_rejected(damage):
    ref=Image.new('RGBA',(80,80),(145,103,75,230));parent=ref.copy()
    generated=Image.new('RGB',(40,40),(160,110,75));kwargs={}
    if damage=='aspect':generated=generated.resize((40,30))
    if damage=='alpha':parent.putalpha(255)
    if damage=='guard':kwargs['guard']=np.full((80,80),np.nan)
    if damage=='held':kwargs['held_boxes']=[(0,0,45,10)]
    with pytest.raises(ValueError):merge(ref,parent,generated,(20,20,60,60),radius=3,edge=4,**kwargs)
