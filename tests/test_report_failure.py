import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from tools.report_failure import report


class FailureReportingTests(unittest.TestCase):
    def test_existing_open_build_issue_is_not_duplicated(self):
        title = 'Forever build 71000: automated compatibility check failed'
        with patch('tools.report_failure.subprocess.run') as run:
            run.return_value = subprocess.CompletedProcess([], 0, json.dumps([dict(title=title, url='https://github.com/example/issues/1')]))
            report(71000)
            self.assertEqual(run.call_count, 1)

    def test_failure_issue_contains_run_link_observation_and_real_test_output(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            observation, log = root / 'observation.json', root / 'tests.txt'
            observation.write_text('{"build":71000}', encoding='utf-8')
            failing_test = root / 'test_failure.py'
            failing_test.write_text('import unittest\nclass Failure(unittest.TestCase):\n    def test_guild_change(self):\n        self.fail("stale guild label")\n', encoding='utf-8')
            failed = subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s', str(root)], capture_output=True, text=True)
            self.assertNotEqual(failed.returncode, 0)
            log.write_text(failed.stdout + failed.stderr, encoding='utf-8')
            bodies = []

            def gh(args, **kwargs):
                if args[2] == 'list':
                    return subprocess.CompletedProcess(args, 0, '[]')
                bodies.append(Path(args[args.index('--body-file') + 1]).read_text(encoding='utf-8'))
                return subprocess.CompletedProcess(args, 0)

            with patch.dict(os.environ, GITHUB_REPOSITORY='oliome/FriendlyNameplateGuild', GITHUB_RUN_ID='123'), patch('tools.report_failure.subprocess.run', side_effect=gh):
                report(71000, observation, log)
            self.assertIn('/actions/runs/123', bodies[0])
            self.assertIn('AssertionError: stale guild label', bodies[0])
            self.assertIn('71000', bodies[0])

    def test_issue_search_failure_is_not_misreported_as_success(self):
        with patch('tools.report_failure.subprocess.run', side_effect=subprocess.CalledProcessError(1, ['gh'])):
            with self.assertRaises(subprocess.CalledProcessError):
                report('unknown')
