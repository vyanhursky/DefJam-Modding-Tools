"""The single packaged catalogue preserves existing IDs and rejects ambiguity."""
import copy
import hashlib
import json
from pathlib import Path
import unittest
from defjam_tools import fighter_catalog as c

class FighterCatalogTests(unittest.TestCase):
    def test_legacy_inventory_contract_exact(self):
        expected=json.loads(Path(__file__).with_name('fighter_catalog_contract.json').read_text())
        values=dict(fighters=list(c.FIGHTERS.items()),pilot=c.PILOT,archives=c.MODEL_ARCHIVES)
        for name,value in values.items():
            self.assertEqual(hashlib.sha256(json.dumps(value,sort_keys=True).encode()).hexdigest(),expected[name],name)

    def test_invalid_or_ambiguous_catalogues(self):
        def alias(d):d['entries'].append(copy.deepcopy(d['entries'][0]))
        def source(d):d['entries'][1]['preview']['source_id']=d['entries'][0]['preview']['source_id']
        def order(d):d['entries'][0]['preview']['order']=1000
        def route(d):d['entries'][0]['preview']['archive']=['../escape.viv','assets/A.viv']
        def unknown(d):d['entries'][0]['accidental_approval']=True
        def omission(d):d['preview_omissions'][0]['source_id']='f'*64
        def reason(d):d['preview_omissions'][0]['reason']=''
        for mutate in (alias,source,order,route,unknown,omission,reason):
            with self.subTest(mutate=mutate.__name__):
                data=copy.deepcopy(c.CATALOG);mutate(data)
                with self.assertRaises(ValueError):c.validate_catalog(data)

    def test_source_specific_exception_never_applies_to_another_fighter(self):
        shawnna=c.FIGHTERS['shawnna'][2]
        self.assertIsNotNone(c.preview_omission('tape',{'A406,1'},shawnna))
        self.assertIsNone(c.preview_omission('tape',{'A406,1'},c.FIGHTERS['blaze'][2]))
        self.assertIsNone(c.preview_omission('tape',{'A406,1','other'},shawnna))
