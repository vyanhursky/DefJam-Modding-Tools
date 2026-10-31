"""Private one-sided cloud bridge assembly of retained imagegen edits.

AI supplies the repaired cloud structure. A harmonic correction matches its
boundary to fixed surrounding pixels, preserving interior gradients rather
than blurring or feathering across the protected original4:3 center.
All prior masters/raw outputs remain unchanged. No approval or installation.
"""
from pathlib import Path
import hashlib
import json
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent
PARENT = ROOT.parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dst1(a, axis):
    """Unnormalized DST-I via an odd FFT extension (NumPy only)."""
    n = a.shape[axis]
    shape = list(a.shape)
    shape[axis] = 2*(n+1)
    extended = np.zeros(shape, dtype=np.float64)
    region = [slice(None)]*a.ndim
    region[axis] = slice(1,n+1)
    extended[tuple(region)] = a
    region[axis] = slice(n+2,None)
    extended[tuple(region)] = -np.flip(a,axis=axis)
    region[axis] = slice(1,n+1)
    return -np.fft.fft(extended,axis=axis).imag[tuple(region)]


def boundary_match(generated, fixed):
    """Solve harmonic correction for exact four-edge Dirichlet boundaries."""
    h,w,_ = generated.shape
    correction = np.zeros_like(generated,dtype=float)
    correction[0] = fixed[0]-generated[0]
    correction[-1] = fixed[-1]-generated[-1]
    correction[:,0] = fixed[:,0]-generated[:,0]
    correction[:,-1] = fixed[:,-1]-generated[:,-1]
    rhs = np.zeros((h-2,w-2,3))
    rhs[0] += correction[0,1:-1]
    rhs[-1] += correction[-1,1:-1]
    rhs[:,0] += correction[1:-1,0]
    rhs[:,-1] += correction[1:-1,-1]
    eigen = (4-2*np.cos(np.pi*np.arange(1,h-1)/(h-1))[:,None]
               -2*np.cos(np.pi*np.arange(1,w-1)/(w-1))[None,:])
    transformed = dst1(dst1(rhs,0),1)/eigen[:,:,None]
    correction[1:-1,1:-1] = dst1(dst1(transformed,0),1)/(4*(h-1)*(w-1))
    residual = (4*correction[1:-1,1:-1]-correction[:-2,1:-1]
                -correction[2:,1:-1]-correction[1:-1,:-2]-correction[1:-1,2:])
    assert np.max(abs(residual)) < 1e-8
    result = generated+correction
    assert np.allclose(result[0],fixed[0]) and np.allclose(result[-1],fixed[-1])
    assert np.allclose(result[:,0],fixed[:,0]) and np.allclose(result[:,-1],fixed[:,-1])
    return result, float(np.max(abs(residual)))


def check_solver():
    y,x = np.mgrid[:31,:41]
    known = np.stack([3*x+2*y,2*x-y,7+x+y],axis=-1).astype(float)
    ramp = np.zeros_like(known)
    result,_ = boundary_match(ramp,known)
    assert np.max(abs(result-known)) < 1e-8
    result,_ = boundary_match(known,known)
    assert np.array_equal(result,known)


if __name__ == '__main__':
    check_solver()
    old = np.array(Image.open(PARENT/'title-skyline-wide-master-draft.png').convert('RGB'))
    master = old.copy()
    mask = np.zeros(old.shape[:2],dtype=bool)
    records = []
    y0,y1 = 380,704
    for side,edge in [('left',1600),('right',3520)]:
        raw_path = ROOT/(side+'-bridge-raw.png')
        raw_image = Image.open(raw_path).convert('RGB')
        assert raw_image.size == (1536,1024), 'Do not silently rescale repair context'
        raw = np.asarray(raw_image,dtype=float)
        x0,x1 = (edge-384,edge) if side=='left' else (edge,edge+384)
        sx0,sx1 = (384,768) if side=='left' else (768,1152)
        proposal = raw[y0-256:y1-256,sx0:sx1].copy()
        fixed = old[y0:y1,x0:x1].astype(float)
        # Match normal slope into the exact source; no source pixel is edited.
        if side=='left':
            fixed[1:-1,-1] = np.clip(2*old[y0+1:y1-1,edge].astype(float)
                                      -old[y0+1:y1-1,edge+1],0,255)
        else:
            fixed[1:-1,0] = np.clip(2*old[y0+1:y1-1,edge-1].astype(float)
                                     -old[y0+1:y1-1,edge-2],0,255)
        matched,residual = boundary_match(proposal,fixed)
        master[y0:y1,x0:x1] = np.rint(matched).clip(0,255).astype(np.uint8)
        mask[y0:y1,x0:x1] = True
        # Guard top padding; only the defined generated-side domains may differ.
        before = abs(old[420:620,edge-1].astype(float)-old[420:620,edge].astype(float))
        after = abs(master[420:620,edge-1].astype(float)-master[420:620,edge].astype(float))
        records.append(dict(side=side,raw=raw_path.name,raw_sha256=sha(raw_path),
            domain=[x0,y0,x1-x0,y1-y0],harmonic_residual=residual,
            sky_roi_master_y=[420,620],before_edge_mean_rgb=float(before.mean()),
            after_edge_mean_rgb=float(after.mean()),
            note='Edge continuity is a diagnostic, not proof of cloud-structure quality.'))
    assert np.array_equal(master[:,1600:3520],old[:,1600:3520])
    assert np.array_equal(master[~mask],old[~mask])
    Image.fromarray(master).save(ROOT/'title-skyline-wide-master-refined.png')
    Image.fromarray(mask.astype(np.uint8)*255).save(ROOT/'edit-domain.png')
    for side,edge in [('left',1600),('right',3520)]:
        Image.fromarray(master).crop((edge-384,350,edge+384,800)).save(ROOT/(side+'-refined-close.png'))
    stage = Image.new('RGB',(5120,1440))
    stage.paste(Image.fromarray(master).crop((0,402,5120,1350)),(0,0))
    outputs = {}
    original_center = Image.open(PARENT/'title-skyline-4x3-layer-preview.png').convert('RGB')
    for ratio,width in [('4x3',1920),('16x10',2304),('16x9',2560),('21x9',3360),('32x9',5120)]:
        x=(5120-width)//2
        frame=stage.crop((x,0,x+width,1440))
        assert np.array_equal(np.array(frame.crop(((width-1920)//2,0,(width+1920)//2,1440))),np.array(original_center))
        path=ROOT/('title-skyline-'+ratio+'-refined.png')
        frame.save(path)
        outputs[ratio]=dict(path=path.name,sha256=sha(path))
    receipt=dict(schema=1,processor_sha256=sha(Path(__file__)),
        parent_master_sha256=sha(PARENT/'title-skyline-wide-master-draft.png'),
        refined_master_sha256=sha(ROOT/'title-skyline-wide-master-refined.png'),
        records=records,center='byte-identical',outside_edit_domains='byte-identical',
        aspect_center_checks='5/5 pass',solver_checks='linear harmonic ramp and identity pass',
        outputs=outputs,status='unapproved art refinement; no import/selection/install')
    (ROOT/'assembly-receipt.json').write_text(json.dumps(receipt,indent=2))
    print(json.dumps(records,indent=2))
