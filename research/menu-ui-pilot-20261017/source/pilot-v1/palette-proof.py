"""Private technical assembly experiment for approved menu color constraints.

Imagegen supplies the art draft. This derivative permits only bounded fine
luminance changes against faithful HD; original spatial chroma, low-frequency
lighting, protected graphics, seam guards, alpha and padding remain authoritative.
Not an authoring-core change, pack installer, approval or evidence of lost detail.
"""
from pathlib import Path
import hashlib
import json
import numpy as np
from PIL import Image
from defjam_tools.color_trial import rgb_to_lab, lab_to_rgb, box_blur

ROOT = Path(__file__).resolve().parent
MAX_DETAIL_L = 1.0
DETAIL_STRENGTH = .25
SCALE = 4


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build(label, source_width, seam_x, visible_height, protected_boxes):
    baseline_path = ROOT / (label + '-faithful.png')
    raw_path = ROOT / (label + '-raw-v2.png')
    original = Image.open(baseline_path).convert('RGBA')
    target = original.size
    with Image.open(raw_path) as raw_image:
        raw_size = raw_image.size
        # Explicit trial-only normalization, retained in the receipt. The live
        # workshop's strict original-aspect import contract is unchanged.
        generated = raw_image.convert('RGB').resize(target, Image.Resampling.LANCZOS)
    rgb = np.array(original)[:, :, :3]
    alpha = np.array(original)[:, :, 3]
    source_lab = rgb_to_lab(rgb)
    draft_lab = rgb_to_lab(np.array(generated))
    source_l = source_lab[:, :, 0]
    draft_l = draft_lab[:, :, 0]
    source_fine = source_l - box_blur(source_l, 2 * SCALE)
    draft_fine = draft_l - box_blur(draft_l, 2 * SCALE)
    detail = np.clip((draft_fine - source_fine) * DETAIL_STRENGTH,
                     -MAX_DETAIL_L, MAX_DETAIL_L)
    # Smooth transition into held pixels avoids hard derivative-mask edges.
    held = np.zeros(rgb.shape[:2], dtype=bool)
    held[:4*SCALE, :] = True
    held[:, :4*SCALE] = True
    held[:, -4*SCALE:] = True
    held[visible_height*SCALE:, :] = True
    held[:, (seam_x-4)*SCALE:(seam_x+4)*SCALE] = True
    for x, y, w, h in protected_boxes:
        held[y*SCALE:(y+h)*SCALE, x*SCALE:(x+w)*SCALE] = True
    held |= (rgb.max(axis=2) <= 16) | (alpha == 0)
    allowed = box_blur((~held).astype(float), SCALE) * (~held)
    result_lab = source_lab.copy()
    result_lab[:, :, 0] = source_l + detail * allowed
    # All a*/b* values are copied at corresponding coordinates from faithful HD.
    assert np.array_equal(result_lab[:, :, 1:], source_lab[:, :, 1:])
    result, clipped = lab_to_rgb(result_lab)
    result[held | clipped] = rgb[held | clipped]
    output = np.dstack([result, alpha])
    out_path = ROOT / (label + '-palette-constrained-trial.png')
    Image.fromarray(output).save(out_path)
    mask_path = ROOT / (label + '-protected-mask.png')
    Image.fromarray((held * 255).astype(np.uint8)).save(mask_path)
    assert np.array_equal(output[:, :, 3], alpha)
    assert np.array_equal(result[held], rgb[held])
    delta = rgb_to_lab(result) - source_lab
    visible = rgb.max(axis=2) > 16
    median = np.median(delta[visible], axis=0)
    mean = np.mean(delta[visible], axis=0)
    assert abs(median[1]) < .1 and abs(median[2]) < .1
    assert abs(mean[1]) < .1 and abs(mean[2]) < .1
    assert np.max(abs(delta[:, :, 0])) <= MAX_DETAIL_L + .5
    return dict(label=label, output=out_path.name, output_sha256=sha(out_path),
                baseline=baseline_path.name, baseline_sha256=sha(baseline_path),
                raw=raw_path.name, raw_sha256=sha(raw_path), raw_size=raw_size,
                target_size=target, original_source_size=[source_width, 512],
                normalization='Explicit full-canvas RGB resize for this trial; raw retained. Not a changed importer contract.',
                algorithm='Original per-pixel Lab a/b; faithful L plus bounded 25% fine-detail difference, radius8px at4x; no broad color/lighting transfer.',
                max_detail_L=MAX_DETAIL_L, detail_strength=DETAIL_STRENGTH,
                protected_boxes_source=protected_boxes, seam_guard_source=[seam_x-4,seam_x+4],
                mask=mask_path.name, mask_sha256=sha(mask_path), held_pixels=int(held.sum()),
                visible_texels=int(visible.sum()), median_Lab_drift=median.tolist(),
                mean_Lab_drift=mean.tolist(), p95_absolute_Lab=np.percentile(abs(delta[visible]),95,axis=0).tolist(),
                max_absolute_Lab=np.max(abs(delta.reshape(-1,3)),axis=0).tolist(),
                protected_pixels='byte-identical', alpha='byte-identical',
                status='Unapproved technical trial; not imported, selected or installed')


if __name__ == '__main__':
    records = []
    for args in [('title-skyline',640,512,450,[]),
                 ('mode-wall-dark',320,256,480,[[0,108,272,300]])]:
        row = build(*args)
        records.append(row)
        print(row['label'], 'median Lab', row['median_Lab_drift'], flush=True)
    receipt = dict(schema=1, processor_sha256=sha(Path(__file__)), records=records,
                   note='Technical derivatives of retained built-in imagegen outputs, under owner-approved protected-pixel/color assembly plan. These do not assert reconstructed authentic detail.')
    (ROOT/'palette-proof-receipt.json').write_text(json.dumps(receipt,indent=2))
