"""Prevent held feature omissions and accidental alpha-cloth RGB exclusion."""
import unittest
import numpy as np
from defjam_tools.fighter_scopes import scopes,feature_coverage,include_unmapped_features


def tri(group):return dict(group=group,positions=[[0,0,0],[1,0,0],[0,1,0]],uv=[[0,0],[1,0],[0,1]],indices=[0,1,2])


class FighterScopeTests(unittest.TestCase):
    def test_alpha_cloth_needs_explicit_rgb_optin(self):
        group='emc4_cloth_ALPHA_MatAlph';g=dict(meshes=[tri(group)])
        self.assertFalse(scopes(g,64)[0].any());self.assertTrue(scopes(g,64,[group])[0][2,2])
        with self.assertRaises(ValueError):scopes(g,64,['emc1_eye_ALPHA'])

    def test_unmapped_source_tile_cannot_override_mapped_material_hold(self):
        allowed=np.zeros((32,32),bool);covered=allowed.copy();covered[:8,:8]=True
        row=dict(source_box=[16,16,24,24],reason='Verified source flag, no static UV coverage')
        out=include_unmapped_features(allowed,{'eye':covered},[row]);self.assertTrue(out[18,18]);self.assertFalse(out[2,2])
        with self.assertRaises(ValueError):include_unmapped_features(allowed,{'eye':covered},[dict(row,source_box=[0,0,8,8])])

    def test_global_changes_cannot_hide_one_unrestored_logo_half(self):
        before=np.zeros((32,32,4),dtype='uint8');after=before.copy();after[:16,:,0]=200
        features=[dict(name='left half',source_box=[0,0,16,16]),dict(name='right half',source_box=[0,16,16,32])]
        with self.assertRaisesRegex(ValueError,'right half'):feature_coverage(before,after,features,1)
        features[1]['status']='held';report=feature_coverage(before,after,features,1)
        self.assertEqual(report[1]['status'],'pending-held')

if __name__=='__main__':unittest.main()
