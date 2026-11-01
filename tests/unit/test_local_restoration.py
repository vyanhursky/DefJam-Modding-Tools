"""Synthetic local-model assembly invariants; no Torch or game assets needed."""
import unittest
import numpy as np
from PIL import Image
from defjam_tools.local_restoration import assemble


class LocalRestorationTests(unittest.TestCase):
    def inputs(self):
        own = np.full((64, 64, 4), [130, 100, 80, 255], np.uint8)
        own[20:25, 20:25, 3] = 73
        raw = own[..., :3].copy()
        yy, xx = np.indices((64, 64))
        raw[(xx + yy) % 2 == 0] = [180, 130, 100]
        return Image.fromarray(own), Image.fromarray(raw)

    def test_alpha_tiles_and_seam_core_remain_own_RGBA(self):
        own, raw = self.inputs()
        out, report, masks = assemble(own, raw, 16, [[4, 4, 6, 6]],
            seams=[dict(body=[[.5, 0], [.5, 1]])])
        a, b = np.asarray(out), np.asarray(own)
        np.testing.assert_array_equal(a[..., 3], b[..., 3])
        np.testing.assert_array_equal(a[masks['held']], b[masks['held']])
        np.testing.assert_array_equal(a[masks['seam_core']], b[masks['seam_core']])
        self.assertGreater(report['changed_pixels'], 0)
        self.assertEqual(report['imagegen_calls'], 0)

    def test_flat_model_color_shift_does_not_replace_source_palette(self):
        own, _ = self.inputs()
        raw = Image.new('RGB', own.size, (180, 130, 100))
        with self.assertRaisesRegex(ValueError, 'No local detail'):
            assemble(own, raw, 16)

    def test_unregistered_dimensions_and_invalid_holds_rejected(self):
        own, raw = self.inputs()
        with self.assertRaisesRegex(ValueError, 'registered'):
            assemble(own, raw.resize((32, 32)), 16)
        with self.assertRaisesRegex(ValueError, 'Protected'):
            assemble(own, raw, 16, [[0, 0, 17, 2]])


if __name__ == '__main__':
    unittest.main()
