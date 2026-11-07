import hashlib
import json
from pathlib import Path
import struct
import zipfile

import pytest
from defjam_tools import fighter_pack as tool


def fixture(tmp_path):
    folder = tmp_path / 'source'
    catalog = {'id': 'retail', 'fighters': [{'id': 'ludacris'}]}
    tool.create(folder, 'example', ['first=First Fighter', 'second=Second Fighter'], 'retail/ludacris', catalog)
    files = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in folder.iterdir()}
    return folder, {'protocol': tool.PROTOCOL, 'ok': True, 'native_compilation': True,
                    'packs': [{'id': 'example', 'version': '1.0.0', 'files': files}]}


def test_package_exact_validated_bytes_deterministic_and_non_overwriting(tmp_path):
    folder, report = fixture(tmp_path)
    first = tool.package(folder, tmp_path / 'a.zip', report)
    second = tool.package(folder, tmp_path / 'b.zip', report)
    assert first['sha256'] == second['sha256']
    with zipfile.ZipFile(first['archive']) as archive:
        assert archive.namelist() == ['example/fighters.json']
        assert archive.read(archive.namelist()[0]) == (folder / 'fighters.json').read_bytes()
    with pytest.raises(ValueError, match='new ZIP'):
        tool.package(folder, tmp_path / 'a.zip', report)


@pytest.mark.parametrize('mutation', ['content', 'addition', 'deletion'])
def test_changes_after_validation_leave_no_archive(tmp_path, mutation):
    folder, report = fixture(tmp_path)
    if mutation == 'content':
        (folder / 'fighters.json').write_text('{}')
    elif mutation == 'addition':
        (folder / 'unreviewed.py').write_text('pass')
    else:
        (folder / 'fighters.json').unlink()
    with pytest.raises(ValueError, match='changed'):
        tool.package(folder, tmp_path / 'a.zip', report)
    assert not (tmp_path / 'a.zip').exists()


def test_validation_cannot_be_bypassed_by_failed_report(tmp_path):
    folder, report = fixture(tmp_path)
    report['ok'] = False
    with pytest.raises(ValueError, match='compilation'):
        tool.package(folder, tmp_path / 'a.zip', report)
    assert not (tmp_path / 'a.zip').exists()


def test_new_pack_preserves_existing_work_and_rejects_unknown_donor(tmp_path):
    folder, _ = fixture(tmp_path)
    before = (folder / 'fighters.json').read_bytes()
    with pytest.raises(ValueError, match='already exists'):
        tool.create(folder, 'example', ['first=One'], 'retail/ludacris', {})
    assert (folder / 'fighters.json').read_bytes() == before
    with pytest.raises(ValueError, match='Donor'):
        tool.create(tmp_path / 'bad', 'example', ['first=One'], 'retail/missing', {'id':'retail','fighters':[]})
    assert not (tmp_path / 'bad').exists()


@pytest.mark.parametrize('entry', ['river=River\nStone', 'river=\x7f', 'river=   '])
def test_starter_rejects_unrenderable_names_without_creating_output(tmp_path, entry):
    destination = tmp_path / 'invalid'
    with pytest.raises(ValueError, match='display name'):
        tool.create(destination, 'example', [entry], 'retail/ludacris',
                    {'id': 'retail', 'fighters': [{'id': 'ludacris'}]})
    assert not destination.exists()


def test_exact_member_extraction_never_uses_member_name_as_destination(tmp_path):
    data, name = b'synthetic data', b'../unsafe.bin\0'
    start = 16 + 8 + len(name)
    archive = tmp_path / 'input.viv'
    archive.write_bytes(b'BIGF' + struct.pack('>III', start + len(data), 1, start)
                        + struct.pack('>II', start, len(data)) + name + data)
    out = tmp_path / 'safe' / 'asset.bin'
    tool.extract(archive, '../unsafe.bin', out)
    assert out.read_bytes() == data
    with pytest.raises(FileExistsError):
        tool.extract(archive, '../unsafe.bin', out)
    assert not (tmp_path.parent / 'unsafe.bin').exists()


@pytest.mark.parametrize('prefix', [b'\x10\xfb\0\0\x04', b'\x11\xfb\0\0\x0d\0\0\x04'])
def test_extraction_decodes_refpack_with_optional_compressed_length(tmp_path, prefix):
    data, name = prefix + b'\xe0abcd\xfc', b'asset.bin\0'
    start = 24 + len(name)
    archive = tmp_path / 'compressed.viv'
    archive.write_bytes(b'BIGF' + struct.pack('>III', start + len(data), 1, start)
                        + struct.pack('>II', start, len(data)) + name + data)
    out = tmp_path / 'decoded.bin'
    receipt = tool.extract(archive, 'asset.bin', out)
    assert out.read_bytes() == b'abcd'
    assert receipt['sha256'] == hashlib.sha256(b'abcd').hexdigest()
