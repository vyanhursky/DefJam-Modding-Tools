"""Synthetic checks for feature restoration, including a logo at atlas edge."""
import unittest
import numpy as np
from PIL import Image
from defjam_tools.feature_detail import restore


class FeatureDetailTests(unittest.TestCase):
    def setUp(self):
        self.ref=Image.new('RGBA',(64,64),(60,75,100,117))
        yy,xx=np.mgrid[:64,:64];rgb=np.zeros((64,64,3),dtype='uint8')
        rgb[:]=[105,90,100];rgb[((xx//2+yy//2)%2)==0]=[75,60,70]
        self.generated=Image.fromarray(rgb);self.mask=np.zeros((64,64),bool);self.mask[8:56,:30]=True

    def test_named_detail_changes_at_atlas_edge_but_never_other_material_or_alpha(self):
        out,r=restore(self.ref,self.ref,self.generated,(0,0,64,64),self.mask,
                      source_size=64,radius_source=3,feather_source=1)
        a=np.asarray(self.ref);b=np.asarray(out)
        self.assertTrue(all(r['checks'].values()));self.assertTrue(np.array_equal(a[~self.mask],b[~self.mask]));self.assertTrue(np.array_equal(a[...,3],b[...,3]))
        self.assertTrue(np.any(a[20:40,0,:3]!=b[20:40,0,:3]))
        self.assertGreater(r['changed_pixels'],500)

    def test_local_source_palette_removes_broad_cast_without_erasing_detail(self):
        out,_=restore(self.ref,self.ref,self.generated,(0,0,64,64),self.mask,source_size=64,radius_source=3,feather_source=0)
        a=np.asarray(self.ref)[self.mask,:3].mean(0);b=np.asarray(out)[self.mask,:3].mean(0)
        before=np.asarray(self.generated)[self.mask].mean(0)
        self.assertLess(np.linalg.norm(a-b),np.linalg.norm(a-before)*.2)
        self.assertGreater(np.asarray(out)[self.mask,0].std(),3)

    def test_empty_mask_changed_aspect_and_alpha_mismatch_fail_closed(self):
        with self.assertRaises(ValueError):restore(self.ref,self.ref,self.generated,(0,0,64,64),np.zeros_like(self.mask),source_size=64)
        with self.assertRaises(ValueError):restore(self.ref,self.ref,self.generated.resize((64,32)),(0,0,64,64),self.mask,source_size=64)
        other=self.ref.copy();other.putpixel((3,3),(60,75,100,118))
        with self.assertRaises(ValueError):restore(self.ref,other,self.generated,(0,0,64,64),self.mask,source_size=64)

if __name__=='__main__':unittest.main()
