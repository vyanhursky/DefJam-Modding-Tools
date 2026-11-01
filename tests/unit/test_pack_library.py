"""Published-byte identity, complete membership and independent review persistence."""
import hashlib
import io
import json
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
import zipfile
from unittest.mock import patch

from PIL import Image
from defjam_tools.pack_library import PackLibrary, safe_name
from defjam_tools.texture_workshop import Invalid, Conflict


def png(size=(8, 4), colour=(70, 20, 90, 80)):
    out=io.BytesIO(); Image.new('RGBA',size,colour).save(out,format='PNG'); return out.getvalue()


class PackTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);self.corpus=self.root/'corpus';self.corpus.mkdir()
        self.sid='a'*64;self.original=png((2,1));self.published=png()
        (self.corpus/'original.png').write_bytes(self.original);(self.corpus/'faithful.png').write_bytes(png())
        self.old={'reviews':{'keep':'exact'},'candidates':{}}
        self.store=SimpleNamespace(root=self.root/'workshop',corpus_root=self.corpus,
            assets={self.sid:dict(id=self.sid,label='Synthetic heading',category='UI',original='original.png',upscaled='faithful.png')},data=self.old)
        self.zip=self.root/'pack.zip';self.make_zip()
        self.cfg={'schema':1,'review_root':str(self.root/'pass'), 'packs':[self.spec()]}
        self.config=self.root/'config.json';self.write_config();self.lib=PackLibrary(self.config,self.store)
    def make_zip(self,colour=None):
        with zipfile.ZipFile(self.zip,'w',zipfile.ZIP_DEFLATED) as z:
            z.writestr('pack/manifest.ini','[pack]\nschema=1\n[textures]\n'+self.sid+'=textures/native.png\n[wide]\n'+self.sid+'=-512:wide/left.png;512:wide/right.png\n')
            z.writestr('pack/textures/native.png',png(colour=colour) if colour else self.published)
            z.writestr('pack/wide/left.png',png());z.writestr('pack/wide/right.png',png())
            z.writestr('pack/anchors/context.png',png())
    def spec(self):
        return dict(id='menus-1',name='Synthetic menu pack',version='1',archive=str(self.zip),size=self.zip.stat().st_size,sha256=hashlib.sha256(self.zip.read_bytes()).hexdigest())
    def write_config(self):self.config.write_text(json.dumps(self.cfg),encoding='utf8')
    def native(self):return next(r for r in self.lib.entries.values() if r['kind']=='native')
    def test_every_png_is_visible_and_published_bytes_are_exact(self):
        p=self.lib.config('token')['packs'][0];self.assertEqual((p['native'],p['wide'],p['supporting'],p['pngs']),(1,2,1,4))
        r=self.native();self.assertEqual(self.lib.image('menus-1',r['id'],'published'),self.published)
        self.assertEqual(self.lib.image('menus-1',r['id'],'original'),self.original)
        self.assertEqual(set(r['baseline']),{'original','faithful'})
        wide=next(r for r in self.lib.entries.values() if r['kind']=='wide');self.assertEqual(wide['baseline'],{})
    def test_requested_page_sizes_and_last_page_use_real_manifest_members(self):
        with zipfile.ZipFile(self.zip,'w') as z:
            lines=[]
            for i in range(237):
                sid=f'{i:064x}';name=f'textures/{sid}.png'
                lines.append(sid+'='+name);z.writestr('pack/'+name,self.published)
            z.writestr('pack/manifest.ini','[pack]\nschema=1\n[textures]\n'+'\n'.join(lines))
        self.cfg['packs']=[self.spec()];self.write_config();lib=PackLibrary(self.config,self.store)
        for limit in (10,25,50,100,200):
            with self.subTest(limit=limit):
                first=lib.catalog({'pack':['menus-1'],'limit':[str(limit)]})
                tail=lib.catalog({'pack':['menus-1'],'limit':[str(limit)],'offset':[str(limit)]})
                self.assertEqual(len(first['items']),limit)
                self.assertEqual(len(tail['items']),min(limit,237-limit))
                self.assertTrue({r['id'] for r in first['items']}.isdisjoint(r['id'] for r in tail['items']))
        self.assertEqual(len(lib.catalog({'limit':['9999']})['items']),200)

    def test_search_filters_and_status_queue(self):
        r=self.native();self.lib.save('menus-1',r['id'],dict(version=0,status='needs_revision',notes='Keep the stencil cuts'))
        result=self.lib.catalog({'pack':['menus-1'],'kind':['native'],'status':['needs_revision'],'q':['heading']})
        self.assertEqual(result['total'],1);self.assertEqual(result['counts']['needs_revision'],1)
        self.assertEqual(self.lib.export()['reviews'][0]['notes'],'Keep the stencil cuts')
        self.assertEqual(self.old,{'reviews':{'keep':'exact'},'candidates':{}})
    def test_conflicts_and_disk_failure_retain_prior_review(self):
        r=self.native();req=dict(version=0,status='looks_good',notes='Original approved separately')
        self.lib.save('menus-1',r['id'],req)
        with self.assertRaises(Conflict):self.lib.save('menus-1',r['id'],req)
        before=self.lib.file.read_bytes()
        with patch('defjam_tools.pack_library.atomic_json',side_effect=OSError('disk full')):
            with self.assertRaises(OSError):self.lib.save('menus-1',r['id'],dict(req,version=1,notes='Unsaved'))
        self.assertEqual(self.lib.file.read_bytes(),before);self.assertEqual(self.lib.review(r)['version'],1)
        reopened=PackLibrary(self.config,self.store);self.assertEqual(reopened.review(r)['notes'],req['notes'])
    def test_changed_release_gets_an_independent_review(self):
        r=self.native();self.lib.save('menus-1',r['id'],dict(version=0,status='looks_good',notes='Old release'))
        self.make_zip(colour=(200,40,30,255));self.cfg['packs']=[self.spec()];self.write_config()
        other=PackLibrary(self.config,self.store);self.assertEqual(other.review(next(r for r in other.entries.values() if r['kind']=='native'))['version'],0)
        self.assertEqual(len(other.data['reviews']),1)
    def test_hash_and_size_mismatch_fail_closed(self):
        for field,value in [('sha256','0'*64),('size',1)]:
            self.cfg['packs']=[dict(self.spec(),**{field:value})];self.write_config()
            with self.assertRaises(Invalid):PackLibrary(self.config,self.store)
    def test_paths_duplicates_symlinks_and_missing_pngs_are_rejected(self):
        for name in ['../bad.png','/bad.png','a\\bad.png','a//bad.png','a/./bad.png','C:/bad.png']:
            with self.subTest(name=name),self.assertRaises(Invalid):safe_name(name)
        for kind in ['duplicate','symlink','missing']:
            self.make_zip()
            with zipfile.ZipFile(self.zip,'a') as z:
                if kind=='duplicate':z.writestr('pack/TEXTURES/NATIVE.PNG',png())
                elif kind=='symlink':
                    info=zipfile.ZipInfo('pack/link.png');info.external_attr=(0o120777<<16);z.writestr(info,'target')
                else:
                    # A manifest references no such file.
                    z.writestr('second/manifest.ini','[pack]\nschema=1\n[textures]\n'+self.sid+'=missing.png')
            self.cfg['packs']=[self.spec()];self.write_config()
            with self.subTest(kind=kind),self.assertRaises(Invalid):PackLibrary(self.config,self.store)
    def test_review_root_cannot_share_old_workspace_or_corpus(self):
        for root in [self.store.root,self.corpus,self.corpus/'notes',self.root]:
            self.cfg['review_root']=str(root);self.write_config()
            with self.subTest(root=root),self.assertRaises(Invalid):PackLibrary(self.config,self.store)
    def test_alpha_crop_and_immutable_hash_guard(self):
        r=self.native();r['crop']=[0,0,.5,1]
        out=self.lib.image('menus-1',r['id'],'published','alpha',True)
        with Image.open(io.BytesIO(out)) as im:self.assertEqual(im.size,(4,4));self.assertEqual(im.getpixel((0,0)),80)
        (self.corpus/'original.png').write_bytes(png((2,1),(0,0,0,0)))
        with self.assertRaises(Invalid):self.lib.image('menus-1',r['id'],'original')


class PackHTTPTests(unittest.TestCase):
    setUp=PackTests.setUp
    make_zip=PackTests.make_zip
    spec=PackTests.spec
    write_config=PackTests.write_config
    native=PackTests.native
    def test_pack_routes_require_loopback_origin_and_token(self):
        import threading
        from urllib.error import HTTPError
        from urllib.request import Request,urlopen
        from defjam_tools.texture_workshop import ThreadingHTTPServer,handler_for
        server=ThreadingHTTPServer(('127.0.0.1',0),handler_for(self.store,'test-token',self.lib))
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        self.addCleanup(server.server_close);self.addCleanup(server.shutdown)
        base='http://127.0.0.1:'+str(server.server_port)
        with urlopen(base+'/packs') as response:self.assertIn(b'Published texture library',response.read())
        with urlopen(base+'/packs-controls.js') as response:self.assertIn(b'export class InspectCamera',response.read())
        with urlopen(base+'/api/packs/config') as response:self.assertEqual(json.load(response)['packs'][0]['pngs'],4)
        row=self.native();url=base+'/api/packs/menus-1/'+row['id']+'/review';body=json.dumps(dict(version=0,status='needs_revision',notes='Preserve stencil')).encode()
        for headers in [{},{'X-Workshop-Token':'test-token','Origin':'https://other.invalid'},{'X-Workshop-Token':'test-token','Host':'other.invalid'}]:
            with self.subTest(headers=headers),self.assertRaises(HTTPError) as cm:urlopen(Request(url,data=body,headers=headers))
            self.assertEqual(cm.exception.code,403)
        headers={'X-Workshop-Token':'test-token','Origin':base}
        with urlopen(Request(url,data=body,headers=headers)) as response:self.assertEqual(json.load(response)['version'],1)
        with self.assertRaises(HTTPError) as cm:urlopen(Request(url,data=body,headers=headers))
        self.assertEqual(cm.exception.code,409)
        with urlopen(base+'/api/packs/menus-1/'+row['id']+'/image/published') as response:self.assertEqual(response.read(),self.published)

if __name__=="__main__":unittest.main()
