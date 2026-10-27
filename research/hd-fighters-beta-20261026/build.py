#!/usr/bin/env python3
"""Build the pinned HD Fighters beta without editing source PNGs or review state.

Artwork and all resulting artifacts must remain outside Git. This release recipe
only packages the explicit owner-authorized three-texture beta selection. It does
not approve art, regenerate images, update active settings or install into a game.
"""
import argparse
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import shutil
import stat
import sys
import zipfile

from PIL import Image
import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO / 'src'))
from defjam_tools.hd_assets import archive_entries, unpack_refpack, shpx_images
from defjam_tools.paths import require_private_output

PUBLIC = 'https://pub-9167b11f83f24f2a9e21af7f0e225057.r2.dev'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def module(name, path):
    sys.path.insert(0, str(path.parent))
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--workspace', type=Path, required=True)
    ap.add_argument('--dump', type=Path, required=True)
    ap.add_argument('--faithful-pack', type=Path, required=True)
    ap.add_argument('--helper', type=Path, required=True)
    ap.add_argument('--catalogue', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    out = require_private_output(args.output)
    if out.exists():
        ap.error('Use a new release output directory; existing artifacts are immutable')
    recipe = json.loads((HERE / 'selection.json').read_text(encoding='utf8'))
    review_raw = (args.workspace / 'workshop.json').read_bytes()
    state = json.loads(review_raw)
    archive_path = args.dump / 'assets/v2ip.viv'
    source_archive = archive_path.read_bytes()
    wanted = {row['source_member'].lower() for row in recipe['selections']}
    leaves = {name.lower(): raw for name, raw in archive_entries(source_archive) if name.lower() in wanted}
    if len(leaves) != 3:
        raise ValueError('Expected exactly three known fighter texture members')
    # Validate everything before creating the release directory.
    verified = []
    for chosen in recipe['selections']:
        aid = chosen['source_id']
        candidate = next(c for c in state['candidates'][aid] if c['id'] == chosen['revision'])
        source = args.workspace / candidate['path']
        if not source.resolve().is_relative_to(args.workspace.resolve()):
            raise ValueError('Candidate path escaped the private workspace')
        if sha(source) != chosen['sha256'] or candidate['sha256'] != chosen['sha256']:
            raise ValueError('Candidate checksum changed: ' + chosen['fighter'])
        baseline = args.faithful_pack / 'textures' / (aid + '.png')
        if sha(baseline) != chosen['baseline_sha256']:
            raise ValueError('Faithful baseline checksum changed')
        rows = list(shpx_images(unpack_refpack(leaves[chosen['source_member'].lower()]), indices={0}))
        if len(rows) != 1 or rows[0][0].get('source_id') != aid or rows[0][0].get('width') != 512 or rows[0][0].get('height') != 512:
            raise ValueError('Dump/source texture identity mismatch')
        if rows[0][0]['nv2a_format'] != 0x0b or rows[0][0]['palette_entries'] != 256:
            raise ValueError('Unexpected source identity descriptor')
        with Image.open(source) as image, Image.open(baseline) as original:
            if image.format != 'PNG' or image.mode != 'RGBA' or image.size != (2048, 2048):
                raise ValueError('Expected single 4x RGBA PNG')
            if getattr(image, 'n_frames', 1) != 1:
                raise ValueError('Animated PNG is unsupported')
            image.load(); original.load()
            a = np.asarray(image); b = np.asarray(original.convert('RGBA'))
            if not np.array_equal(a[..., 3], b[..., 3]):
                raise ValueError('Material alpha changed')
            for x0, y0, x1, y1 in chosen['protected_pixel_boxes']:
                if not np.array_equal(a[y0:y1, x0:x1], b[y0:y1, x0:x1]):
                    raise ValueError('Protected face pixels changed')
        verified.append(dict(chosen, source_path=source, decoded_id=rows[0][0]['decoded_id'],
            nv2a_format=0x0b, palette_entries=256, source_width=512, source_height=512,
            source_identity_verified=True, alpha_exact=True, protected_face_exact=True))
    out.mkdir(parents=True)
    root = 'hd-fighters-v0-1-0-beta-1'
    pack = out / root
    (pack / 'textures').mkdir(parents=True)
    manifest = '[pack]\nschema=1\nname=' + recipe['display_name'] + '\npng_mips=channels\n[textures]\n'
    for item in verified:
        aid = item['source_id']
        shutil.copyfile(item['source_path'], pack / 'textures' / (aid + '.png'))
        manifest += aid + '=textures/' + aid + '.png\n'
    (pack / 'manifest.ini').write_text(manifest, encoding='ascii')
    notes = '''HD Fighters 0.1 (beta) / 0.1.0-beta.1

First three-fighter texture pilot: Blaze and Nyne Rich Original Detail v1;
Trejo Rich Original Detail v4 with Source palette skin/neck correction.
Three 2048x2048 main-outfit atlases. Original face regions and all material
alpha are preserved. Alternate outfits, portraits, menus and other fighters
are not replaced. There are no model, gameplay or executable changes.

Beta for playtesting. Tattoo/lettering fidelity and Blaze/Nyne skin tint remain
under review. Owner Trejo in-game acceptance is pending. This release is not a
claim that all fighter textures are complete or approved.

Install in Def Jam Recompiled 0.12.1 or later: Mods > Show testing versions >
Refresh catalogue > HD Fighters > Install. Then enable HD Fighters in Load Order
AFTER optional Faithful HD packs and restart the game. Faithful HD is optional.
HD Widescreen Menus is separate and can remain enabled. Installation does not
automatically enable this pack. To remove, disable/remove HD Fighters in Mods.

Credits: vyanhursky; AI-assisted restoration of the user's own game textures.
Derived game artwork; rights remain with their respective owners. The project
source MIT licence does not cover the artwork. No game executable or disc data
is included. New revisions will have a new immutable version and hash.
'''
    (pack / 'README.txt').write_text(notes, encoding='utf8')
    receipt = {k: recipe[k] for k in ('schema', 'id', 'name', 'display_name', 'version', 'channel', 'min_recomp', 'publication_authorized', 'status')}
    receipt.update(png_mips='channels', textures=[{k: v for k, v in item.items() if k != 'source_path'} for item in verified],
        aliases=[], art_review_state_modified=False, game_verified=False,
        recipe_sha256=sha(HERE / 'selection.json'), builder_sha256=sha(Path(__file__)),
        rights='Derived game artwork; original rights retained; source MIT licence does not cover artwork')
    (pack / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf8')
    archive = out / 'hd-fighters-v0.1.0-beta.1.zip'
    with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=1) as bundle:
        for file in sorted(p for p in pack.rglob('*') if p.is_file()):
            info = zipfile.ZipInfo(root + '/' + file.relative_to(pack).as_posix(), date_time=(2026, 10, 26, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = (stat.S_IFREG | 0o644) << 16
            bundle.writestr(info, file.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=1)
    with zipfile.ZipFile(archive) as bundle:
        if bundle.testzip() is not None:
            raise ValueError('ZIP CRC check failed')
        files = bundle.infolist()
    digest = sha(archive)
    descriptor = dict(size=archive.stat().st_size, unpacked_size=sum(i.file_size for i in files),
        file_count=len(files), sha256=digest, root=root,
        urls=[PUBLIC + '/hd-fighters/' + recipe['version'] + '/' + digest + '/' + archive.name])
    helper = module('released_hd_fighters_mods', args.helper / 'setup/mods.py')
    installed = helper.unpack_archive(archive, descriptor, out / 'released-installer-validation')
    catalogue = module('catalogue_hd_fighters_pack_check', args.catalogue / 'tools/package_check.py')
    checked = catalogue.unpack_archive(archive, descriptor, out / 'catalogue-installer-validation')
    expected = {row['source_id'] for row in verified}
    if set(installed['texture_ids']) != expected or set(checked['texture_ids']) != expected:
        raise ValueError('Installer manifest IDs differ')
    if installed['capabilities'] != ['textures-v1'] or checked['capabilities'] != ['textures-v1']:
        raise ValueError('Unexpected runtime capability')
    if installed['files'] != checked['files'] or len(installed['files']) != 6:
        raise ValueError('Installer outputs differ')
    if (args.workspace / 'workshop.json').read_bytes() != review_raw:
        raise ValueError('Review state changed during build; retain output and inspect')
    plan = dict(profile='defjam-r2', endpoint='https://01e722513e8a17b02561c12731a3e4cb.r2.cloudflarestorage.com',
        bucket='defjam-ffny-mods', public_base=PUBLIC, prefix='hd-fighters/' + recipe['version'] + '/' + digest,
        filename=archive.name, local_zip=str(archive), sha256=digest, size=descriptor['size'])
    result = dict(id='hd-fighters', version=recipe['version'], archive=descriptor,
        textures=3, mappings=3, png_mips='channels', min_recomp=recipe['min_recomp'],
        source_identities_verified=True, original_candidate_bytes_exact=True,
        alpha_and_protected_faces_exact=True, reviews_unchanged=True,
        released_helper='DefJamFFNY-recomp v0.12.1 eeed26d4ae6871e78bcfae751437cb00e8b282a0',
        released_installer_validated=True, catalogue_validator_validated=True,
        installed_file_hashes=installed['files'], in_game_acceptance_pending=True)
    (out / 'artifact.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf8')
    (out / 'upload-plan.json').write_text(json.dumps(plan, indent=2) + '\n', encoding='utf8')
    (out / (archive.name + '.sha256')).write_text(digest + '  ' + archive.name + '\n', encoding='ascii')
    (out / 'RELEASE-NOTES.txt').write_text(notes, encoding='utf8')
    (out / 'workshop-before.json').write_bytes(review_raw)
    print(json.dumps({k: result[k] for k in ('id', 'version', 'archive', 'textures', 'mappings', 'reviews_unchanged', 'released_installer_validated', 'catalogue_validator_validated')}, indent=2))


if __name__ == '__main__':
    main()
