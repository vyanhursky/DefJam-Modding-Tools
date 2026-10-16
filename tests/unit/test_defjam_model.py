"""Synthetic EAGL-like data resources; no game files or downloaded fixtures."""
import copy
import io
import json
from pathlib import Path
import struct
import sys
import tempfile
import threading
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen

try:
    from PIL import Image
except ImportError:
    raise unittest.SkipTest("Model preview tests require Pillow")

from defjam_tools import defjam_model as m, model_workshop as mw, texture_workshop as w


def fixture():
    """Independent four-vertex plane with an ELF section-relative pointer graph."""
    data=bytearray(0x1400);rel=[]
    names=['','__Model:::synthetic','__RM:::__GP_RM_synthetic_0',
           *['__VB:::__GPvb_'+str(i)+'_0_synthetic' for i in range(5)],
           'ParentRM_IrradTexture_Skin','__const MATRIX4:::EAGLAnimationBuffer',
           '__EAGL::GeoPrimState:::SetPrimitiveType=EAGL::PT_TRIANGLESTRIP;']
    # Symbol0 is the section symbol (empty name). The fixture is hand-authored.
    values=[0,0x1000,0x200,*[0x600+i*0x30 for i in range(5)],0,0,0]
    def word(at,v):struct.pack_into('<I',data,at,v)
    def ptr(at,v):word(at,v);rel.append((at,2))
    def external(at,index):word(at,0);rel.append((at,(index<<8)|2))
    word(0x109c,1);ptr(0x10a0,0x1200);ptr(0x10cc,0x1240)
    ptr(0x1200,0x1280);data[0x1280:0x1285]=b'body\0'
    word(0x1240,0);word(0x1244,1);ptr(0x1248,0x238)
    external(0x21c,8);external(0x248,10);external(0x260,9)
    word(0x264,1);ptr(0x268,0x100);word(0x26c,4);ptr(0x270,0x120);word(0x100,4)
    struct.pack_into('<4H',data,0x120,0,1,2,3)
    arrays=[(12,0x800),(8,0x840),(4,0x870),(4,0x890),(2,0x8b0)]
    for i,(stride,at) in enumerate(arrays):
        header=0x600+i*0x30;word(header+4,stride*4);word(header+8,stride);word(header+12,1);ptr(header+16,at)
    struct.pack_into('<12f',data,0x800,0,0,0,1,0,0,0,1,0,1,1,0)
    struct.pack_into('<8f',data,0x840,0,0,1,0,0,1,1,1)
    struct.pack_into('<4I',data,0x870,*[0xffffffff]*4)
    struct.pack_into('<4I',data,0x890,*[513<<22]*4) # source normal (0,0,-1)
    shstr=b'\0.data\0.shstrtab\0.strtab\0.symtab\0.rel.data\0'
    strings=b'\0';offsets=[]
    for name in names:offsets.append(len(strings));strings+=name.encode()+b'\0'
    sym=b''.join(struct.pack('<IIIBBH',offsets[i],v,4,17,0,1 if i<8 else 0) for i,v in enumerate(values))
    payloads=[b'',bytes(data),shstr,strings,sym,b''.join(struct.pack('<II',*r) for r in rel)]
    sections=[];blob=bytearray(b'\0'*52)
    for i,payload in enumerate(payloads):
        at=len(blob);blob.extend(payload)
        sections.append((0 if not i else shstr.index(('.data','.shstrtab','.strtab','.symtab','.rel.data')[i-1].encode()),
                         (0,1,3,3,2,9)[i],0,0,at,len(payload),3 if i==4 else (4 if i==5 else 0),1 if i==5 else 0,4,16 if i==4 else (8 if i==5 else 0)))
    shoff=len(blob)
    for section in sections:blob.extend(struct.pack('<10I',*section))
    blob[:16]=b'\x7fELF\x01\x01\x01'+b'\0'*9
    struct.pack_into('<HHIIIIIHHHHHH',blob,16,1,8,1,0,0,shoff,0,52,0,0,40,6,2)
    return bytes(blob)


def png():
    f=io.BytesIO();Image.new('RGBA',(2,2),(40,90,180,123)).save(f,format='PNG');return f.getvalue()


class DecodeTests(unittest.TestCase):
    def test_plane_keeps_top_left_uvs_normals_and_reverses_winding(self):
        model=m.decode(fixture(),'Plane','a'*64);mesh=model['meshes'][0]
        self.assertEqual(model['bounds'],[[0,0,0],[1,1,0]])
        self.assertEqual(mesh['uv'],[[0,0],[1,0],[0,1],[1,1]])
        self.assertEqual(mesh['normals'],[[0,0,-1]]*4)
        self.assertEqual(mesh['indices'],[1,0,2,1,2,3])
        for i in range(0,len(mesh['indices']),3):
            a,b,c=[mesh['positions'][j] for j in mesh['indices'][i:i+3]]
            # Both faces must agree with the negative-Z source normal.
            self.assertLess((b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0]),0)
        self.assertEqual((model['vertices'],model['triangles']),(4,2))

    def test_strip_degenerate_joins_keep_parity(self):
        self.assertEqual(m.triangles_from_strip([0,1,2,2,3,3,4,5],6),[0,1,2,4,3,5])
        with self.assertRaises(m.ModelError):m.triangles_from_strip([0,1,65535],3)

    def test_rejects_invalid_elf_ranges_external_pointers_and_bad_indices(self):
        raw=fixture()
        bad=bytearray(raw);struct.pack_into('<I',bad,32,0xfffffffc)
        with self.assertRaises(m.ModelError):m.ElfData(bytes(bad))
        elf=m.ElfData(raw)
        with self.assertRaises(m.ModelError):elf.ptr(0x260)
        with self.assertRaises(m.ModelError):elf.unpack('<4f',len(elf.data)-4)
        bad=bytearray(raw);struct.pack_into('<H',bad,52+0x120,4)
        with self.assertRaises(m.ModelError):m.decode(bytes(bad),'Plane','a'*64)

    def test_glb_is_self_contained_aligned_and_preserves_source_values(self):
        model=m.decode(fixture(),'Plane','a'*64);raw=m.make_glb(model,png(),'draft-one')
        magic,version,length=struct.unpack_from('<III',raw);self.assertEqual((magic,version,length),(0x46546c67,2,len(raw)))
        size,kind=struct.unpack_from('<II',raw,12);self.assertEqual(kind,0x4e4f534a)
        doc=json.loads(raw[20:20+size]);binary=raw[28+size:]
        self.assertEqual(doc['extras']['revision'],'draft-one')
        self.assertNotIn('uri',doc['buffers'][0]);self.assertNotIn('uri',doc['images'][0])
        self.assertEqual(doc['materials'][0]['alphaMode'],'OPAQUE')
        self.assertEqual(doc['materials'][0]['extensions'],{'KHR_materials_unlit':{}})
        for v in doc['bufferViews']:
            self.assertEqual(v['byteOffset']%4,0)
            self.assertLessEqual(v['byteOffset']+v['byteLength'],len(binary))
        attrs=doc['meshes'][0]['primitives'][0]['attributes'];uv=doc['accessors'][attrs['TEXCOORD_0']];v=doc['bufferViews'][uv['bufferView']]
        self.assertEqual(struct.unpack_from('<8f',binary,v['byteOffset']),(0,0,1,0,0,1,1,1))
        image=doc['bufferViews'][doc['images'][0]['bufferView']]
        with Image.open(io.BytesIO(binary[image['byteOffset']:image['byteOffset']+image['byteLength']])) as im:
            self.assertEqual(im.getpixel((0,0)),(40,90,180,123))

    def test_transparent_material_stays_separate(self):
        model=m.decode(fixture(),'Plane','a'*64);second=copy.deepcopy(model['meshes'][0]);second.update(group='hair_ALPHA',transparent=True);model['meshes'].append(second)
        raw=m.make_glb(model,png());size=struct.unpack_from('<I',raw,12)[0];doc=json.loads(raw[20:20+size])
        self.assertEqual([v['alphaMode'] for v in doc['materials']],['OPAQUE','BLEND'])


class ModelStoreTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
        corpus=self.root/'corpus';corpus.mkdir();(corpus/'source.png').write_bytes(png())
        self.ident=m.FIGHTERS['trejo'][2]
        a=dict(id=self.ident,width=2,height=2,label='Synthetic',original='source.png',upscaled='source.png',thumbnail='source.png')
        (corpus/'corpus.json').write_text(json.dumps(dict(corpus_id='synthetic',assets=[a])))
        self.store=w.Workshop(corpus,self.root/'work');dest=self.store.root/'models/trejo';dest.mkdir(parents=True)
        model=m.decode(fixture(),'Synthetic',self.ident);raw=json.dumps(model).encode();(dest/'geometry.json').write_bytes(raw)
        (dest/'index.json').write_text(json.dumps(dict(schema=1,decoder=1,source_id=self.ident,geometry_sha256=m.sha(raw),groups=['body'])))
        self.view=dict(position=[0,1,4],target=[0,0,0],left='original',right='faithful',lighting='unlit',wireframe=False,groups=['body'])

    def test_camera_saves_separately_from_existing_gallery_session_and_notes(self):
        self.store.save_session(dict(zoom='.25'));self.store.save_review(self.ident,'asset',dict(w.empty_review(),notes='Owner note'))
        before=self.store.file.read_bytes()
        mw.save_view(self.store,dict(fighter='trejo',view=self.view),w.atomic_json)
        self.assertEqual(mw.catalog(self.store)['state']['views']['trejo'],self.view)
        self.assertEqual(self.store.file.read_bytes(),before)

    def test_invalid_camera_revision_and_material_group_are_rejected(self):
        for key,value in [('position',[0,float('nan'),2]),('right','missing'),('groups',['bad']),('lighting','custom')]:
            with self.subTest(key=key),self.assertRaises(ValueError):mw.save_view(self.store,dict(fighter='trejo',view={**self.view,key:value}),w.atomic_json)
        with self.assertRaises(ValueError):mw.receipt(self.store,'../outside')

    def test_modified_geometry_is_not_exported(self):
        path=self.store.root/'models/trejo/geometry.json';path.write_bytes(path.read_bytes()+b' ')
        with self.assertRaisesRegex(ValueError,'checksum'):mw.model_glb(self.store,'trejo')

    def test_changed_candidate_bytes_cannot_reuse_an_immutable_revision_for_export(self):
        c=self.store.import_candidate(self.ident,png(),'Synthetic candidate','faithful')
        self.assertEqual(mw.model_glb(self.store,'trejo',c['id'])[:4],b'glTF')
        (self.store.root/c['path']).write_bytes(png()+b'changed')
        with self.assertRaisesRegex(ValueError,'Texture checksum'):mw.model_glb(self.store,'trejo',c['id'])

    def test_http_local_modules_camera_auth_and_glb_export(self):
        server=w.ThreadingHTTPServer(('127.0.0.1',0),w.handler_for(self.store,'test-token'))
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        self.addCleanup(server.server_close);self.addCleanup(server.shutdown)
        base='http://127.0.0.1:'+str(server.server_port)
        with urlopen(base+'/model-viewer') as r:self.assertIn(b'Synchronized 3D comparison',r.read())
        with urlopen(base+'/vendor/loaders/GLTFLoader.js') as r:
            self.assertIn(b"from '/vendor/three.module.min.js'",r.read());self.assertIn("connect-src 'self' blob:",r.headers['Content-Security-Policy'])
        with urlopen(base+'/api/model/trejo/model.glb?revision=faithful') as r:self.assertEqual(r.read()[:4],b'glTF')
        req=Request(base+'/api/model-view',data=json.dumps(dict(fighter='trejo',view=self.view)).encode(),headers={'Content-Type':'application/json'})
        with self.assertRaises(HTTPError) as e:urlopen(req)
        self.assertEqual(e.exception.code,403)
        req.add_header('X-Workshop-Token','test-token')
        with urlopen(req) as r:self.assertTrue(json.load(r)['saved'])
        for path in ['/vendor/../LICENSE','/api/model/unknown/model.glb']:
            with self.subTest(path=path),self.assertRaises(HTTPError):urlopen(base+path)


if __name__=='__main__':unittest.main()
