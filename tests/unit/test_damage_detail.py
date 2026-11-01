"""Synthetic invariants for registered supplemental injury assembly."""
import unittest
import numpy as np
from PIL import Image
from defjam_tools.damage_detail import restore


class DamageDetailTests(unittest.TestCase):
    def inputs(self):
        clean = np.full((16, 16, 4), [130, 100, 80, 255], dtype='uint8')
        state = clean.copy(); state[4:8, 4:8, :3] = [100, 65, 60]
        state[5, 5, 3] = 73
        im = lambda a: Image.fromarray(a)
        hd = lambda a: im(a).resize((64, 64), Image.Resampling.NEAREST)
        restored = np.asarray(hd(clean)).copy(); restored[..., 0] += 2
        yy, xx = np.indices((64, 64)); raw = np.full((64, 64, 3), 120, dtype='uint8')
        raw[(xx + yy) % 2 == 0] = 150
        return [im(state), im(clean), hd(state), hd(clean), im(restored), im(raw)]

    def test_state_alpha_holds_and_clean_exterior_survive(self):
        args = self.inputs(); out, report, masks = restore(*args,
            held_source_boxes=[[4, 4, 5, 5]])
        a, b, c = np.asarray(out), np.asarray(args[2]), np.asarray(args[4])
        np.testing.assert_array_equal(a[..., 3], b[..., 3])
        np.testing.assert_array_equal(a[masks['held']], b[masks['held']])
        outside = ~masks['transition'] & ~masks['held']
        np.testing.assert_array_equal(a[outside, :3], c[outside, :3])
        self.assertGreater(report['generated_detail_pixels'], 0)
        self.assertTrue(all(report['checks'].values()))

    def test_generated_marks_outside_source_changes_cannot_transfer(self):
        args = self.inputs(); first, _, masks = restore(*args)
        raw = np.asarray(args[-1]).copy(); raw[:4, :4] = [250, 0, 0]
        args[-1] = Image.fromarray(raw); second, _, _ = restore(*args)
        np.testing.assert_array_equal(np.asarray(first), np.asarray(second))
        np.testing.assert_array_equal(np.asarray(second)[~masks['detail_active']],
                                      np.asarray(masks['baseline'])[~masks['detail_active']])

    def test_mismatched_registration_and_empty_state_rejected(self):
        args = self.inputs(); args[0] = args[1]
        with self.assertRaisesRegex(ValueError, 'registration'):
            restore(*args)
        args = self.inputs(); args[0] = Image.new('RGBA', (16, 16), (20, 20, 20, 255))
        with self.assertRaisesRegex(ValueError, 'registration'):
            restore(*args)

    def test_invalid_holds_and_nonmatching_dimensions_rejected(self):
        args = self.inputs()
        with self.assertRaisesRegex(ValueError, 'Held tile'):
            restore(*args, held_source_boxes=[[0, 0, 17, 2]])
        args[4] = Image.new('RGBA', (32, 32))
        with self.assertRaisesRegex(ValueError, 'reference crops'):
            restore(*args)

    def test_small_palette_registration_requires_explicit_bounded_opt_in(self):
        args = self.inputs()
        state = np.array(args[0]); state[9:, :, 0] += 1
        args[0] = Image.fromarray(state)
        args[2] = args[0].resize((64, 64), Image.Resampling.NEAREST)
        with self.assertRaisesRegex(ValueError, 'registration'):
            restore(*args)
        out, report, masks = restore(*args, registration_rgb_tolerance=3)
        self.assertLess(report['registration_unchanged_rgb_fraction'], .75)
        self.assertGreaterEqual(report['registration_close_rgb_fraction'], .8)
        self.assertTrue(masks['source_support'][40, 0])
        np.testing.assert_array_equal(np.asarray(out)[..., 3],
                                      np.asarray(args[2])[..., 3])

    def test_palette_opt_in_does_not_accept_large_changes_or_unbounded_tolerance(self):
        args = self.inputs(); state = np.array(args[0]); state[9:, :, 0] += 20
        args[0] = Image.fromarray(state)
        with self.assertRaisesRegex(ValueError, 'registration'):
            restore(*args, registration_rgb_tolerance=3)
        for invalid in (4, -1, True, 1.5):
            with self.assertRaisesRegex(ValueError, 'tolerance'):
                restore(*self.inputs(), registration_rgb_tolerance=invalid)


if __name__ == '__main__':
    unittest.main()
