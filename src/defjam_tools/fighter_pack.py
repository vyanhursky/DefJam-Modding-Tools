"""Offline Fighter Mod Support authoring; validation uses the matching recomp.

Never installs a pack or changes a game/profile. Keep the recomp checkout and
game dump explicit: the runtime is the authority for its evolving data formats.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import zipfile

PROTOCOL = 'fighter-authoring-api-1'
SCHEMA = 'fighter-registry-draft-1'


def ordinary(path):
    path = Path(path).absolute()
    if any(p.is_symlink() or getattr(p, 'is_junction', lambda: False)() for p in (path, *path.parents)):
        raise ValueError('Refusing linked authoring input/output: ' + str(path))
    return path


def slug(value):
    if not isinstance(value, str) or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', value) or len(value) > 63:
        raise ValueError('Use an ID of at most 63 lowercase letters/digits separated by single hyphens')
    return value


def contract(recomp, game, command, packs=(), language=None):
    script = Path(recomp).resolve() / 'scripts/fighter-contract.py'
    if not script.is_file():
        raise ValueError('Choose the matching Fighter Mod Support recomp checkout (fighter-contract.py missing)')
    arguments = [sys.executable, str(script), command, '--game', str(Path(game).resolve())]
    for pack in packs:
        arguments += ['--pack', str(ordinary(pack))]
    if language:
        arguments += ['--language', str(ordinary(language))]
    result = subprocess.run(arguments, capture_output=True, text=True, timeout=600)
    if len(result.stdout) > 16 * 1024**2:
        raise ValueError('Runtime validation report exceeds budget')
    try:
        report = json.loads(result.stdout)
    except ValueError as error:
        raise ValueError('Runtime validator did not return a contract report: ' + result.stderr[-1500:]) from error
    if report.get('protocol') != PROTOCOL:
        raise ValueError('Unsupported runtime authoring protocol')
    if result.returncode or not report.get('ok'):
        raise ValueError(str(report.get('error', 'Runtime validation failed')))
    return report


def create(destination, identifier, fighters, donor, catalog):
    destination = ordinary(destination)
    slug(identifier)
    if destination.exists():
        raise ValueError('Starter destination already exists; choose a new folder')
    if donor not in {catalog['id'] + '/' + fighter['id'] for fighter in catalog['fighters']}:
        raise ValueError('Donor is not in the verified retail catalog')
    rows, seen = [], set()
    for entry in fighters:
        local, equals, name = entry.partition('=')
        slug(local)
        if (not equals or not name.strip() or len(name) > 96
                or any(not 32 <= ord(char) < 127 for char in name) or local in seen):
            raise ValueError('Each fighter needs a unique id=ASCII display name (maximum 96 characters)')
        seen.add(local)
        rows.append({'id': local, 'name': name, 'inherits': donor, 'components': {}})
    if not rows:
        raise ValueError('Add at least one fighter')
    manifest = dict(schema=SCHEMA, id=identifier, version='1.0.0', requires={},
                    resources=[], fighters=rows, overrides=[])
    destination.parent.mkdir(parents=True, exist_ok=True)
    # Exclusive output: no existing pack or workspace is replaced.
    destination.mkdir()
    (destination / 'fighters.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    return manifest


def package(folder, destination, report):
    """Package precisely the bytes validated by the runtime, with stable ZIP metadata."""
    folder, destination = ordinary(folder), ordinary(destination)
    if destination.exists() or destination.is_relative_to(folder):
        raise ValueError('Choose a new ZIP outside the source pack folder')
    if report.get('protocol') != PROTOCOL or not report.get('ok') or not report.get('native_compilation'):
        raise ValueError('Packaging requires successful native compilation')
    row = report['packs'][0]
    identifier = slug(row['id'])
    files = row['files']
    if {p.relative_to(folder).as_posix() for p in folder.rglob('*') if p.is_file()} != set(files):
        raise ValueError('Pack file population changed after validation')
    destination.parent.mkdir(parents=True, exist_ok=True)
    # The final path is created exclusively only after the complete ZIP is checked.
    with tempfile.TemporaryDirectory(prefix='.fighter-package-', dir=destination.parent) as temporary:
        stage = Path(temporary) / 'pack.zip'
        with zipfile.ZipFile(stage, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as output:
            for name, digest in sorted(files.items()):
                path = ordinary(folder / name)
                if not path.is_relative_to(folder) or not path.is_file() or path.stat().st_size > 64 * 1024**2:
                    raise ValueError('Invalid validated package path')
                data = path.read_bytes()
                if hashlib.sha256(data).hexdigest() != digest:
                    raise ValueError('Pack changed after validation: ' + name)
                info = zipfile.ZipInfo(identifier + '/' + name, (1980, 1, 1, 0, 0, 0))
                info.create_system = 3
                info.external_attr = 0o100644 << 16
                info.compress_type = zipfile.ZIP_DEFLATED
                output.writestr(info, data, compresslevel=9)
        with zipfile.ZipFile(stage) as archive:
            if archive.testzip() is not None:
                raise ValueError('ZIP readback failed')
        with destination.open('xb') as output, stage.open('rb') as source:
            try:
                import shutil
                shutil.copyfileobj(source, output)
                output.flush(); os.fsync(output.fileno())
            except BaseException:
                output.close(); destination.unlink()
                raise
    return {'archive': str(destination), 'sha256': hashlib.sha256(destination.read_bytes()).hexdigest(),
            'files': len(files), 'native_compilation': True, 'native_playtest': False}


def extract(archive, member, output):
    from .hd_assets import archive_entries, unpack_refpack, MAX_BLOB
    archive, output = ordinary(archive), ordinary(output)
    if archive.stat().st_size > MAX_BLOB:
        raise ValueError('Archive exceeds extraction budget')
    matches = [data for name, data in archive_entries(archive.read_bytes()) if name == member]
    if len(matches) != 1:
        raise ValueError('Expected one exact archive member name')
    data = matches[0]
    if len(data) >= 2 and int.from_bytes(data[:2], 'big') & 0x3eff == 0x10fb:
        data = unpack_refpack(data)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open('xb') as stream:
        stream.write(data)
    return {'path': str(output), 'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    for name in ('catalog', 'new', 'validate', 'package'):
        command = sub.add_parser(name)
        command.add_argument('--recomp', type=Path, required=True)
        command.add_argument('--game', type=Path, required=True)
        if name == 'new':
            command.add_argument('--out', type=Path, required=True)
            command.add_argument('--id', required=True)
            command.add_argument('--donor', required=True)
            command.add_argument('--fighter', action='append', required=True, metavar='ID=NAME')
        if name in ('validate', 'package'):
            command.add_argument('folder', type=Path)
            command.add_argument('--with-pack', type=Path, action='append', default=[])
            command.add_argument('--language', type=Path)
        if name == 'package':
            command.add_argument('--out', type=Path, required=True)
    command = sub.add_parser('extract', help='Extract/decompress one exact BIG archive member to a new file')
    command.add_argument('--archive', type=Path, required=True)
    command.add_argument('--member', required=True)
    command.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.command == 'extract':
            result = extract(args.archive, args.member, args.out)
        elif args.command in ('catalog', 'new'):
            result = contract(args.recomp, args.game, 'catalog')
            if args.command == 'new':
                result = create(args.out, args.id, args.fighter, args.donor, result['baseline'])
        else:
            result = contract(args.recomp, args.game, 'validate', [args.folder, *args.with_pack], args.language)
            if args.command == 'package':
                result = package(args.folder, args.out, result)
        print(json.dumps(result, indent=2))
        return 0
    except (ValueError, OSError, KeyError, subprocess.TimeoutExpired) as error:
        parser.exit(1, str(error) + '\n')
