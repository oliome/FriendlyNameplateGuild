"""Fail-closed metadata update and deterministic release packaging."""

import argparse
import json
import re
from pathlib import Path
from urllib.request import urlopen
from zipfile import ZipFile, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parents[1]
TOC = Path('addon/FriendlyNameplateGuild/FriendlyNameplateGuild.toc')
BUILD_URL = 'https://us.version.battle.net/v2/products/wowf/versions'


def official_observation(text, state):
    """Read the live wowf region row; never infer Interface from a patch number."""
    lines = [line.strip() for line in text.splitlines() if line.strip() and not line.startswith('#')]
    if not lines:
        raise ValueError('Empty Blizzard version response')
    headers = [column.split('!', 1)[0] for column in lines[0].split('|')]
    if len(headers) != len(set(headers)) or not {'Region', 'BuildId', 'VersionsName'} <= set(headers):
        raise ValueError('Unrecognized Blizzard version schema')
    rows = []
    for line in lines[1:]:
        values = line.split('|')
        if len(values) != len(headers):
            raise ValueError('Malformed Blizzard version row')
        row = dict(zip(headers, values))
        if row['Region'] == state.get('region', 'us'):
            rows.append(row)
    if len(rows) != 1:
        raise ValueError('Expected exactly one configured region in Blizzard version response')
    row = rows[0]
    match = re.fullmatch(r'(1\.\d{1,2}\.\d{1,2})\.([1-9]\d{0,9})', row['VersionsName'])
    if not match or not re.fullmatch(r'[1-9]\d{0,9}', row['BuildId']) or int(match[2]) != int(row['BuildId']):
        raise ValueError('Blizzard build and version disagree or are not a recognized Forever version')
    observed = dict(product='wowf', channel='live', region=row['Region'],
                    game_version=match[1], build=int(row['BuildId']), source=BUILD_URL)
    if observed['build'] < state['build']:
        raise ValueError('Blizzard feed regressed; refusing to downgrade')
    if observed['build'] == state['build'] and state.get('game_version') and observed['game_version'] != state['game_version']:
        raise ValueError('Existing build has conflicting game-patch metadata')
    if observed['game_version'] == state.get('game_version'):
        observed['interface'] = state['interface']
        observed['interface_source'] = 'Previously verified Interface for this unchanged game patch'
    else:
        observed['interface_error'] = ('New game patch ' + match[1] +
            ' requires a verified live Interface value; no Interface was inferred.')
    return observed


def fetch_text(url, limit=65536):
    if not url.startswith('https://'):
        raise ValueError('Source must use HTTPS')
    with urlopen(url, timeout=30) as response:
        if not response.geturl().startswith('https://'):
            raise ValueError('Source redirected away from HTTPS')
        raw = response.read(limit + 1)
    if len(raw) > limit:
        raise ValueError('Source response too large')
    return raw.decode('utf-8')


def detect(state, feed=None):
    observation = official_observation(fetch_text(BUILD_URL), state)
    if 'interface' not in observation and feed:
        verified = json.loads(fetch_text(feed))
        validate_observation(verified)
        if verified['build'] != observation['build']:
            raise ValueError('Interface feed does not match the official live build')
        observation.update(interface=verified['interface'], interface_source=feed)
        observation.pop('interface_error', None)
    return observation


def validate_observation(value):
    if not isinstance(value, dict):
        raise ValueError('Build observation must be an object')
    if value.get('product') != 'wowf' or value.get('channel') != 'live':
        raise ValueError('Only live wowf observations are accepted')
    for key in ('interface', 'build'):
        if type(value.get(key)) is not int or value[key] <= 0:
            raise ValueError(f'{key} must be a positive integer')
    if not 16000 <= value['interface'] < 17000:
        raise ValueError('New client family requires manual review')
    return value


def metadata(text, key):
    matches = re.findall(rf'^## {re.escape(key)}: (.+)$', text, re.MULTILINE)
    if len(matches) != 1:
        raise ValueError(f'Expected exactly one {key} field')
    return matches[0]


def propose(state, observation, toc):
    validate_observation(state)
    validate_observation(observation)
    version = state['addon_version']
    if not re.fullmatch(r'(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)', version):
        raise ValueError('Expected a stable semantic addon version')
    if metadata(toc, 'Interface') != str(state['interface']) or metadata(toc, 'Version') != version:
        raise ValueError('TOC and compatibility state disagree')
    if observation['build'] < state['build'] or observation['interface'] < state['interface']:
        raise ValueError('Regressing build/interface observation')
    if observation['build'] == state['build'] and observation['interface'] == state['interface']:
        return None
    if observation['build'] <= state['build']:
        raise ValueError('New Interface must come from a newer build')
    major, minor, patch = map(int, version.split('.'))
    new = dict(state, interface=observation['interface'], build=observation['build'],
               addon_version=f'{major}.{minor}.{patch + 1}')
    if 'game_version' in observation:
        new['game_version'] = observation['game_version']
    updated = re.sub(r'^## Interface: .+$', f"## Interface: {new['interface']}", toc, flags=re.MULTILINE)
    updated = re.sub(r'^## Version: .+$', f"## Version: {new['addon_version']}", updated, flags=re.MULTILINE)
    return new, updated


def stage(root, observation):
    if observation.get('interface_error'):
        raise ValueError(observation['interface_error'])
    state_path = root / 'compatibility.json'
    state = json.loads(state_path.read_text(encoding='utf-8'))
    proposal = propose(state, observation, (root / TOC).read_text(encoding='utf-8'))
    if proposal is None:
        return False
    state, toc = proposal
    (root / TOC).write_text(toc, encoding='utf-8')
    state_path.write_text(json.dumps(state, indent=2) + '\n', encoding='utf-8')
    return True


def package(root, destination, preview=False):
    state = json.loads((root / 'compatibility.json').read_text(encoding='utf-8'))
    validate_observation(state)
    if state.get('runtime_ready') is not True and not preview:
        raise ValueError('Runtime not validated; packaging is disabled')
    toc = (root / TOC).read_text(encoding='utf-8')
    propose(state, state, toc)  # Also verify version/TOC consistency.
    folder = root / 'addon/FriendlyNameplateGuild'
    listed = [line.strip() for line in toc.splitlines() if line.strip() and not line.startswith('#')]
    if not listed or not any(line.endswith('.lua') for line in listed):
        raise ValueError('No runtime Lua files in TOC')
    for name in listed:
        path = (folder / name.replace('\\', '/')).resolve()
        if not path.is_relative_to(folder.resolve()) or not path.is_file():
            raise ValueError(f'Invalid TOC file: {name}')
    destination.mkdir(parents=True, exist_ok=True)
    suffix = '-preview' if preview else ''
    archive = destination / f"FriendlyNameplateGuild-{state['addon_version']}{suffix}.zip"
    with ZipFile(archive, 'w', ZIP_DEFLATED) as output:
        for path in sorted(folder.rglob('*')):
            if path.is_file():
                output.write(path, path.relative_to(root / 'addon').as_posix())
    return archive


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--feed', help='Trusted HTTPS live build-observation JSON URL')
    parser.add_argument('--observation', type=Path, help='Local JSON observation for offline checks')
    parser.add_argument('--package', action='store_true')
    parser.add_argument('--preview', action='store_true', help='Explicitly package an unvalidated desktop test build')
    parser.add_argument('--watch', action='store_true', help='Print a newer official live build without changing files')
    parser.add_argument('--detect', action='store_true', help='Write the official live observation and GitHub Actions outputs')
    parser.add_argument('--output', type=Path, default=Path('candidate.json'))
    args = parser.parse_args()
    if args.watch or args.detect:
        if args.package or args.preview or args.observation or (args.watch and args.detect):
            parser.error('Detection cannot be combined with staging/package options')
        state = json.loads((ROOT / 'compatibility.json').read_text(encoding='utf-8'))
        observation = detect(state, args.feed)
        changed = observation['build'] > state['build']
        if args.watch:
            print(f"{observation['game_version']}.{observation['build']}" if changed else '')
            return
        args.output.write_text(json.dumps(observation, indent=2) + '\n', encoding='utf-8')
        import os
        if os.environ.get('GITHUB_OUTPUT'):
            with open(os.environ['GITHUB_OUTPUT'], 'a', encoding='utf-8') as output:
                print(f'changed={str(changed).lower()}', file=output)
                print(f"build={observation['build']}", file=output)
        print(json.dumps(observation, indent=2))
        return
    if args.package:
        print(package(ROOT, ROOT / 'dist', preview=args.preview))
        return
    if args.preview:
        parser.error('--preview requires --package')
    if bool(args.feed) == bool(args.observation):
        parser.error('Specify exactly one of --feed or --observation')
    if args.feed:
        observation = json.loads(fetch_text(args.feed))
    else:
        observation = json.loads(args.observation.read_text(encoding='utf-8'))
    print('Staged compatibility patch' if stage(ROOT, observation) else 'No live build change')


if __name__ == '__main__':
    main()
