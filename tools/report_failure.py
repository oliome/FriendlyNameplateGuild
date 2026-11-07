"""Open one issue for a failed live-build check; credentials stay with gh."""
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile


def report(build, observation=Path('candidate.json'), log=Path('test-results.txt')):
    build = str(build) if re.fullmatch(r'[1-9]\d*', str(build)) else 'unknown'
    title = f'Forever build {build}: automated compatibility check failed'
    result = subprocess.run(['gh', 'issue', 'list', '--state', 'open', '--limit', '100',
                             '--search', title + ' in:title', '--json', 'title,url'],
                            check=True, capture_output=True, text=True)
    for issue in json.loads(result.stdout):
        if issue['title'] == title:
            print('Failure already tracked:', issue['url'])
            return
    run = (os.environ.get('GITHUB_SERVER_URL', 'https://github.com') + '/' +
           os.environ['GITHUB_REPOSITORY'] + '/actions/runs/' + os.environ['GITHUB_RUN_ID'])
    details = observation.read_text(encoding='utf-8') if observation.exists() else 'Live observation unavailable.'
    output = log.read_text(encoding='utf-8', errors='replace')[-12000:] if log.exists() else 'Tests were not reached; inspect the workflow logs.'
    # Indentation keeps test output from terminating a Markdown code fence.
    body = ('The live-build workflow failed. Failed tests block version commits and publication. '
            'A later publishing failure can occur after a tested commit/tag was pushed; inspect the linked run before retrying.\n\n'
            f'Workflow: {run}\n\nObservation:\n\n' +
            '\n'.join('    ' + line for line in details.splitlines()) +
            '\n\nTest output (last 12,000 characters):\n\n' +
            '\n'.join('    ' + line for line in output.splitlines()) +
            '\n\nFix the reported error and rerun Forever compatibility. If a new patch lacks an Interface, verify it from the live client rather than inferring it from the build number.\n')
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / 'issue.md'
        path.write_text(body, encoding='utf-8')
        subprocess.run(['gh', 'issue', 'create', '--title', title, '--body-file', str(path)], check=True)


if __name__ == '__main__':
    report(os.environ.get('FNG_BUILD', 'unknown'))
