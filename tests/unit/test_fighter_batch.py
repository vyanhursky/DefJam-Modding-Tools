"""Material/seam invariants for bulk assembly, using invented triangle data."""
import copy
import importlib.util
from pathlib import Path
import unittest
import numpy as np

p=Path(__file__).resolve().parents[2]/'research/fighters-batch10-20261029/assemble.py'
spec=importlib.util.spec_from_file_location('fighter_batch_recipe',p)
recipe=importlib.util.module_from_spec(spec);spec.loader.exec_module(recipe)


def tri(group,uv):
    return dict(group=group,positions=[[0,0,0],[1,0,0],[0,1,0]],uv=uv,indices=[0,1,2])


class BatchScopesTests(unittest.TestCase):
    def test_auxiliary_and_unknown_materials_hold_shared_cloth_coverage(self):
        g=dict(meshes=[tri('emc4_cloth1',[[0,0],[1,0],[0,1]]),tri('eyelid_ALPHA_MatAlph',[[.1,.1],[.3,.1],[.1,.3]]),tri('unknown',[[.4,.1],[.6,.1],[.4,.3]])])
        allowed,groups,seams=recipe.scopes(g,64)
        self.assertTrue(allowed[2,2]);self.assertFalse(allowed[10,10]);self.assertFalse(allowed[10,29]);self.assertFalse(allowed[63,63]);self.assertEqual(seams,[])
        self.assertIn('emc4_cloth1',groups)

    def test_only_distinct_paired_skin_uv_edges_create_bilateral_guards(self):
        a=tri('emc2_skin',[[.01,.01],[.3,.01],[.01,.3]])
        b=tri('emc2_skin',[[.55,.55],[.9,.55],[.55,.9]])
        _,_,seams=recipe.scopes(dict(meshes=[a,b]),64)
        self.assertEqual(len(seams),6) # three paired edges, both atlas sides
        _,_,continuous=recipe.scopes(dict(meshes=[a,copy.deepcopy(a)]),64)
        self.assertEqual(continuous,[])
        c=tri('emc2_skin',[[.4,.4],[.5,.4],[.4,.5]])
        _,_,ambiguous=recipe.scopes(dict(meshes=[a,b,c]),64)
        self.assertEqual(ambiguous,[]) # no guessed match among three UV sides

    def test_invalid_uv_cannot_create_unbounded_masks(self):
        with self.assertRaises(ValueError):
            recipe.scopes(dict(meshes=[tri('emc2_skin',[[0,0],[float('nan'),0],[0,1]])]),64)

if __name__=='__main__':unittest.main()
