"""Recover generated clothing detail excluded by an overly broad tile hold.

This is deterministic assembly of an existing imagegen patch. Rectangles only
bound the requested repair: source cloth triangles minus guarded other-material
coverage decide which pixels may change. It never imports or approves a draft.
"""
import numpy as np
from PIL import Image
from . import face_detail, material_palette

VERSION = 1


def repair(reference, parent, generated, geometry, patch_box, repair_boxes,
           source_size=512, strength=.8):
    if not isinstance(source_size, int) or not 8 <= source_size <= 2048:
        raise ValueError('Invalid source analysis size')
    if (reference.mode != 'RGBA' or parent.mode != 'RGBA' or
            reference.size != parent.size or parent.width != parent.height or
            parent.width % source_size):
        raise ValueError('Use equal square RGBA atlases at an integer source scale')
    if not repair_boxes:
        raise ValueError('Specify the omitted clothing regions')
    x0, y0, x1, y1 = patch_box
    requested = np.zeros((parent.height, parent.width), dtype=bool)
    for a, b, c, d in repair_boxes:
        if not x0 <= a < c <= x1 or not y0 <= b < d <= y1:
            raise ValueError('Repair region must be inside the generated patch')
        requested[b:d, a:c] = True
    editable, _, _ = material_palette.clothing_mask(geometry, source_size)
    mask = np.asarray(Image.fromarray(editable).resize(parent.size, Image.Resampling.NEAREST)) & requested
    if not mask.any():
        raise ValueError('No safe clothing coverage in requested regions')
    detail, detail_report = face_detail.merge(reference, parent, generated,
                                             patch_box, strength=strength)
    matched, palette_report, _ = material_palette.match(reference, detail, geometry,
                                                       source_size=source_size)
    before = np.asarray(parent)
    out = before.copy()
    out[mask, :3] = np.asarray(matched)[mask, :3]
    changed = np.any(out[..., :3] != before[..., :3], axis=-1)
    checks = dict(alpha_exact=bool(np.array_equal(out[..., 3], before[..., 3])),
                  outside_repair_exact=bool(np.array_equal(out[~mask], before[~mask])))
    if not all(checks.values()):
        raise ValueError('Clothing repair invariant failed')
    report = dict(version=VERSION, patch_box=list(patch_box),
                  repair_boxes=[list(b) for b in repair_boxes], checks=checks,
                  safe_pixels=int(mask.sum()), changed_pixels=int(changed.sum()),
                  regions=[dict(box=list(b), safe_pixels=int(mask[b[1]:b[3], b[0]:b[2]].sum()),
                                changed_pixels=int(changed[b[1]:b[3], b[0]:b[2]].sum()))
                           for b in repair_boxes],
                  detail=detail_report, palette=palette_report,
                  visual_review_required=True)
    return Image.fromarray(out), report, Image.fromarray(mask.astype(np.uint8)*255)
