"""Product boundary and migration regressions; synthetic data, no model calls."""
from pathlib import Path
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
import tomllib
import unittest

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {"_manuel", "_mantou"}
LEGACY = {"_wayne", "_clayton", "_alan", "_jim", "_factbot", "_invest"}


class PublishedBoundaryTests(unittest.TestCase):
    def test_only_two_registered_configs_and_no_hidden_roles(self):
        files = list((ROOT / "agents").rglob("*.toml"))
        self.assertEqual({p.relative_to(ROOT / "agents").as_posix() for p in files},
                         {name + ".toml" for name in EXPECTED})
        self.assertEqual({tomllib.loads(p.read_text(encoding="utf-8"))["name"] for p in files}, EXPECTED)
        manifest = json.loads((ROOT / "managed-files.json").read_text(encoding="utf-8"))
        self.assertEqual({p.split('/')[1].removesuffix('.toml') for p in manifest}, EXPECTED)

    def test_current_guides_do_not_offer_retired_invocations(self):
        files = list((ROOT / 'agents').rglob('*.md')) + list((ROOT / 'docs').rglob('*.md')) + [ROOT / 'README.md']
        for path in files:
            if 'history' in path.parts or path.name in {'CHANGELOG.md', 'migration.md'}:
                continue
            text = path.read_text(encoding='utf-8')
            for name in LEGACY:
                for marker in [f'调用 {name}', f'调用 `{name}`', f'-Agent {name}']:
                    self.assertNotIn(marker, text, str(path))

    def test_legacy_registry_has_only_retired_names_and_sha256(self):
        registry = json.loads((ROOT/'migration/legacy-agent-hashes.json').read_text())
        self.assertEqual(set(registry), LEGACY)
        for hashes in registry.values():
            self.assertTrue(hashes)
            for value in hashes:
                self.assertRegex(value, r'^[A-F0-9]{64}$')

    def test_github_templates_only_offer_current_agents(self):
        for path in (ROOT/'.github').rglob('*'):
            if path.is_file():
                names = set(re.findall(r'\b_(?:manuel|mantou|wayne|clayton|alan|jim|factbot|invest)\b', path.read_text(encoding='utf-8')))
                self.assertFalse(names & LEGACY, str(path))


@unittest.skipUnless(shutil.which('pwsh'), 'PowerShell required')
class MigrationTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix='two-agent-migration-')
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.package = self.root/'package'
        self.home = self.root/'home'
        self.package.mkdir()
        (self.package/'migration').mkdir()
        shutil.copy2(ROOT/'migrate-legacy.ps1', self.package/'migrate-legacy.ps1')
        self.original = b'name = "synthetic-retired"\n'
        self.modified = b'name = "user-customized"\n'
        self.registry = {name:[hashlib.sha256(self.original).hexdigest().upper()] for name in LEGACY}
        (self.package/'migration/legacy-agent-hashes.json').write_text(json.dumps(self.registry))
        self.write('agents/_wayne.toml', self.original)
        self.write('agents/_invest.toml', self.modified)
        self.write('agents/unrelated.toml', b'keep-unrelated')
        self.write('agents/_wayne/source.local.json', b'{"epub":"synthetic-private-book"}')
        self.write('agents/_invest/knowledge-map.local.md', b'private-investment-index')
        self.write('agents/_wayne/custom.md', b'private-note')

    def write(self, relative, data):
        path = self.home/relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)

    def snapshot(self):
        return {p.relative_to(self.home).as_posix():p.read_bytes() for p in self.home.rglob('*') if p.is_file()}

    def run_migration(self, *args):
        env = dict(os.environ, CODEX_HOME=str(self.home))
        return subprocess.run(['pwsh','-NoProfile','-File',str(self.package/'migrate-legacy.ps1'),*args],
                              env=env,capture_output=True,text=True,encoding='utf-8',timeout=30)

    def test_preview_backup_idempotence_and_modified_private_preservation(self):
        before = self.snapshot()
        result = self.run_migration('-WhatIf')
        self.assertEqual(result.returncode, 0, result.stdout+result.stderr)
        self.assertEqual(self.snapshot(), before)
        self.assertFalse((self.home/'agent-migration-backups').exists())
        result = self.run_migration()
        self.assertEqual(result.returncode, 0, result.stdout+result.stderr)
        self.assertFalse((self.home/'agents/_wayne.toml').exists())
        self.assertEqual((self.home/'agents/_invest.toml').read_bytes(), self.modified)
        self.assertIn('Preserved modified or unrecognized config', result.stdout)
        for name in ['agents/unrelated.toml','agents/_wayne/source.local.json',
                     'agents/_invest/knowledge-map.local.md','agents/_wayne/custom.md']:
            self.assertEqual((self.home/name).read_bytes(), before[name])
        self.assertEqual((self.home/'agents/_manuel/books/research/source.local.json').read_bytes(),
                         before['agents/_wayne/source.local.json'])
        backups=list((self.home/'agent-migration-backups').glob('*/_wayne.toml'))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_bytes(), self.original)
        after=self.snapshot()
        self.assertEqual(self.run_migration().returncode, 0)
        self.assertEqual(self.snapshot(), after)

    def test_existing_private_destination_is_never_overwritten(self):
        relative='agents/_manuel/books/research/source.local.json'
        self.write(relative, b'newer-private-config')
        result=self.run_migration()
        self.assertEqual(result.returncode, 0, result.stdout+result.stderr)
        self.assertEqual((self.home/relative).read_bytes(), b'newer-private-config')
        self.assertIn('Preserved existing destination', result.stdout)

    def test_malformed_source_path_stops_before_any_retirement(self):
        (self.home/'agents/_wayne/source.local.json').unlink()
        (self.home/'agents/_wayne/source.local.json').mkdir()
        result=self.run_migration()
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual((self.home/'agents/_wayne.toml').read_bytes(), self.original)
        self.assertFalse((self.home/'agent-migration-backups').exists())

    def test_all_recognized_legacy_roles_retire_and_leave_two_current_roles(self):
        for name in LEGACY:
            self.write(f'agents/{name}.toml', self.original)
        for name in EXPECTED:
            self.write(f'agents/{name}.toml', f'name = "{name}"'.encode())
        result=self.run_migration()
        self.assertEqual(result.returncode, 0, result.stdout+result.stderr)
        self.assertEqual({p.stem for p in (self.home/'agents').glob('*.toml')},EXPECTED|{'unrelated'})
        self.assertEqual(len(list((self.home/'agent-migration-backups').glob('*/*.toml'))),6)
