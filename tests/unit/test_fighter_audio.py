"""Synthetic audio containers; no game data or external decoder needed."""
import struct

import pytest

from defjam_tools.fighter_audio import bank_entries, prepare_r2, stream_span


def chunk(tag, payload):
    return tag + struct.pack('<I', len(payload) + 8) + payload


def stream(counts=(28, 25), *, declared=None):
    props = b'PT\x07\0\x06\x01\x65\xfd\x80\x01\x03\x85\x04'
    props += struct.pack('>I', sum(counts) if declared is None else declared) + b'\xa0\x01\x0a\xff'
    return (chunk(b'SCHl', props) + chunk(b'SCCl', struct.pack('<I', len(counts)))
            + b''.join(chunk(b'SCDl', struct.pack('<II', count, 0) + bytes(15 * ((count + 27) // 28)))
                       for count in counts) + chunk(b'SCEl', b''))


def test_partial_tail_is_decoded_then_trimmed_without_changing_source():
    data = stream()
    staged, report = prepare_r2(data)
    assert report == {'sample_rate': 24000, 'sample_count': 53, 'packet_count': 2,
                      'decoded_tail_samples_to_trim': 3}
    assert data != staged and len(staged) == len(data) + 6
    assert b'\x84\x04\x00\x00\x5d\xc0' in staged
    assert prepare_r2(stream((28, 56)))[1]['decoded_tail_samples_to_trim'] == 0


@pytest.mark.parametrize('data, message', [
    (stream((27, 28)), 'Non-final partial'), (stream(declared=54), 'samples differ'),
    (stream().replace(b'\xa0\x01\x0a', b'\xa0\x01\x08'), 'Only revision 3'),
    (stream()[:-1], 'Truncated EA chunk header'), (stream() + b'not padding', 'nonzero padding'),
    (stream().replace(b'\x85\x04', b'\x85\x05'), 'property span'),
])
def test_malformed_and_unsupported_streams_fail(data, message):
    with pytest.raises(ValueError, match=message):
        prepare_r2(data)


@pytest.mark.parametrize('encoded', [b'\x80', b'\x80\x00', b'\x80\x00\x00'])
def test_native_negative_short_counts_are_not_positive_export_durations(encoded):
    data = stream()
    size, = struct.unpack_from('<I', data, 4)
    changed = bytearray(data.replace(b'\x85\x04' + struct.pack('>I', 53),
                                   bytes((0x85, len(encoded))) + encoded))
    struct.pack_into('<I', changed, 4, size + len(encoded) - 4)
    with pytest.raises(ValueError, match='bounded mono'):
        prepare_r2(bytes(changed))


def test_bank_preserves_logical_order_duplicates_and_accounts_for_unindexed_data():
    first, second = stream((28,)), stream((56,))
    data = first + bytes(256 - len(first)) + b'unreferenced' + bytes(256 - 12)
    data += second + bytes(256 - len(second))
    header = bytearray(24)
    header[4:8] = bytes((2, 3, 0, 0))
    struct.pack_into('<H', header, 8, 3)
    for ordinal, offset in enumerate((2, 0, 2)):
        struct.pack_into('>H', header, 12 + 4 * ordinal, offset)
    streams, report = bank_entries(bytes(header), data)
    assert streams == [second, first, second]
    assert report['source_offsets'] == [512, 0, 512]
    assert report['unindexed_gaps'][0]['nonzero']
    changed = bytearray(header)
    changed[2:4] = b'\x01\x02'
    assert bank_entries(bytes(changed), data)[1]['event_metadata_sha256'] == report['event_metadata_sha256']
    changed[14] = 1
    assert bank_entries(bytes(changed), data)[1]['event_metadata_sha256'] != report['event_metadata_sha256']


def test_stream_extraction_cannot_cross_next_bank_entry():
    data = stream()
    header = bytearray(16)
    header[5] = 1
    struct.pack_into('<H', header, 8, 1)
    with pytest.raises(ValueError, match='offsets exceed'):
        bank_entries(bytes(header), data)
    with pytest.raises(ValueError, match='bounded stream'):
        stream_span(data[:40], unindexed_tail=True)


def test_decode_requires_exact_population_and_mono_probe(tmp_path, monkeypatch):
    from defjam_tools.fighter_audio import decode_stream
    from types import SimpleNamespace
    def run(args, **kwargs):
        if args[0] == 'probe':
            return SimpleNamespace(returncode=0, stderr=b'', stdout=b'{"streams":[{"codec_name":"adpcm_ea_r2","sample_rate":"24000","channels":1}]}')
        (tmp_path / 'output.pcm').write_bytes(struct.pack('<56h', *range(56)))
        return SimpleNamespace(returncode=0)
    monkeypatch.setattr('defjam_tools.fighter_audio.subprocess.run', run)
    pcm, receipt = decode_stream(stream(), 'decode', 'probe', tmp_path)
    assert struct.unpack('<53h', pcm) == tuple(range(53))
    assert receipt['decoded_tail_samples_to_trim'] == 3
    def bad(args, **kwargs):
        result = run(args, **kwargs)
        if args[0] == 'decode':
            (tmp_path / 'output.pcm').write_bytes(bytes(104))
        return result
    monkeypatch.setattr('defjam_tools.fighter_audio.subprocess.run', bad)
    with pytest.raises(ValueError, match='population differs'):
        decode_stream(stream(), 'decode', 'probe', tmp_path)


def test_original_r2_export_preserves_exact_stream_and_refuses_existing_output(tmp_path):
    from defjam_tools.fighter_audio import export_audio
    source, destination = tmp_path / 'sound.asf', tmp_path / 'export'
    source.write_bytes(stream())
    report = export_audio(source, destination, encoding='ea-adpcm-r2')
    assert (destination / '000.bin').read_bytes() == stream()
    assert report['tools'] == {} and report['entries'][0]['format'] == 'ea-adpcm-r2'
    assert report['entries'][0]['sample_rate'] == 24000
    assert not report['runtime_ready']
    with pytest.raises(ValueError, match='already exists'):
        export_audio(source, destination, encoding='ea-adpcm-r2')


def voice_fixture(tmp_path):
    header = bytearray(16)
    struct.pack_into('<2H', header, 0, 1, 626)
    header[5] = 1
    struct.pack_into('<H', header, 8, 1)
    data = stream((28,))
    padded = data + bytes(256 - len(data))
    (tmp_path / 'character.hdr').write_bytes(header)
    (tmp_path / 'character.dat').write_bytes(padded)
    (tmp_path / 'line.asf').write_bytes(data)
    metadata = bank_entries(bytes(header), padded)[1]
    catalog = {'identity': 'fighter-voice-events-1', 'archive_sha256': 'a' * 64,
               'templates': [{'category': 'Character', 'template_voice': 504,
                              'entries': 1, 'event_identity': metadata['event_template_identity']}]}
    return tmp_path / 'character.hdr', tmp_path / 'line.asf', catalog


def test_voice_export_matches_event_templates_and_preserves_original_r2_and_absence(tmp_path, monkeypatch):
    import json
    from defjam_tools.fighter_audio import export_voice
    bank, line, catalog = voice_fixture(tmp_path)
    from defjam_tools.fighter_audio import digest
    calls = []
    def validate(recomp, game, command, *, voice_source):
        assert command == 'validate-voice'
        assert voice_source.is_file() and not (tmp_path / 'voice').exists()
        calls.append(command)
        return {'component_compilation': True, 'source_sha256': digest(voice_source.read_bytes())}
    monkeypatch.setattr('defjam_tools.fighter_pack.contract', validate)
    output = tmp_path / 'voice'
    report = export_voice({'Character': bank}, {'Taunts', 'Enviro'}, line, line, output, catalog, recomp=tmp_path, game=tmp_path)
    source = json.loads((output / 'voice-source.json').read_text())
    assert source['format'] == 'fighter-voice-4'
    assert source['banks']['Character']['template_voice'] == 504
    assert source['banks']['Character']['family'] == 1
    assert source['banks']['Taunts'] == source['banks']['Enviro'] == {'state': 'absent'}
    assert (output / 'audio/Character/000.bin').read_bytes() == line.read_bytes()
    assert not (output / 'audio/Taunts').exists()
    assert not report['native_compilation'] and not report['native_playtest']
    assert report['component_compilation'] and calls == ['validate-voice']
    with pytest.raises(ValueError, match='already exists'):
        export_voice({'Character': bank}, {'Taunts', 'Enviro'}, line, line, output, catalog, recomp=tmp_path, game=tmp_path)


@pytest.mark.parametrize('failure', ['missing', 'overlap', 'template', 'codec'])
def test_voice_export_preflights_without_creating_partial_output(tmp_path, failure):
    from defjam_tools.fighter_audio import export_voice
    bank, line, catalog = voice_fixture(tmp_path)
    banks, absent = {'Character': bank}, {'Taunts', 'Enviro'}
    if failure == 'missing':
        absent.remove('Taunts')
    elif failure == 'overlap':
        absent.add('Character')
    elif failure == 'template':
        catalog['templates'][0]['event_identity'] = 'b' * 64
    else:
        line.write_bytes(b'not an EA stream')
    with pytest.raises(ValueError):
        export_voice(banks, absent, line, line, tmp_path / 'output', catalog, recomp=tmp_path, game=tmp_path)
    assert not (tmp_path / 'output').exists()


def test_voice_export_runtime_rejection_never_publishes_the_staged_folder(tmp_path, monkeypatch):
    from defjam_tools.fighter_audio import export_voice
    bank, line, catalog = voice_fixture(tmp_path)
    def reject(*args, **kwargs):
        raise ValueError('Native predictor or expanded bank budget rejected')
    monkeypatch.setattr('defjam_tools.fighter_pack.contract', reject)
    with pytest.raises(ValueError, match='predictor'):
        export_voice({'Character': bank}, {'Taunts', 'Enviro'}, line, line, tmp_path / 'output', catalog,
                     recomp=tmp_path, game=tmp_path)
    assert not (tmp_path / 'output').exists()
