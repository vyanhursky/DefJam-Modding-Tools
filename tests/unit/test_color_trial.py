"""Synthetic palette/seam tests; no game textures or geometry."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import numpy as np
from PIL import Image
import pytest

from defjam_tools import color_trial as c


BOXES=[[.5,0,.5,.5]]


def fixture():
    body=dict(group="emc2_skin",positions=[[0,1,0],[1,1,0],[0,0,0],[1,0,0]],uv=[[.05,.10],[.45,.10],[.05,.80],[.45,.80]],indices=[0,1,2,1,3,2])
    face=dict(group="emc2_skin",positions=[[0,1,0],[1,1,0],[0,2,0]],uv=[[.55,.4],[.9,.4],[.55,.05]],indices=[0,1,2])
    cloth=dict(group="emc4_cloth",positions=[[0,0,1],[1,0,1],[0,1,1]],uv=[[.55,.6],[.9,.6],[.55,.9]],indices=[0,1,2])
    geometry=dict(schema=1,source_id="synthetic",meshes=[body,face,cloth])
    ref=np.empty((256,256,4),dtype=np.uint8);ref[:]=[170,115,80,255]
    ref[...,3]=np.arange(256,dtype=np.uint8)[None,:]
    raw=ref.copy();raw[:,:,:3]=[188,117,70]
    raw[:128,128:]=ref[:128,128:]
    # Fine neutral ink remains dark; corrections must not tint it blue.
    raw[140:155:2,35:90,:3]=[12,12,12]
    return Image.fromarray(ref),Image.fromarray(raw),geometry


def test_srgb_lab_roundtrip_and_gamut_clipping():
    rgb=np.random.default_rng(10).integers(0,256,size=(40,60,3),dtype=np.uint8)
    result,clipped=c.lab_to_rgb(c.rgb_to_lab(rgb))
    assert np.array_equal(result,rgb)
    assert not clipped.any()
    result,clipped=c.lab_to_rgb(np.array([[[60,200,-200]]]))
    assert clipped.all() and result.dtype==np.uint8


def test_masks_match_material_ownership_and_proven_seam():
    _,_,g=fixture()
    mask,padded,seams,other,held=c.geometry_masks(g,64,BOXES)
    assert len(seams)==1
    assert not np.any(padded&other) and not np.any(padded&held)
    assert np.any(mask) and np.all(padded[mask])
    assert seams[0]['body']==([.05,.1],[.45,.1])


@pytest.mark.parametrize("variant",list(c.VARIANTS))
def test_color_trial_reduces_cast_preserves_face_alpha_other_materials_and_ink(variant):
    ref,raw,g=fixture()
    out,report,masks,seams=c.correct(ref,raw,g,BOXES,variant,64)
    assert all(report['checks'].values()) and report['seam_edges']==1
    a,b,r=np.asarray(out),np.asarray(raw),np.asarray(ref)
    assert np.array_equal(a[...,3],b[...,3])
    assert np.array_equal(a[:128,128:],b[:128,128:])
    assert np.array_equal(a[190:,190:],b[190:,190:])
    assert np.array_equal(a[140:155:2,35:90,:3],b[140:155:2,35:90,:3])
    before=c.rgb_to_lab(b[95:115,45:90,:3])-c.rgb_to_lab(r[95:115,45:90,:3])
    after=c.rgb_to_lab(a[95:115,45:90,:3])-c.rgb_to_lab(r[95:115,45:90,:3])
    assert abs(np.mean(after[...,2]))<abs(np.mean(before[...,2]))*.65
    if variant=='gentle':assert np.max(abs(c.rgb_to_lab(a[95:115,45:90,:3])[...,0]-c.rgb_to_lab(b[95:115,45:90,:3])[...,0]))<.5
    guard=np.asarray(masks['seam_guard'])==255
    assert np.array_equal(a[guard],r[guard])


def test_box_blur_keeps_dimensions_and_weighted_constant_field():
    a=np.zeros((20,30,3));a[3:17,4:26]=[2,3,4]
    mask=np.any(a,axis=-1).astype(float)
    values=c.box_blur(a,3)/np.maximum(c.box_blur(mask,3)[...,None],1e-10)
    assert values.shape==a.shape
    assert np.allclose(values[mask>0],[2,3,4])


@pytest.mark.parametrize('damage',['alpha','face','seam','shape'])
def test_refuse_incompatible_inputs(damage):
    ref,raw,g=fixture()
    if damage=='alpha':
        a=np.array(raw);a[0,0,3]^=1;raw=Image.fromarray(a)
    elif damage=='face':
        a=np.array(raw);a[0,140,0]^=1;raw=Image.fromarray(a)
    elif damage=='seam':g['meshes'][1]['positions'][0][0]=10
    else:raw=raw.resize((128,128))
    with pytest.raises(ValueError):c.correct(ref,raw,g,BOXES,'gentle',64)


def test_cli_writes_reproducible_receipts_and_refuses_reuse_or_bad_hash(tmp_path):
    ref,raw,g=fixture()
    inputs={'reference':tmp_path/'ref.png','parent':tmp_path/'raw.png','geometry':tmp_path/'g.json'}
    ref.save(inputs['reference']);raw.save(inputs['parent']);inputs['geometry'].write_text(json.dumps(g))
    args=[sys.executable,'-m','defjam_tools.color_trial','--reference',str(inputs['reference']),'--parent-image',str(inputs['parent']),'--geometry',str(inputs['geometry']),'--output',str(tmp_path/'trial'),'--parent-id','r-source','--asset-id','synthetic','--source-size','64','--protect-region','0.5,0,0.5,0.5']
    for name,path in inputs.items():args+=['--'+name+'-sha256',hashlib.sha256(path.read_bytes()).hexdigest()]
    result=subprocess.run(args,capture_output=True,text=True)
    assert result.returncode==0,result.stderr
    receipt=json.loads((tmp_path/'trial/receipt.json').read_text())
    assert len(receipt['outputs'])==2
    for report in receipt['outputs']:
        assert report['sha256']==hashlib.sha256((tmp_path/'trial'/report['file']).read_bytes()).hexdigest()
        assert all(report['checks'].values())
    retry=subprocess.run(args,capture_output=True,text=True)
    assert retry.returncode!=0 and 'new directory' in retry.stderr
    args[args.index(str(tmp_path/'trial'))]=str(tmp_path/'other')
    args[-1]='0'*64
    bad=subprocess.run(args,capture_output=True,text=True)
    assert bad.returncode!=0 and 'checksum' in bad.stderr
    assert not (tmp_path/'other').exists()


def test_explicit_neck_region_excludes_other_welded_skin_edges():
    _,_,g=fixture()
    g['bounds']=[[0,0,0],[1,2,1]]
    assert len(c.geometry_masks(g,64,BOXES,[.4,.6],.26)[2])==1
    assert len(c.geometry_masks(g,64,BOXES,[.7,.9],.26)[2])==0
    assert len(c.geometry_masks(g,64,BOXES,[.4,.6],.1)[2])==0
