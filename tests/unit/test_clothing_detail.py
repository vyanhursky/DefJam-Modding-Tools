import unittest
import numpy as np
from PIL import Image
from defjam_tools.clothing_detail import repair


class ClothingDetailTests(unittest.TestCase):
    def setUp(self):
        uv = [[.05,.05],[.95,.05],[.95,.95],[.05,.95]]
        self.geometry = dict(schema=1, meshes=[
            dict(group='emc4_cloth', uv=uv, indices=[0,1,2,0,2,3]),
            dict(group='emc1_eye', uv=[[.35,.35],[.65,.35],[.5,.65]], indices=[0,1,2])])
        self.source = Image.new('RGBA', (128,128), (85,95,110,170))
        raw = np.asarray(self.source.convert('RGB')).copy()
        raw[::3, :, :] = (95,102,120)
        raw[:, ::5, :] = (75,85,100)
        self.raw = Image.fromarray(raw)

    def test_repair_is_limited_by_material_and_requested_region(self):
        result, report, mask = repair(self.source, self.source, self.raw, self.geometry,
                                       (0,0,128,128), [(0,0,80,128)], source_size=32)
        a, b, m = np.asarray(self.source), np.asarray(result), np.asarray(mask)>0
        self.assertTrue(report['checks']['alpha_exact'])
        self.assertTrue(report['checks']['outside_repair_exact'])
        self.assertTrue(np.array_equal(a[~m], b[~m]))
        self.assertFalse(m[:,80:].any())
        self.assertFalse(m[56,64])  # overlapping eye triangle is held
        self.assertGreater(report['changed_pixels'], 500)

    def test_invalid_or_empty_regions_fail_without_output(self):
        for boxes in [[], [(0,0,129,128)], [(0,0,1,1)]]:
            with self.subTest(boxes=boxes), self.assertRaises(ValueError):
                repair(self.source, self.source, self.raw, self.geometry,
                       (0,0,128,128), boxes, source_size=32)


if __name__ == '__main__':
    unittest.main()
