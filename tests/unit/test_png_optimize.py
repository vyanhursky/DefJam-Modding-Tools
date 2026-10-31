import io
import json
from pathlib import Path
import shutil
import struct
import zlib

from PIL import Image, PngImagePlugin
import pytest
from defjam_tools import png_optimize as mod


def png(compress=0, hidden=(35, 77, 121, 0)):
    im = Image.new('RGBA', (24, 12), (182, 34, 29, 200))
    im.putpixel((0, 0), hidden)
    info = PngImagePlugin.PngInfo()
    info.add_text('Source', 'Synthetic fixture café')
    info.add(b'gAMA', struct.pack('>I', 45455))
    data = io.BytesIO()
    im.save(data, format='PNG', compress_level=compress, pnginfo=info)
    return data.getvalue()


def test_exact_rgba_metadata_and_smaller_only():
    before, after = png(), png(9)
    selected, proof = mod.optimize_bytes(before, 'unused', encoder=lambda *_: after)
    assert selected == after and len(after) < len(before)
    assert proof['rgba_exact'] and proof['non_idat_chunks_exact']
    selected, proof = mod.optimize_bytes(after, 'unused', encoder=lambda *_: before)
    assert selected == after and proof['status'] == 'retained_not_smaller'


@pytest.mark.parametrize('candidate,reason', [
    (lambda: png(9, (0, 0, 0, 0)), 'Decoded RGBA'),
    (lambda: remove_chunk(png(9), b'gAMA'), 'metadata'),
    (lambda: remove_chunk(png(9), b'tEXt'), 'metadata'),
])
def test_rejects_hidden_rgb_and_metadata_changes(candidate, reason):
    original = png()
    selected, proof = mod.optimize_bytes(original, 'unused', encoder=lambda *_: candidate())
    assert selected == original and proof['status'] == 'retained_verification_failed'
    assert reason in proof['reason']


def remove_chunk(data, kind):
    return mod.SIGNATURE + b''.join(struct.pack('>I', len(v))+k+v+struct.pack('>I', zlib.crc32(k+v)&0xffffffff)
                                 for k,v in mod.chunks(data) if k != kind)


def test_crc_and_unsupported_depth():
    bad = bytearray(png()); bad[-1] ^= 1
    with pytest.raises(ValueError, match='CRC'):
        mod.chunks(bytes(bad))
    im = Image.new('I;16', (2, 2), 12345); buf = io.BytesIO(); im.save(buf, format='PNG')
    selected, proof = mod.optimize_bytes(buf.getvalue(), 'unused', encoder=lambda *_: pytest.fail('encoder called'))
    assert selected == buf.getvalue() and proof['status'] == 'retained_unsupported'


@pytest.mark.parametrize('name', ['../x.png', '/x.png', 'a/../x.png', 'a\\x.png', 'C:x.png', 'x.jpg', './x.png', 'a//x.png'])
def test_rejects_unsafe_output_paths(name):
    with pytest.raises(ValueError):
        mod.relative_png(name)


def test_manifest_case_collision_and_symlink(tmp_path):
    p = tmp_path/'source.png'; p.write_bytes(png())
    manifest = tmp_path/'inputs.json'
    manifest.write_text(json.dumps([{'input':str(p),'output':n} for n in ['A.png','a.png']]))
    with pytest.raises(ValueError, match='Duplicate'):
        mod.plan_entries(manifest=manifest)
    link = tmp_path/'link.png'
    try:
        link.symlink_to(p)
    except OSError:
        pytest.skip('symlinks unavailable')
    manifest.write_text(json.dumps([{'input':str(link),'output':'x.png'}]))
    with pytest.raises(ValueError, match='symlink'):
        mod.plan_entries(manifest=manifest)


def test_batch_copy_receipt_and_existing_output(tmp_path, monkeypatch):
    source = tmp_path/'input'; source.mkdir()
    p = source/'one.png'; original = png(); p.write_bytes(original)
    out = tmp_path/'output'
    monkeypatch.setattr(mod.shutil, 'which', lambda _: 'fake-oxipng')
    monkeypatch.setattr(mod.subprocess, 'run', lambda *a,**k: type('Result', (), {'stdout':'oxipng synthetic'})())
    monkeypatch.setattr(mod, 'encode_copy', lambda *_: png(9))
    receipt = mod.optimize_batch(out, source=source, jobs=1)
    assert receipt['complete'] and receipt['files']==1 and receipt['failures']==0
    assert receipt['saved_bytes'] > 0 and p.read_bytes()==original
    assert json.loads((out/'optimization-receipt.json').read_text()) == receipt
    mod.verify_pixels(original, (out/'one.png').read_bytes())
    with pytest.raises(ValueError, match='already exist'):
        mod.optimize_batch(out, source=source)
    with pytest.raises(ValueError, match='disjoint'):
        mod.optimize_batch(source/'child', source=source)


@pytest.mark.skipif(not shutil.which('oxipng'), reason='optional installed optimizer')
def test_real_oxipng_profile():
    original=png()
    optimized, proof=mod.optimize_bytes(original, shutil.which('oxipng'))
    assert proof['status']=='optimized', proof
    assert len(optimized)<len(original)
    mod.verify_pixels(original, optimized)
