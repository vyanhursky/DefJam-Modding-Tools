"""Synthetic UV/orientation/depth checks; no game model or image fixtures."""
import unittest
from PIL import Image
import numpy as np
from defjam_tools.uv_preview import render


def plane(z):return dict(group='cloth',positions=[[-1,1,z],[1,1,z],[-1,-1,z],[1,-1,z]],uv=[[0,0],[1,0],[0,1],[1,1]],indices=[0,1,2,2,1,3])


class UVPreviewTests(unittest.TestCase):
    def test_top_left_uvs_and_back_view_mirroring(self):
        t=Image.fromarray(np.array([[[200,0,0],[0,200,0]],[[0,0,200],[200,200,0]]],dtype='uint8'));g=dict(schema=1,meshes=[plane(0)])
        a=render(g,t,bounds=(-1,-1,1,1),size=(8,8));b=render(g,t,view='back',bounds=(-1,-1,1,1),size=(8,8))
        self.assertEqual(a.getpixel((1,1)),(200,0,0));self.assertEqual(a.getpixel((1,6)),(0,0,200));self.assertEqual(b.getpixel((6,1)),(200,0,0))

    def test_default_framing_preserves_model_aspect(self):
        g=dict(schema=1,bounds=[[-1,-1,0],[1,1,0]],meshes=[plane(0)])
        out=np.asarray(render(g,Image.new('RGB',(2,2),'red'),size=(16,32)))
        yy,xx=np.where(out[...,0]==255)
        self.assertLessEqual(abs((xx.max()-xx.min())-(yy.max()-yy.min())),1)

    def test_nearest_surface_wins_and_rgb_is_independent_of_alpha(self):
        near=plane(1);far=plane(-1);near['uv']=[[0,0]]*4;far['uv']=[[.9,0]]*4
        t=Image.new('RGBA',(2,1));t.putdata([(200,0,0,0),(0,0,200,255)]);g=dict(schema=1,meshes=[near,far])
        self.assertEqual(render(g,t,bounds=(-1,-1,1,1),size=(8,8)).getpixel((3,3)),(200,0,0))
        self.assertEqual(render(g,t,view='back',bounds=(-1,-1,1,1),size=(8,8)).getpixel((3,3)),(0,0,200))

if __name__=='__main__':unittest.main()
