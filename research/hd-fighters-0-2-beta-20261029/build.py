#!/usr/bin/env python3
"""Build the pinned HD Fighters beta without editing source PNGs or review state.

Artwork and all resulting artifacts must remain outside Git. This release recipe
only packages the explicit owner-authorized five-texture, owner-approved beta selection. It does
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
    if len(leaves) != len(recipe['selections']):
        raise ValueError('Expected the exact five known fighter texture members')
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
        r = state['reviews'].get(aid + ':' + chosen['revision'], {})
        if not (r.get('status') == 'approved' and r.get('face_reviewed') and r.get('channels_reviewed') and r.get('selected') and r.get('output_sha256') == chosen['sha256']):
            raise ValueError('Exact revision lacks complete release review: ' + chosen['fighter'])
        verified.append(dict(chosen, source_path=source, decoded_id=rows[0][0]['decoded_id'],
            nv2a_format=0x0b, palette_entries=256, source_width=512, source_height=512,
            source_identity_verified=True, alpha_exact=True, approved_face_revision_exact=True))
    out.mkdir(parents=True)
    root = 'hd-fighters-v0-2-0-beta-1'
    pack = out / root
    (pack / 'textures').mkdir(parents=True)
    manifest = '[pack]\nschema=1\nname=' + recipe['display_name'] + '\npng_mips=channels\n[textures]\n'
    for item in verified:
        aid = item['source_id']
        shutil.copyfile(item['source_path'], pack / 'textures' / (aid + '.png'))
        manifest += aid + '=textures/' + aid + '.png\n'
    (pack / 'manifest.ini').write_text(manifest, encoding='ascii')
    notes = """HD Fighters 0.2 (beta) / 0.2.0-beta.1

Five owner-approved 2048x2048 main-outfit restorations: Blaze, Nyne, Trejo,
Redman and Henry Rollins. Rich Original Detail includes restored faces, hair,
headwear, skin, tattoos, clothing and footwear; source palette matching keeps
skin and garments close to their original colors. All material alpha is exact
Faithful baseline alpha, with channel-preserving PNG mip generation.

These five exact model revisions were visually approved on 2026-10-29.
Native playtesting of this 0.2 release is pending. Alternate outfits, portraits,
menus and other fighters are not replaced. No model/gameplay/executable changes.
The next ten restoration drafts are excluded from this approved release.

Install in Def Jam Recompiled 0.12.1 or later: Mods > Show testing versions >
Refresh catalogue > HD Fighters > Install/Update. Enable HD Fighters in Load
Order AFTER optional Faithful HD packs and restart the game. Faithful HD is
optional; HD Widescreen Menus is separate. Installation does not auto-enable.
To remove, disable/remove HD Fighters in Mods. Previous 0.1 stays immutable.

Credits: vyanhursky; AI-assisted restoration of the user's own game textures.
Derived game artwork; rights remain with their respective owners. The project
source MIT licence does not cover artwork. No executable or disc data included.
"""
    (pack / 'README.txt').write_text(notes, encoding='utf8')
    receipt = {k: recipe[k] for k in ('schema', 'id', 'name', 'display_name', 'version', 'channel', 'min_recomp', 'publication_authorized', 'status')}
    receipt.update(png_mips='channels', textures=[{k: v for k, v in item.items() if k != 'source_path'} for item in verified],
        aliases=[], art_review_state_modified=False, game_verified=False,
        recipe_sha256=sha(HERE / 'selection.json'), builder_sha256=sha(Path(__file__)),
        rights='Derived game artwork; original rights retained; source MIT licence does not cover artwork')
    (pack / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf8')
    archive = out / 'hd-fighters-v0.2.0-beta.1.zip'
    with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=1) as bundle:
        for file in sorted(p for p in pack.rglob('*') if p.is_file()):
            info = zipfile.ZipInfo(root + '/' + file.relative_to(pack).as_posix(), date_time=(2026, 10, 29, 0, 0, 0))
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
    if installed['files'] != checked['files'] or len(installed['files']) != 8:
        raise ValueError('Installer outputs differ')
    if (args.workspace / 'workshop.json').read_bytes() != review_raw:
        raise ValueError('Review state changed during build; retain output and inspect')
    plan = dict(profile='defjam-r2', endpoint='https://01e722513e8a17b02561c12731a3e4cb.r2.cloudflarestorage.com',
        bucket='defjam-ffny-mods', public_base=PUBLIC, prefix='hd-fighters/' + recipe['version'] + '/' + digest,
        filename=archive.name, local_zip=str(archive), sha256=digest, size=descriptor['size'])
    result = dict(id='hd-fighters', version=recipe['version'], archive=descriptor,
        textures=5, mappings=5, png_mips='channels', min_recomp=recipe['min_recomp'],
        source_identities_verified=True, original_candidate_bytes_exact=True,
        alpha_and_approved_revision_bytes_exact=True, reviews_unchanged=True,
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
