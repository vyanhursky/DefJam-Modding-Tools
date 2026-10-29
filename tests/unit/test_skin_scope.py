import unittest
import numpy as np
from defjam_tools.skin_scope import rasterize


class SkinScopeTests(unittest.TestCase):
    def setUp(self):
        self.mesh=dict(group='emc2_skin',rm=1,positions=[[0,0,1],[1,0,1],[1,1,1],[0,1,1]],
                       uv=[[.1,.1],[.9,.1],[.9,.9],[.1,.9]],indices=[0,1,2,0,2,3])
        self.g=dict(schema=1,meshes=[self.mesh])

    def test_clips_crossing_triangles_at_world_plane(self):
        mask,parts=rasterize(self.g,64,[(1,.5,True)])
        self.assertFalse(mask[20,32]);self.assertTrue(mask[45,32])
        self.assertEqual(parts[0]['triangles'],[0,1])

    def test_uv_and_world_clips_intersect(self):
        mask,_=rasterize(self.g,64,[(1,.5,True),(3,.5,False)])
        self.assertTrue(mask[45,20]);self.assertFalse(mask[45,45])

    def test_explicit_skin_island_is_unioned(self):
        mask,_=rasterize(self.g,64,[(1,2,True)],{1:[0]})
        self.assertTrue(mask.any());self.assertFalse(mask[50,10])
        other=dict(self.mesh,group='emc4_cloth');empty,_=rasterize(dict(schema=1,meshes=[other]),64,[],{1:[0]})
        self.assertFalse(empty.any())

    def test_bad_triangle_and_planes_rejected(self):
        with self.assertRaises(ValueError):rasterize(self.g,64,[(8,0,True)])
        with self.assertRaises(ValueError):rasterize(self.g,64,[],{1:[9]})


if __name__=='__main__':unittest.main()
