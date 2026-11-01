import unittest
import numpy as np
from PIL import Image
from defjam_tools import region_detail as r


class RegionDetailTests(unittest.TestCase):
    def setUp(self):
        a=np.zeros((128,128,4),np.uint8);a[:]=[150,105,75,143];a[50:75,50:75,:3]=15
        self.parent=Image.fromarray(a);self.mask=np.zeros((128,128),bool);self.mask[10:118,10:118]=True
        self.guard=np.zeros((128,128));self.guard[:,60:65]=1
        yy,xx=np.mgrid[:128,:128];v=np.where((xx+yy)%2,110,140).astype(np.uint8)
        self.generated=Image.fromarray(np.repeat(v[...,None],3,axis=-1))

    def test_grain_holds_other_material_alpha_letters_and_seams(self):
        out,report=r.grain(self.parent,self.generated,self.mask,self.guard,[(20,20,40,40)])
        a,b=np.asarray(self.parent),np.asarray(out)
        self.assertTrue(all(report['checks'].values()))
        self.assertGreater(report['changed_pixels'],100)
        self.assertTrue(np.array_equal(a[20:40,20:40],b[20:40,20:40]))
        self.assertTrue(np.array_equal(a[52:58,52:58],b[52:58,52:58]))

    def test_direct_crop_holds_actual_materials_and_text(self):
        out,report=r.patch(self.parent,self.parent,self.generated,(0,0,128,128),self.mask,self.guard,[(25,25,50,50)])
        self.assertTrue(all(report['checks'].values()))
        self.assertTrue(np.array_equal(np.asarray(out)[25:50,25:50],np.asarray(self.parent)[25:50,25:50]))

    def test_locked_crop_cannot_repaint_outside_original_ink(self):
        out,report=r.patch(self.parent,self.parent,self.generated,(0,0,128,128),self.mask,self.guard,method='source-locked')
        a,b=np.asarray(self.parent),np.asarray(out);changed=np.any(a!=b,axis=-1)
        self.assertGreater(changed.sum(),0)
        self.assertFalse(changed[:50].any());self.assertFalse(changed[75:].any())
        self.assertTrue(all(report['checks'].values()))

    def test_bad_mask_and_guard_rejected(self):
        with self.assertRaises(ValueError):r.grain(self.parent,self.generated,self.mask.astype(float),self.guard)
        bad=self.guard.copy();bad[0,0]=float('nan')
        with self.assertRaises(ValueError):r.grain(self.parent,self.generated,self.mask,bad)

    def test_rounding_tolerance_does_not_allow_a_reframed_crop(self):
        out,report=r.patch(self.parent,self.parent,self.generated.resize((256,255)),
                            (0,0,128,128),self.mask,self.guard,method='source-locked')
        self.assertTrue(all(report['checks'].values()))
        self.assertLess(report['aspect_rounding_error'],.005)
        with self.assertRaises(ValueError):
            r.patch(self.parent,self.parent,self.generated.resize((128,100)),
                    (0,0,128,128),self.mask,self.guard,method='source-locked')


if __name__=='__main__':unittest.main()
