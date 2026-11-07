import copy
import json
from pathlib import Path
import tempfile
import unittest
from zipfile import ZipFile

from tools.compatibility import ROOT, TOC, package, propose, stage, official_observation, detect
from unittest.mock import patch


class CompatibilityTests(unittest.TestCase):
    def setUp(self):
        self.state = dict(product='wowf', channel='live', interface=16001,
                          build=70862, addon_version='0.1.0', runtime_ready=False)
        self.toc = '## Interface: 16001\n## Title: FriendlyNameplateGuild\n## Version: 0.1.0\n'
        self.next = dict(product='wowf', channel='live', interface=16002, build=71000)

    def test_interface_bump_updates_both_versions_and_preserves_metadata(self):
        state, toc = propose(self.state, self.next, self.toc)
        self.assertEqual((state['interface'], state['addon_version'], state['build']),
                         (16002, '0.1.1', 71000))
        self.assertIn('## Interface: 16002\n', toc)
        self.assertIn('## Version: 0.1.1\n', toc)
        self.assertIn('## Title: FriendlyNameplateGuild\n', toc)
        self.assertFalse(state['runtime_ready'])

    def test_new_build_with_same_interface_bumps_addon_version_only(self):
        state, toc = propose(self.state, dict(self.next, interface=16001), self.toc)
        self.assertEqual(state['addon_version'], '0.1.1')
        self.assertEqual(state['interface'], 16001)
        self.assertIn('## Interface: 16001\n', toc)

    def test_repeated_observation_is_idempotent(self):
        state, toc = propose(self.state, self.next, self.toc)
        self.assertIsNone(propose(state, self.next, toc))

    def test_inputs_are_not_mutated(self):
        original = copy.deepcopy((self.state, self.next))
        propose(self.state, self.next, self.toc)
        self.assertEqual((self.state, self.next), original)

    def test_reject_wrong_product_channel_and_new_family(self):
        for patch in (dict(product='wow'), dict(product='wow_classic'),
                      dict(channel='beta'), dict(interface=120105), dict(interface=17000)):
            with self.subTest(patch=patch), self.assertRaises(ValueError):
                propose(self.state, dict(self.next, **patch), self.toc)

    def test_reject_non_integer_and_missing_values(self):
        for key in ('interface', 'build'):
            for value in ('16002', True, None, 0, -1, 16002.0):
                with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                    propose(self.state, dict(self.next, **{key: value}), self.toc)
            broken = dict(self.next)
            del broken[key]
            with self.assertRaises(ValueError):
                propose(self.state, broken, self.toc)

    def test_reject_regression_and_same_build_new_interface(self):
        for patch in (dict(build=70000), dict(build=70862), dict(interface=16000)):
            with self.subTest(patch=patch), self.assertRaises(ValueError):
                propose(self.state, dict(self.next, **patch), self.toc)

    def test_reject_mismatched_or_duplicate_toc_metadata(self):
        for toc in (self.toc.replace('16001', '16002'), self.toc.replace('0.1.0', '0.2.0'),
                    self.toc + '## Interface: 16001\n', self.toc + '## Version: 0.1.0\n',
                    '## Title: Missing metadata\n'):
            with self.subTest(toc=toc), self.assertRaises(ValueError):
                propose(self.state, self.next, toc)

    def test_reject_invalid_semantic_version(self):
        for version in ('v1.2.3', '1.0', '0.1.0-dev', '01.2.3'):
            with self.subTest(version=version), self.assertRaises(ValueError):
                propose(dict(self.state, addon_version=version), self.next, self.toc)

    def test_patch_number_carries_as_semver_not_decimal(self):
        state, _ = propose(dict(self.state, addon_version='1.2.9'), self.next,
                           self.toc.replace('0.1.0', '1.2.9'))
        self.assertEqual(state['addon_version'], '1.2.10')

    def prepare_root(self, root):
        (root / TOC).parent.mkdir(parents=True)
        (root / TOC).write_text(self.toc, encoding='utf-8')
        (root / 'compatibility.json').write_text(json.dumps(self.state), encoding='utf-8')

    def test_staging_changes_only_metadata(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.prepare_root(root)
            runtime = root / TOC.parent / 'Core.lua'
            runtime.write_text('-- runtime sentinel', encoding='utf-8')
            self.assertTrue(stage(root, self.next))
            self.assertFalse(stage(root, self.next))
            self.assertEqual(runtime.read_text(), '-- runtime sentinel')
            self.assertEqual(json.loads((root / 'compatibility.json').read_text())['addon_version'], '0.1.1')

    def test_invalid_observation_leaves_files_untouched(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.prepare_root(root)
            before = [(root / path).read_bytes() for path in (TOC, Path('compatibility.json'))]
            with self.assertRaises(ValueError):
                stage(root, dict(self.next, channel='beta'))
            self.assertEqual(before, [(root / path).read_bytes() for path in (TOC, Path('compatibility.json'))])

    def test_packaging_blocked_before_runtime_validation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.prepare_root(root)
            with self.assertRaisesRegex(ValueError, 'Runtime not validated'):
                package(root, root / 'dist')
            self.assertFalse((root / 'dist').exists())

    def test_packaging_rejects_empty_or_missing_runtime(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.state['runtime_ready'] = True
            self.prepare_root(root)
            with self.assertRaisesRegex(ValueError, 'No runtime'):
                package(root, root / 'dist')
            (root / TOC).write_text(self.toc + 'Missing.lua\n', encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'Invalid TOC file'):
                package(root, root / 'dist')

    def test_packaging_rejects_path_escape(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.state['runtime_ready'] = True
            self.prepare_root(root)
            (root / TOC).write_text(self.toc + '../../outside.lua\n', encoding='utf-8')
            (root / 'outside.lua').write_text('-- outside', encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'Invalid TOC file'):
                package(root, root / 'dist')

    def test_archive_has_installable_top_level_folder(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.state['runtime_ready'] = True
            self.prepare_root(root)
            (root / TOC).write_text(self.toc + 'Core.lua\n', encoding='utf-8')
            (root / TOC.parent / 'Core.lua').write_text('-- test fixture only', encoding='utf-8')
            with ZipFile(package(root, root / 'dist')) as archive:
                self.assertEqual(set(archive.namelist()),
                                 {'FriendlyNameplateGuild/FriendlyNameplateGuild.toc', 'FriendlyNameplateGuild/Core.lua'})

    def test_explicit_preview_is_separate_and_does_not_enable_releases(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.prepare_root(root)
            (root / TOC).write_text(self.toc + 'Core.lua\n', encoding='utf-8')
            (root / TOC.parent / 'Core.lua').write_text('-- preview fixture', encoding='utf-8')
            archive = package(root, root / 'dist', preview=True)
            self.assertEqual(archive.name, 'FriendlyNameplateGuild-0.1.0-preview.zip')
            self.assertFalse(json.loads((root / 'compatibility.json').read_text())['runtime_ready'])
            with self.assertRaisesRegex(ValueError, 'Runtime not validated'):
                package(root, root / 'dist')

    def test_repository_metadata_is_consistent(self):
        state = json.loads((ROOT / 'compatibility.json').read_text())
        self.assertIsNone(propose(state, state, (ROOT / TOC).read_text()))


class DetectionTests(unittest.TestCase):
    HEADER = 'Region!STRING:0|BuildId!DEC:4|VersionsName!String:0\n## seqn = 123\n'

    def setUp(self):
        self.state = dict(build=70862, game_version='1.60.1', interface=16001, region='us')

    def table(self, row='us|71000|1.60.1.71000'):
        return self.HEADER + row + '\n'

    def test_selects_configured_live_region_and_reuses_known_patch_interface(self):
        value = official_observation(self.table('eu|70900|1.60.1.70900\nus|71000|1.60.1.71000'), self.state)
        self.assertEqual((value['build'], value['interface'], value['game_version']), (71000, 16001, '1.60.1'))
        self.assertEqual(value['product'], 'wowf')

    def test_unknown_patch_does_not_guess_interface(self):
        value = official_observation(self.table('us|71000|1.60.2.71000'), self.state)
        self.assertNotIn('interface', value)
        self.assertIn('requires a verified', value['interface_error'])

    def test_rejects_wrong_versions_mismatches_duplicates_missing_regions_and_regression(self):
        for row in ('us|71000|12.1.5.71000', 'us|71000|1.60.1.99999',
                    'us|71000|bad', 'us|71000|1.60.1.71000\nus|71001|1.60.1.71001',
                    'eu|71000|1.60.1.71000', 'us|70000|1.60.1.70000',
                    'us|70862|1.60.2.70862', 'us|71000'):
            with self.subTest(row=row), self.assertRaises(ValueError):
                official_observation(self.table(row), self.state)

    def test_rejects_html_empty_and_ambiguous_schema(self):
        for body in ('', '<html>Unavailable</html>', 'Region|BuildId|VersionsName|Region\nus|71000|1.60.1.71000|us'):
            with self.subTest(body=body), self.assertRaises(ValueError):
                official_observation(body, self.state)

    def test_verified_feed_must_match_official_build(self):
        official = self.table('us|71000|1.60.2.71000')
        verified = dict(product='wowf', channel='live', build=71000, interface=16002)
        with patch('tools.compatibility.fetch_text', side_effect=[official, json.dumps(verified)]):
            self.assertEqual(detect(self.state, 'https://example.com/verified.json')['interface'], 16002)
        verified['build'] = 70999
        with patch('tools.compatibility.fetch_text', side_effect=[official, json.dumps(verified)]), self.assertRaises(ValueError):
            detect(self.state, 'https://example.com/verified.json')

    def test_staging_unverified_patch_preserves_repository_files(self):
        observation = official_observation(self.table('us|71000|1.60.2.71000'), self.state)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with self.assertRaisesRegex(ValueError, 'requires a verified'):
                stage(root, observation)
            self.assertEqual(list(root.iterdir()), [])


if __name__ == '__main__':
    unittest.main()
