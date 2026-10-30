#!/usr/bin/env python3
"""Assemble one private registered supplemental texture from an immutable plan.

No imports, reviews, approvals, source-model edits or runtime emulation. The
output directory must be new. Run with PYTHONPATH=src from the tools checkout.
"""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw
from defjam_tools import damage_detail, color_trial
from defjam_tools.paths import require_private_output


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--plan', required=True, type=Path)
    ap.add_argument('--key', required=True)
    ap.add_argument('--output', required=True, type=Path)
    args = ap.parse_args()
    plan = json.loads(args.plan.read_text())
    row = next(r for r in plan['textures'] if r['key'] == args.key)
    out = require_private_output(args.output)
    if out.exists():
        ap.error('Use a new immutable output stage')
    for path, expected in [(row['original_path'], row['original_sha256']),
            (row['faithful_path'], row['faithful_sha256']),
            (row['main_original_path'], row['main_original_sha256']),
            (row['main_faithful_path'], row['main_faithful_sha256']),
            (row['main_revision_path'], row['main_revision_sha256'])]:
        if sha(path) != expected:
            raise ValueError('Pinned input changed')
    for source in row['inputs']:
        if sha(source['path']) != source['sha256']:
            raise ValueError('Submitted input changed')
    original = Image.open(row['original_path']).convert('RGBA')
    faithful = Image.open(row['faithful_path']).convert('RGBA')
    native_box = row['clean_head_source_box']
    if original.size != (256, 256) or faithful.size != (1024, 1024):
        raise ValueError('This audited recipe uses256 native /1024 final')
    clean = Image.open(row['main_original_path']).convert('RGBA').crop(native_box)
    box = [v * 4 for v in native_box]
    clean_faithful = Image.open(row['main_faithful_path']).convert('RGBA').crop(box)
    clean_restored = Image.open(row['main_revision_path']).convert('RGBA').crop(box)
    generated = Image.open(row['raw_path'])
    result, report, masks = damage_detail.restore(original, clean, faithful,
        clean_faithful, clean_restored, generated,
        held_source_boxes=[h['box'] for h in row['source_holds']])
    out.mkdir(parents=True)
    result.save(out / 'texture.png', compress_level=3)
    masks['baseline'].save(out / 'continuity-baseline.png', compress_level=3)
    for key in ('source_support', 'transition', 'held', 'detail_active'):
        Image.fromarray(masks[key].astype('uint8') * 255).save(out / (key + '.png'))
    sheet = Image.new('RGB', (1536, 536), '#171717')
    draw = ImageDraw.Draw(sheet)
    for i, (title, image) in enumerate((('Original injury state', original),
            ('Clean restored reference', clean_restored), ('Restored injury draft', result))):
        draw.text((i * 512 + 8, 5), title, fill='white')
        sheet.paste(image.convert('RGB').resize((512, 512), Image.Resampling.LANCZOS),
                    (i * 512, 24))
    sheet.save(out / 'comparison.png')
    # Inspect the actual source-difference extent, not an invented facial mask.
    yy, xx = np.where(masks['source_support'])
    extent = [int(xx.min()), int(yy.min()), int(xx.max()) + 1, int(yy.max()) + 1]
    feature = Image.new('RGB', (1536, 536), '#171717')
    draw = ImageDraw.Draw(feature)
    for i, (title, image) in enumerate((('Source injury extent', faithful),
            ('Continuity baseline', masks['baseline']), ('Final bounded detail', result))):
        draw.text((i * 512 + 8, 5), title, fill='white')
        tile = image.convert('RGB').crop(extent)
        tile.thumbnail((512, 512))
        feature.paste(tile, (i * 512, 24))
    feature.save(out / 'injury-detail.png')
    processors = [Path(__file__), Path(damage_detail.__file__), Path(color_trial.__file__)]
    receipt = dict(schema=1, key=row['key'], fighter=row['fighter'],
        slot=row['slot_name'], source_id=row['source_id'],
        plan_sha256=sha(args.plan), original_sha256=row['original_sha256'],
        faithful_sha256=row['faithful_sha256'],
        main_source_id=row['main_source_id'], clean_reference_revision=row['main_revision'],
        clean_reference_sha256=row['main_revision_sha256'],
        raw_sha256=sha(row['raw_path']), raw_size=list(generated.size),
        output_sha256=sha(out / 'texture.png'), output_size=list(result.size),
        assembly=report, named_features=row['named_features'],
        source_holds=row['source_holds'], injury_extent_HD=extent,
        processor_hashes={p.name: sha(p) for p in processors},
        approved=False, selected=False, game_verified=False,
        preview='2D source-bound supplemental atlas; runtime transition unverified')
    (out / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(dict(key=row['key'], sha256=receipt['output_sha256'],
        clipped=report['baseline_clipped_pixels'], detail=report['generated_detail_pixels'])))


if __name__ == '__main__':
    main()
