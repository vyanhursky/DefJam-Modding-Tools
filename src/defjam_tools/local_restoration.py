"""Source-palette assembly for locally inferred RGB super-resolution studies.

Keep the own Faithful alpha/protected pixels, low-frequency shading and chroma.
Only bounded, high-frequency luminance differences from a pinned local model
are adopted. This does not recover unknown lettering or verify game materials.
"""
import numpy as np
from PIL import Image

from .color_trial import rgb_to_lab, lab_to_rgb, box_blur, seam_guard

VERSION = 2


def assemble(faithful, inferred, source_size, held_source_boxes=(), seams=(),
             limit=6., strength=.85):
    if (faithful.mode != 'RGBA' or faithful.width != faithful.height
            or type(source_size) is not int or source_size < 8
            or faithful.width % source_size or inferred.size != faithful.size):
        raise ValueError('Use registered square references at integer source scale')
    if not 0 < limit <= 8 or not 0 < strength <= 1:
        raise ValueError('Invalid bounded local-detail settings')
    scale = faithful.width // source_size
    own = np.asarray(faithful)
    held = np.zeros(own.shape[:2], bool)
    for box in held_source_boxes:
        if (len(box) != 4 or any(type(v) is not int for v in box)
                or not 0 <= box[0] < box[2] <= source_size
                or not 0 <= box[1] < box[3] <= source_size):
            raise ValueError('Protected box outside native source')
        x0, y0, x1, y1 = (v * scale for v in box)
        held[y0:y1, x0:x1] = True
    base = rgb_to_lab(own[..., :3])
    local = rgb_to_lab(np.asarray(inferred.convert('RGB')))
    delta = local[..., 0] - base[..., 0]
    # Reject broad model brightness changes and all inferred chroma. Preserve
    # low-frequency painted shading rather than making skin/clothes brighter.
    radius = 2 * scale
    padded = np.pad(delta, radius, mode='edge')
    smooth = box_blur(padded, radius)[radius:-radius, radius:-radius]
    detail = np.clip(delta - smooth, -limit, limit)
    detail[np.abs(detail) < 1e-9] = 0
    guard = seam_guard(faithful.width, seams, inner=.75 * scale,
                       outer=3 * scale)
    weight = (1 - guard) * ~held * strength
    active = (weight > 0) & (detail != 0)
    adjusted = base.copy()
    adjusted[..., 0] += detail * weight
    rgb, gamut = lab_to_rgb(adjusted)
    result = own.copy()
    result[active, :3] = rgb[active]
    assert np.array_equal(result[..., 3], own[..., 3])
    assert np.array_equal(result[held], own[held])
    assert np.array_equal(result[~active], own[~active])
    changed = np.any(result[..., :3] != own[..., :3], axis=-1)
    if not changed.any():
        raise ValueError('No local detail survived protected assembly')
    drift = rgb_to_lab(result[..., :3]) - base
    report = dict(version=VERSION, source_size=source_size, scale=scale,
        method='local model fine luminance + own Faithful chroma/shading',
        detail_limit_L=limit, strength=strength, seam_edges=len(seams),
        seam_inner_native=.75, seam_outer_native=3,
        changed_pixels=int(changed.sum()), gamut_clipped_pixels=int((gamut & active).sum()),
        median_Lab_drift=np.median(drift[active], axis=0).tolist(),
        p95_absolute_Lab_drift=np.percentile(np.abs(drift[active]), 95, axis=0).tolist(),
        held_source_boxes=[list(b) for b in held_source_boxes],
        checks=dict(own_alpha_exact=True, own_held_RGBA_exact=True,
                    outside_active_RGBA_exact=True),
        imagegen_calls=0, approved=False, selected=False, game_verified=False)
    return Image.fromarray(result), report, dict(held=held, active=active,
        seam_core=guard >= 1 - 1e-10)
