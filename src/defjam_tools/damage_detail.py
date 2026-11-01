"""Restore registered supplemental head textures without adopting new injuries.

Reuse an exact clean-restoration crop, add the original state's signed RGB
difference, then transfer bounded generated luminance detail only inside source
change support. This is an offline art recipe, not runtime shader emulation.
Each state's own faithful alpha and explicitly held tiles remain exact.
"""
import numpy as np
from PIL import Image, ImageFilter

from .color_trial import rgb_to_lab, lab_to_rgb, box_blur

VERSION = 2


def restore(original, clean_original, faithful, clean_faithful, clean_restored,
            generated, held_source_boxes=(), detail_limit=3., strength=.8,
            registration_rgb_tolerance=0):
    if (original.mode != 'RGBA' or clean_original.mode != 'RGBA'
            or original.size != clean_original.size
            or original.width != original.height or original.width < 8):
        raise ValueError('Use equal square native RGBA head crops')
    if (any(im.mode != 'RGBA' or im.size != faithful.size
            for im in (faithful, clean_faithful, clean_restored))
            or faithful.width != faithful.height
            or faithful.width % original.width):
        raise ValueError('Use equal RGBA reference crops at integer source scale')
    if (abs(generated.width / generated.height - 1) > .005
            or not 0 < detail_limit <= 4 or not 0 < strength <= 1):
        raise ValueError('Invalid generated framing or bounded-detail parameters')
    src, clean = np.asarray(original), np.asarray(clean_original)
    native = np.any(src[..., :3] != clean[..., :3], axis=-1)
    unchanged = float((~native).mean())
    if type(registration_rgb_tolerance) is not int or not 0 <= registration_rgb_tolerance <= 3:
        raise ValueError('Registration RGB tolerance must be an integer from 0 to 3')
    # The opt-in gate recognizes audited palette quantization only. Literal
    # RGB inequality above still defines every original changed source texel.
    close = np.max(np.abs(src[..., :3].astype(int) - clean[..., :3].astype(int)),
                   axis=-1) <= registration_rgb_tolerance
    close_fraction = float(close.mean())
    palette_registered = (registration_rgb_tolerance > 0 and unchanged >= .5 and close_fraction >= .8)
    if (unchanged < .75 and not palette_registered) or not native.any():
        raise ValueError('Head registration is unproven or state has no RGB changes')
    scale = faithful.width // original.width
    expand = lambda a: np.repeat(np.repeat(a, scale, axis=0), scale, axis=1)
    exact_support = expand(native)
    # Two native texels accommodate faithful enlargement interpolation. This is
    # a documented transition band, never permission to create new injury paths.
    band = expand(np.asarray(Image.fromarray(native.astype('uint8') * 255)
                             .filter(ImageFilter.MaxFilter(5))) > 0)
    held_native = np.zeros(native.shape, dtype=bool)
    for box in held_source_boxes:
        if (len(box) != 4 or any(type(v) != int for v in box)
                or not 0 <= box[0] < box[2] <= original.width
                or not 0 <= box[1] < box[3] <= original.height):
            raise ValueError('Held tile lies outside native head texture')
        x0, y0, x1, y1 = box
        held_native[y0:y1, x0:x1] = True
    held = expand(held_native)
    own, cf, restored = map(np.asarray, (faithful, clean_faithful, clean_restored))
    baseline = restored.copy()
    delta = own[..., :3].astype(float) - cf[..., :3].astype(float)
    candidate = restored[..., :3].astype(float) + delta
    clipped = np.any((candidate < 0) | (candidate > 255), axis=-1) & band & ~held
    baseline[band, :3] = np.rint(np.clip(candidate[band], 0, 255)).astype('uint8')
    baseline[held] = own[held]
    baseline[..., 3] = own[..., 3]
    raw = rgb_to_lab(np.asarray(generated.convert('RGB').resize(
        faithful.size, Image.Resampling.LANCZOS)))[..., 0]
    smooth = box_blur(box_blur(raw, max(1, round(scale * .75))),
                      max(1, round(scale * .75)))
    residual = np.clip(raw - smooth, -detail_limit, detail_limit)
    # Fade within the exact source support. No generated red/chroma or broad
    # new contours are copied; a raw output can invent marks that we reject.
    blur = np.asarray(Image.fromarray(exact_support.astype('uint8') * 255)
                      .filter(ImageFilter.GaussianBlur(scale * .5)), dtype=float) / 255
    weight = exact_support * ~held * np.clip((blur - .5) * 2, 0, 1) * strength
    active = weight > 0
    lab = rgb_to_lab(baseline[..., :3])
    lab[..., 0] += residual * weight
    rgb, gamut = lab_to_rgb(lab)
    out = baseline.copy()
    out[active, :3] = rgb[active]
    assert np.array_equal(out[..., 3], own[..., 3])
    assert np.array_equal(out[held], own[held])
    outside = ~band & ~held
    assert np.array_equal(out[outside, :3], restored[outside, :3])
    assert np.array_equal(out[~active], baseline[~active])
    changed_detail = np.any(out[..., :3] != baseline[..., :3], axis=-1)
    if not changed_detail.any():
        raise ValueError('No generated injury detail survived assembly')
    report = dict(version=VERSION, source_size=original.width, scale=scale,
        registration_unchanged_rgb_fraction=unchanged,
        registration_rgb_tolerance=registration_rgb_tolerance,
        registration_close_rgb_fraction=close_fraction,
        registration_method=("audited small-palette-difference crop" if unchanged < .75 else "exact RGB majority crop"),
        source_changed_pixels=int(native.sum()), transition_native_texels=2,
        baseline_clipped_pixels=int(clipped.sum()),
        baseline_clipped_fraction=float(clipped.sum() / max(1, (band & ~held).sum())),
        detail_limit_L=detail_limit, strength=strength,
        generated_detail_pixels=int(changed_detail.sum()),
        generated_gamut_clipped_pixels=int((gamut & active).sum()),
        generated_detail_active_pixels=int(active.sum()),
        held_source_boxes=[list(b) for b in held_source_boxes],
        checks=dict(own_alpha_exact=True, own_held_tiles_exact=True,
                    clean_rgb_outside_transition_exact=True,
                    generated_detail_outside_source_support_exact=True),
        method='registered clean detail + original state RGB delta + bounded generated luminance',
        runtime_binding_verified=False, visual_review_required=True)
    return Image.fromarray(out), report, dict(source_support=exact_support,
        transition=band, held=held, detail_active=active,
        baseline=Image.fromarray(baseline))
