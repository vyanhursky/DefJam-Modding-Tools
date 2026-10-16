"""Durable authoring-state and export checks with synthetic PNGs; no game data.

Can run without pytest: python -m unittest discover -s tests/unit -p test_texture_workshop.py
"""
import copy
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import sys
import threading
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import Request, urlopen

try:
    from PIL import Image
except ImportError:
    raise unittest.SkipTest("Texture workshop tests require Pillow")

from defjam_tools import texture_workshop as w


def png(size=(8,8),colour=(30,70,110,180)):
    out=io.BytesIO();Image.new("RGBA",size,colour).save(out,format="PNG");return out.getvalue()


class WorkshopTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);self.corpus=self.root/"corpus";self.corpus.mkdir();self.work=self.root/"work"
        self.ident="a"*64
        for name in ("original.png","faithful.png","thumb.png"):(self.corpus/name).write_bytes(png((2,2)))
        asset=dict(id=self.ident,width=2,height=2,label="Synthetic atlas",category="Fighters",categories=["Fighters"],
                   aliases=[dict(source="assets/v2ip.viv::V2IP_113A.xsh",index=0,name="test")],
                   original="original.png",upscaled="faithful.png",thumbnail="thumb.png")
        (self.corpus/"corpus.json").write_text(json.dumps(dict(corpus_id="c"*64,assets=[asset])))
        self.store=w.Workshop(self.corpus,self.work,{"b"*64:self.ident})

    def test_notes_regions_flags_and_session_survive_reopen(self):
        review=w.empty_review();review.update(notes="Keep tattoo lettering; verify reference",flag=True,tags=["tattoo"],
            regions=[dict(id="one",rect=[.2,.3,.4,.2],kind="protect",note="Keep face unchanged")])
        saved=self.store.save_review(self.ident,"asset",review)
        self.store.save_session(dict(scope="featured",asset=self.ident,target="asset",zoom="2"))
        reopened=w.Workshop(self.corpus,self.work)
        self.assertEqual(reopened.review(self.ident),saved)
        self.assertEqual(reopened.data["session"]["zoom"],"2")
        self.assertEqual(reopened.catalog({"scope":["featured"]})["total"],1)

    def test_conflicting_tab_cannot_overwrite_new_notes(self):
        first=w.empty_review();first["notes"]="Owner note"
        self.store.save_review(self.ident,"asset",first)
        stale=w.empty_review();stale["notes"]="Stale tab"
        with self.assertRaises(w.Conflict):self.store.save_review(self.ident,"asset",stale)
        self.assertEqual(json.loads(self.store.file.read_text())["reviews"][self.ident+":asset"]["notes"],"Owner note")

    def test_failed_disk_save_rolls_back_memory(self):
        before=self.store.file.read_bytes()
        with patch.object(w,"atomic_json",side_effect=OSError("disk full")):
            with self.assertRaises(OSError):self.store.save_review(self.ident,"asset",dict(w.empty_review(),notes="unsaved"))
        self.assertEqual(self.store.review(self.ident)["version"],0)
        self.assertEqual(self.store.file.read_bytes(),before)

    def test_invalid_regions_do_not_replace_existing_review(self):
        for rect in ([.9,0,.2,.4],[0,0,float("nan"),.5],[0,0,0,.5]):
            with self.subTest(rect=rect):
                r=dict(w.empty_review(),regions=[dict(id="x",rect=rect,kind="revise",note="test")])
                with self.assertRaises(w.Invalid):self.store.save_review(self.ident,"asset",r)
                self.assertEqual(self.store.review(self.ident)["version"],0)

    def test_candidates_immutable_revisions_and_shape_checked(self):
        a=self.store.import_candidate(self.ident,png(),"First","faithful",prompt="Exact prompt")
        b=self.store.import_candidate(self.ident,png(),"Second","faithful",parent=a["id"])
        self.assertNotEqual(a["id"],b["id"])
        self.assertEqual(a["sha256"],b["sha256"])
        self.assertEqual(b["parent"],a["id"])
        with self.assertRaises(w.Invalid):self.store.import_candidate(self.ident,png((8,4)),"Wrong aspect","faithful")
        with self.assertRaises(w.Invalid):self.store.import_candidate(self.ident,png((3,3)),"Noninteger","faithful")
        self.assertEqual(len(self.store.detail(self.ident)["candidates"]),2)
        self.assertEqual(self.store.review(self.ident,a["id"])["status"],"unreviewed")

    def approve(self,candidate,selected=True):
        r=self.store.review(self.ident,candidate["id"])
        r.update(status="approved",face_reviewed=True,channels_reviewed=True,selected=selected)
        return self.store.save_review(self.ident,candidate["id"],r)

    def test_generated_assembly_preserves_face_pixels_alpha_and_raw_provenance(self):
        baseline=Image.new("RGBA",(8,8),(10,20,30,255))
        baseline.putpixel((1,6),(40,50,60,17))
        baseline.putpixel((7,0),(70,80,90,123))
        baseline.save(self.corpus/"faithful.png")
        job=self.store.queue_request(self.ident,"faithful","asset","")
        raw=png((5,5),(200,100,50,1))
        candidate=self.store.import_candidate(self.ident,raw,"Assembled","faithful",
            assembly=dict(scale=4,preserve_alpha=True,protected_regions=[[.5,0,.5,.5]]),request_id=job["id"])
        with Image.open(self.store.image_path(self.ident,candidate["id"])) as result:
            self.assertEqual(result.size,(8,8))
            self.assertEqual(result.crop((4,0,8,4)).tobytes(),baseline.crop((4,0,8,4)).tobytes())
            self.assertEqual(result.getchannel("A").tobytes(),baseline.getchannel("A").tobytes())
            self.assertEqual(result.getpixel((1,6)),(200,100,50,17))
        self.assertEqual((self.work/candidate["assembly"]["raw_path"]).read_bytes(),raw)
        self.assertEqual(candidate["assembly"]["raw_sha256"],w.sha(raw))
        self.assertEqual(candidate["assembly"]["protected_pixel_boxes"],[[4,0,8,4]])
        self.assertEqual(self.store.data["requests"][0]["output_revision"],candidate["id"])
        self.assertEqual(self.store.data["requests"][0]["status"],"generated")
        self.assertEqual(self.store.review(self.ident,candidate["id"])["status"],"unreviewed")

    def test_generated_assembly_rejects_stretched_atlas_or_invalid_protection(self):
        for raw,options in ((png((6,5)),dict(scale=4)),
                            (png((5,5)),dict(scale=4,protected_regions=[[.8,0,.4,.3]])),
                            (png((5,5)),dict(scale=0))):
            with self.subTest(options=options):
                with self.assertRaises(w.Invalid):
                    self.store.import_candidate(self.ident,raw,"Invalid","faithful",assembly=options)
        self.assertEqual(self.store.detail(self.ident)["candidates"],[])

    def test_regional_revision_copies_only_edit_boxes_from_generation(self):
        parent=self.store.import_candidate(self.ident,png(colour=(60,90,120,180)),"Parent","faithful")
        candidate=self.store.import_candidate(self.ident,png((5,5),(200,100,50,1)),"Targeted","faithful",parent=parent["id"],
            assembly=dict(scale=4,preserve_alpha=True,edited_regions=[[0,0,.5,.5]]))
        with Image.open(self.store.image_path(self.ident,parent["id"])) as prior, Image.open(self.store.image_path(self.ident,candidate["id"])) as result:
            self.assertEqual(result.getpixel((0,0)),(200,100,50,180))
            self.assertEqual(result.crop((4,0,8,8)).tobytes(),prior.crop((4,0,8,8)).tobytes())
            self.assertEqual(result.crop((0,4,4,8)).tobytes(),prior.crop((0,4,4,8)).tobytes())
        self.assertEqual(candidate["assembly"]["parent_sha256"],parent["sha256"])
        self.assertEqual(candidate["assembly"]["edited_pixel_boxes"],[[0,0,4,4]])

    def test_regional_revision_rejects_missing_changed_or_resized_parent(self):
        options=dict(scale=4,edited_regions=[[0,0,.5,.5]])
        with self.assertRaisesRegex(w.Invalid,"require a parent"):
            self.store.import_candidate(self.ident,png(),"No parent","faithful",assembly=options)
        parent=self.store.import_candidate(self.ident,png(),"Parent","faithful")
        with self.assertRaisesRegex(w.Invalid,"exact resolution"):
            self.store.import_candidate(self.ident,png(),"Resized","faithful",parent=parent["id"],assembly=dict(options,scale=2))
        self.store.image_path(self.ident,parent["id"]).write_bytes(png(colour=(1,2,3,255)))
        with self.assertRaisesRegex(w.Invalid,"Parent candidate checksum"):
            self.store.import_candidate(self.ident,png(),"Changed","faithful",parent=parent["id"],assembly=options)

    def test_export_requires_hash_bound_selection_and_retains_originals(self):
        original=(self.corpus/"original.png").read_bytes()
        a=self.store.import_candidate(self.ident,png(),"A","faithful")
        with self.assertRaises(w.Invalid):self.store.export_pack()
        r=w.empty_review();r.update(status="approved",selected=True)
        with self.assertRaises(w.Invalid):self.store.save_review(self.ident,a["id"],r)
        self.approve(a)
        result=self.store.export_pack();output=Path(result["path"])
        manifest=(output/result["packs"][0]/"manifest.ini").read_text()
        self.assertIn("png_mips=channels",manifest)
        self.assertIn("b"*64+"=textures/"+self.ident+".png",manifest)
        self.assertEqual((output/result["packs"][0]/"textures"/(self.ident+".png")).read_bytes(),png())
        self.assertFalse((output/result["packs"][0]/"original.png").exists())
        self.assertEqual((self.corpus/"original.png").read_bytes(),original)
        self.store.image_path(self.ident,a["id"]).write_bytes(png(colour=(0,0,0,255)))
        with self.assertRaisesRegex(w.Invalid,"changed"):self.store.export_pack()

    def test_selection_moves_to_one_revision_and_modified_review_needs_reselection(self):
        a=self.store.import_candidate(self.ident,png(),"A","faithful")
        b=self.store.import_candidate(self.ident,png(),"B","remaster")
        self.approve(a);self.approve(b)
        self.assertFalse(self.store.review(self.ident,a["id"])["selected"])
        self.assertTrue(self.store.review(self.ident,b["id"])["selected"])
        r=self.store.review(self.ident,b["id"]);r["status"]="needs_revision"
        with self.assertRaises(w.Invalid):self.store.save_review(self.ident,b["id"],r)
        r["selected"]=False;self.store.save_review(self.ident,b["id"],r)
        with self.assertRaises(w.Invalid):self.store.export_pack()

    def test_queue_retains_exact_scope_and_faces_policy(self):
        r=dict(w.empty_review(),notes="Verify jersey spelling")
        self.store.save_review(self.ident,"asset",r)
        queued=self.store.queue_request(self.ident,"remaster","asset","")
        self.assertIn("Preserve faces and likeness",queued["prompt"])
        self.assertIn("Verify jersey spelling",queued["prompt"])
        self.assertEqual(w.Workshop(self.corpus,self.work).data["requests"][0],queued)

    def test_revision_queue_uses_parent_image_and_hash_as_edit_target(self):
        c=self.store.import_candidate(self.ident,png(),"Parent","faithful")
        item=self.store.queue_request(self.ident,"faithful",c["id"],"Only refine denim")
        self.assertIn("selected candidate revision "+c["id"],item["prompt"])
        self.assertEqual(item["parent_sha256"],c["sha256"])
        self.assertEqual(Path(item["parent_image"]).read_bytes(),png())

    def test_candidate_flags_notes_and_regions_are_searchable_in_catalog(self):
        c=self.store.import_candidate(self.ident,png(),"Detail","remaster")
        r=dict(w.empty_review(),flag=True,notes="verify inscription",regions=[dict(id="x",rect=[0,0,.2,.2],kind="reference",note="tattoo glyph")])
        self.store.save_review(self.ident,c["id"],r)
        for params in ({"status":["flagged"]},{"status":["noted"]},{"q":["inscription"]},{"q":["tattoo glyph"]}):
            self.assertEqual(self.store.catalog(params)["total"],1)

    def test_queue_rejects_changed_original_before_generation(self):
        self.store.assets[self.ident]["original_hash"]=w.sha((self.corpus/"original.png").read_bytes())
        (self.corpus/"original.png").write_bytes(png((2,2),(1,2,3,255)))
        with self.assertRaisesRegex(w.Invalid,"corpus before generation"):
            self.store.queue_request(self.ident,"faithful","asset","")
        self.assertEqual(self.store.data["requests"],[])

    def test_other_corpus_is_rejected_without_resetting_review(self):
        before=self.store.file.read_bytes()
        raw=json.loads((self.corpus/"corpus.json").read_text());raw["corpus_id"]="d"*64
        (self.corpus/"corpus.json").write_text(json.dumps(raw))
        with self.assertRaises(w.Invalid):w.Workshop(self.corpus,self.work)
        self.assertEqual(self.store.file.read_bytes(),before)

    def test_source_path_escape_is_rejected(self):
        self.store.assets[self.ident]["original"]="../outside.png"
        with self.assertRaises(w.Invalid):self.store.image_path(self.ident,"original")

    def test_workspace_process_lock_rejects_second_writer(self):
        with w.WorkspaceLock(self.work):
            with self.assertRaises(w.Invalid):
                with w.WorkspaceLock(self.work):pass
        with w.WorkspaceLock(self.work):pass

    def test_http_authorization_and_durable_post(self):
        server=w.ThreadingHTTPServer(("127.0.0.1",0),w.handler_for(self.store,"test-token"))
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        self.addCleanup(server.server_close);self.addCleanup(server.shutdown)
        base="http://127.0.0.1:"+str(server.server_port)
        with urlopen(base+"/api/config") as response:self.assertEqual(json.load(response)["token"],"test-token")
        payload=json.dumps(dict(w.empty_review(),notes="HTTP persistence")).encode()
        with self.assertRaises(HTTPError) as failure:urlopen(Request(base+"/api/review/"+self.ident+"/asset",data=payload))
        self.assertEqual(failure.exception.code,403)
        headers={"Content-Type":"application/json","X-Workshop-Token":"test-token","Origin":"https://other.example"}
        with self.assertRaises(HTTPError):urlopen(Request(base+"/api/review/"+self.ident+"/asset",data=payload,headers=headers))
        headers["Origin"]=base
        with urlopen(Request(base+"/api/review/"+self.ident+"/asset",data=payload,headers=headers)) as response:
            self.assertEqual(json.load(response)["version"],1)
        self.assertEqual(w.Workshop(self.corpus,self.work).review(self.ident)["notes"],"HTTP persistence")
        with self.assertRaises(HTTPError):urlopen(Request(base+"/api/config",headers={"Host":"untrusted.example"}))


if __name__=="__main__":unittest.main()
