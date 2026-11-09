import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('export_portable',ROOT/'tools/export_portable.py')
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class PortableTests(unittest.TestCase):
    def test_all_roles_and_only_public_allowlisted_files(self):
        with tempfile.TemporaryDirectory() as temp:
            dest=Path(temp)
            catalog=module.build(dest)
            self.assertEqual(len(catalog),8)
            managed=json.loads((ROOT/'managed-files.json').read_text())
            for role in catalog:
                self.assertIn('text-only',role['prompt'])
                self.assertTrue(all(p in managed and '.local.' not in p for p in role['sources']))
                for path in role['sources']:
                    if path.endswith('.md'):
                        self.assertIn(module.portable_links((ROOT/path).read_text(encoding='utf-8-sig'),path),role['prompt'])
            invest=next(r for r in catalog if r['id']=='_invest')
            self.assertIn('等待用户明确确认',invest['prompt'])
            with zipfile.ZipFile(dest/'portable-agents.zip') as archive:
                self.assertEqual(len(archive.namelist()),11)
                self.assertIn('LICENSE',archive.namelist())

if __name__=='__main__': unittest.main()
