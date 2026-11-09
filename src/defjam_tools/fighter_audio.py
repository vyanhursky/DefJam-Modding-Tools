"""Offline, bounded EA R2 speech extraction to ordinary mono PCM16 WAV.

This does not admit native bank metadata or install a fighter. Event ordinals
and source hashes are recorded so the runtime's verified template contract can
be matched separately. FFmpeg is an explicitly supplied local tool, not bundled.
"""
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import tempfile
import wave

from .fighter_pack import ordinary

MAX_BANK = 64 * 1024**2
MAX_STREAM = 16 * 1024**2
MAX_SAMPLES = 4_000_000


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def read_bounded(path, limit):
    path = ordinary(path)
    require(path.is_file() and path.stat().st_size <= limit, 'Audio input exceeds its byte budget')
    with path.open('rb') as source:
        data = source.read(limit + 1)
    require(len(data) <= limit, 'Audio input grew beyond its byte budget')
    return data


def stream_span(data, *, unindexed_tail=False):
    """Accept one terminated chunk stream and zero alignment padding only."""
    require(data[:4] == b'SCHl', 'Expected an EA SCHl stream')
    at = 0
    while at < len(data):
        require(at + 8 <= len(data), 'Truncated EA chunk header')
        tag, size = struct.unpack_from('<4sI', data, at)
        require(8 <= size <= len(data) - at and at + size <= MAX_STREAM,
                'EA chunk exceeds its bounded stream')
        at += size
        if tag == b'SCEl':
            require(size == 8 and (unindexed_tail or not any(data[at:])), 'Invalid EA end marker or nonzero padding')
            return data[:at]
    raise ValueError('EA stream has no end marker')


def bank_entries(header, data):
    """Resolve logical HDR ordinals independently of physical DAT ordering.

    Metadata is identified, never interpreted as a runtime event declaration.
    Duplicate offsets intentionally preserve multiple logical entries.
    """
    require(12 <= len(header) <= 65536 and 0 < len(data) <= MAX_BANK, 'Invalid speech bank budget')
    count, stride, unit = header[5], (header[4] & 127) + 2, (header[7] + 1) * 256
    require(count > 0 and 12 + count * stride <= len(header), 'Truncated speech entry table')
    starts = [int.from_bytes(header[12 + i * stride:14 + i * stride], 'big') * unit
              for i in range(count)]
    terminal = struct.unpack_from('<H', header, 8)[0] * unit
    require(0 < terminal <= len(data) and all(0 <= start < terminal for start in starts),
            'Speech bank offsets exceed DAT')
    ordered = sorted(set(starts)) + [terminal]
    streams = {start: stream_span(data[start:stop], unindexed_tail=True)
               for start, stop in zip(ordered, ordered[1:])}
    gaps = [{'start': start + len(streams[start]), 'bytes': stop - start - len(streams[start]),
             'sha256': digest(data[start + len(streams[start]):stop]),
             'nonzero': any(data[start + len(streams[start]):stop])}
            for start, stop in zip(ordered, ordered[1:]) if start + len(streams[start]) < stop]
    metadata = bytearray(header)
    metadata[2:4] = b'\0\0'  # Voice ID, physical alignment and offsets are not event identity.
    metadata[7:10] = bytes(3)
    for i in range(count):
        metadata[12 + i * stride:14 + i * stride] = b'\0\0'
    return [streams[start] for start in starts], {
        'header_sha256': digest(header), 'data_sha256': digest(data),
        'event_metadata_sha256': digest(metadata), 'entry_count': count,
        'event_template_identity': digest(bytes(2) + bytes(metadata[2:])),
        'source_offsets': starts, 'unindexed_prefix_bytes': ordered[0],
        'unindexed_suffix_bytes': len(data) - terminal, 'unindexed_gaps': gaps,
    }


def export_voice(banks, absent, intro, extro, destination, catalog, *, recomp, game):
    """Build an explicit voice4 source using exact, verified-template matches.

    The output is an authoring fragment and audio files, not an installed pack.
    Missing banks must be declared absent; no donor clips are synthesized.
    """
    categories = {'Character': (0, 1), 'Taunts': (16625, 16626), 'Enviro': (40962, 40963)}
    require(type(banks) is dict and type(absent) is set and not banks.keys() & absent
            and banks.keys() | absent == categories.keys(),
            'Declare each category once with --bank or --absent')
    require(catalog.get('identity') == 'fighter-voice-events-1'
            and type(catalog.get('templates')) is list, 'Unsupported runtime voice catalog')
    destination = ordinary(destination)
    require(not destination.exists(), 'Voice destination already exists; choose a new folder')
    files, specs, reports = {}, {}, {}

    def audio(name, stream):
        info = prepare_r2(stream)[1]
        files[name] = stream
        return {'path': name, 'sha256': digest(stream), 'format': 'ea-adpcm-r2'}, info

    for category in categories:
        if category in absent:
            specs[category] = {'state': 'absent'}
            reports[category] = {'state': 'absent'}
            continue
        header_path = ordinary(banks[category])
        header = read_bounded(header_path, 65536)
        streams, metadata = bank_entries(header, read_bounded(header_path.with_suffix('.dat'), MAX_BANK))
        family = struct.unpack_from('<H', header)[0]
        require(family in categories[category], 'Source voice family differs from category: ' + category)
        matches = [row for row in catalog['templates'] if row['category'] == category
                   and row['event_identity'] == metadata['event_template_identity']
                   and row['entries'] == len(streams)]
        require(matches, 'No verified event template matches source bank: ' + category)
        chosen = min(matches, key=lambda row: row['template_voice'])
        samples, rows = {}, []
        for index, stream in enumerate(streams):
            samples[str(index)], info = audio(f'audio/{category}/{index:03d}.bin', stream)
            rows.append(info)
        specs[category] = {'state': 'present', 'template_voice': chosen['template_voice'],
                           'family': family, 'samples': samples}
        reports[category] = {**metadata, 'state': 'present', 'template_voice': chosen['template_voice'],
                             'family': family, 'entries': rows}
    source = {'format': 'fighter-voice-4', 'banks': specs}
    for purpose, path in (('intro', intro), ('extro', extro)):
        data = read_bounded(path, MAX_STREAM)
        exact = stream_span(data)
        source[purpose], reports[purpose] = audio(f'audio/{purpose}.bin', exact)
        reports[purpose]['input_sha256'] = digest(data)
    require(sum(map(len, files.values())) <= 256 * 1024**2, 'Voice export exceeds aggregate budget')
    report = {'schema': 'fighter-voice-export-1', 'archive_sha256': catalog['archive_sha256'],
              'categories': reports, 'files': {name: digest(data) for name, data in files.items()},
              'native_compilation': False, 'native_playtest': False,
              'next': 'Copy source fragment into a voice resource, copy audio files, then run fighter validate/package'}
    # Preflight all streams, templates and declarations before creating output.
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.fighter-voice-', dir=destination.parent) as temporary:
        stage = Path(temporary)
        for name, data in files.items():
            path = stage / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        (stage / 'voice-source.json').write_text(json.dumps(source, indent=2) + '\n', encoding='utf-8')
        # Decoder-export preflight is intentionally broader than native R2
        # admission. Use the shared compiler for predictor/header/packet and
        # per-bank alignment/aggregate budgets before publishing any output.
        from .fighter_pack import contract
        checked = contract(recomp, game, 'validate-voice', voice_source=stage / 'voice-source.json')
        require(checked.get('component_compilation') is True
                and checked.get('source_sha256') == digest((stage / 'voice-source.json').read_bytes()),
                'Runtime did not compile the exact exported voice source')
        report['component_compilation'] = True
        report['voice_validation'] = checked
        (stage / 'voice-export.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
        destination.mkdir()
        import shutil
        for path in stage.iterdir():
            if path.is_dir():
                shutil.copytree(path, destination / path.name)
            else:
                shutil.copyfile(path, destination / path.name)
    return report


def prepare_r2(data):
    """Preserve the partial final ADPCM block that FFmpeg rounds down.

    R2 codes blocks of 28 samples. Ask the decoder to decode the complete final
    encoded block, then retain exactly the source's declared sample count. No
    samples are synthesized. Non-final partial packets are a separate profile.
    """
    require(isinstance(data, bytes) and 8 <= len(data) <= MAX_STREAM, 'Invalid EA stream budget')
    require(stream_span(data) == data, 'Pass an exact EA stream without bank padding')
    size = struct.unpack_from('<I', data, 4)[0]
    header = data[8:size]
    require(header[:4] == b'PT\x07\0', 'Unsupported EA platform header')
    at, properties, split = 4, {}, False
    while at < len(header) and header[at] != 255:
        key = header[at]
        at += 1
        if key == 253:
            require(not split, 'Duplicate EA property section')
            split = True
            continue
        require(key not in properties and key != 254 and at < len(header), 'Invalid EA property')
        width = header[at]
        at += 1
        require(1 <= width <= 4 and at + width <= len(header), 'Invalid EA property span')
        # Native short count properties are signed; a high bit cannot be
        # reinterpreted as a positive duration during an offline export.
        properties[key] = int.from_bytes(header[at:at + width], 'big', signed=key == 0x85)
        at += width
    require(at < len(header) and header[at] == 255 and not any(header[at + 1:]),
            'Invalid EA property terminator')
    require(properties.get(0x80) == 3 and properties.get(0xA0) == 10,
            'Only revision 3 EA ADPCM R2 is supported by this exporter')
    # Native1264F0 defaults to 24000; FFmpeg's EA demuxer defaults to48000.
    # Declare the native rate in the staged header; do not resample the samples.
    terminator = at
    rate, channels, samples = properties.get(0x84, 24000), properties.get(0x82, 1), properties.get(0x85, 0)
    require(channels == 1 and 8000 <= rate <= 48000 and 0 < samples <= MAX_SAMPLES,
            'EA speech must be bounded mono audio at 8000..48000 Hz')
    at, packets, declared_packets = size, [], None
    while at < len(data):
        tag, size = struct.unpack_from('<4sI', data, at)
        if tag == b'SCCl':
            require(not packets and declared_packets is None and size == 12, 'Invalid EA packet count')
            declared_packets = struct.unpack_from('<I', data, at + 8)[0]
        elif tag == b'SCDl':
            require(size > 16, 'EA packet has no coded data')
            count, offset = struct.unpack_from('<2I', data, at + 8)
            require(0 < count <= MAX_SAMPLES and offset == 0, 'Unsupported EA mono packet layout')
            packets.append((at + 8, count))
        else:
            require(tag == b'SCEl' and at + size == len(data), 'Unsupported EA stream chunk')
        at += size
    require(packets and (declared_packets is None or declared_packets == len(packets)),
            'EA packet population differs from header')
    require(sum(n for _, n in packets) == samples, 'EA packet samples differ from header')
    require(all(n % 28 == 0 for _, n in packets[:-1]), 'Non-final partial R2 block needs a separate adapter')
    rounding = (-packets[-1][1]) % 28
    staged = bytearray(data)
    if rounding:
        struct.pack_into('<I', staged, packets[-1][0], packets[-1][1] + rounding)
    if 0x84 not in properties:
        rate_property = b'\x84\x04' + struct.pack('>I', rate)
        staged[8 + terminator:8 + terminator] = rate_property
        struct.pack_into('<I', staged, 4, len(header) + 8 + len(rate_property))
    return bytes(staged), {'sample_rate': rate, 'sample_count': samples,
                          'packet_count': len(packets), 'decoded_tail_samples_to_trim': rounding}


def decode_stream(data, ffmpeg, ffprobe, scratch):
    staged, info = prepare_r2(data)
    source, output = scratch / 'input.asf', scratch / 'output.pcm'
    source.write_bytes(staged)
    options = ['-v', 'error', '-protocol_whitelist', 'file', '-f', 'ea', '-i', str(source)]
    result = subprocess.run([str(ffprobe), *options, '-show_entries',
                             'stream=codec_name,sample_rate,channels', '-of', 'json'],
                            capture_output=True, timeout=30)
    require(result.returncode == 0 and not result.stderr and len(result.stdout) < 8192,
            'FFprobe could not inspect this bounded EA stream')
    probe = json.loads(result.stdout)
    require(probe.get('streams') == [{'codec_name': 'adpcm_ea_r2',
                                     'sample_rate': str(info['sample_rate']), 'channels': 1}],
            'FFprobe stream format disagrees with the EA header')
    with (scratch / 'decode-errors.txt').open('wb') as errors:
        result = subprocess.run([str(ffmpeg), '-nostdin', '-xerror', *options, '-map', '0:a:0',
                                 '-c:a', 'pcm_s16le', '-f', 's16le', '-fs', str(2 * MAX_SAMPLES + 56),
                                 '-y', str(output)], stdout=subprocess.DEVNULL, stderr=errors, timeout=60)
    require(result.returncode == 0 and (scratch / 'decode-errors.txt').stat().st_size == 0,
            'FFmpeg rejected the EA stream; no truncated output is accepted')
    pcm = read_bounded(output, 2 * MAX_SAMPLES + 56)
    require(len(pcm) == 2 * (info['sample_count'] + info['decoded_tail_samples_to_trim']),
            'Decoded sample population differs from the declared source')
    pcm = pcm[:2 * info['sample_count']]
    return pcm, {**info, 'source_sha256': digest(data), 'pcm16_sha256': digest(pcm)}


def export_audio(source, destination, ffmpeg=None, ffprobe=None, header=None, encoding='wav-pcm16'):
    source, destination = ordinary(source), ordinary(destination)
    require(encoding in ('wav-pcm16', 'ea-adpcm-r2'), 'Unknown audio export format')
    if encoding == 'wav-pcm16':
        require(ffmpeg is not None and ffprobe is not None, 'WAV export requires explicit FFmpeg and FFprobe paths')
        ffmpeg, ffprobe = ordinary(ffmpeg), ordinary(ffprobe)
        require(ffmpeg.is_file() and ffprobe.is_file(), 'Choose existing local FFmpeg and FFprobe executables')
    require(not destination.exists(), 'Audio destination already exists; choose a new folder')
    data = read_bounded(source, MAX_BANK if header else MAX_STREAM)
    if header:
        streams, bank = bank_entries(read_bounded(header, 65536), data)
    else:
        streams, bank = [stream_span(data)], None
    # Preflight every stream before any decoder or output; unknown input fails as a whole.
    infos = [prepare_r2(stream)[1] for stream in streams]
    require(sum(info['sample_count'] * 2 for info in infos) <= 512 * 1024**2,
            'Decoded bank exceeds the aggregate output budget')
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.fighter-audio-', dir=destination.parent) as temporary:
        stage = Path(temporary)
        scratch, result = stage / 'scratch', stage / 'result'
        scratch.mkdir(); result.mkdir()
        rows = []
        for ordinal, stream in enumerate(streams):
            if encoding == 'wav-pcm16':
                pcm, receipt = decode_stream(stream, ffmpeg, ffprobe, scratch)
                name = f'{ordinal:03d}.wav'
                with wave.open(str(result / name), 'wb') as output:
                    output.setparams((1, 2, receipt['sample_rate'], 0, 'NONE', 'not compressed'))
                    output.writeframes(pcm)
            else:
                name = f'{ordinal:03d}.bin'
                (result / name).write_bytes(stream)
                receipt = {k: v for k, v in infos[ordinal].items() if k != 'decoded_tail_samples_to_trim'}
                receipt['source_sha256'] = digest(stream)
            rows.append({'ordinal': ordinal, 'file': name, 'format': encoding, **receipt,
                         'sha256': digest((result / name).read_bytes())})
        report = {'schema': 'fighter-audio-export-1', 'source_sha256': digest(data),
                  'bank': bank, 'entries': rows, 'encoding': encoding,
                  'tools': {'ffmpeg_sha256': digest(ffmpeg.read_bytes()),
                            'ffprobe_sha256': digest(ffprobe.read_bytes())} if encoding == 'wav-pcm16' else {},
                  'runtime_ready': False,
                  'event_assignment': 'unassigned; match verified template metadata separately'}
        (result / 'audio-export.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
        # Exclusive final directory; leave existing user output untouched, including races.
        destination.mkdir()
        for path in result.iterdir():
            with (destination / path.name).open('xb') as output:
                output.write(path.read_bytes())
    return report
