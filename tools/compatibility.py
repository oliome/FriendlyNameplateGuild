"""Fail-closed metadata update and deterministic release packaging."""

import argparse
import json
import re
from pathlib import Path
from urllib.request import urlopen
from zipfile import ZipFile, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parents[1]
TOC = Path('addon/BetterForeverNames/BetterForeverNames.toc')
BUILD_URL = 'https://raw.githubusercontent.com/Gethe/wow-ui-source/forever/version.txt'


def newer_build(version, current_build):
    """A UI mirror can reveal a build change, but cannot supply an Interface."""
    match = re.fullmatch(r'1\.60\.\d+\.(\d+)', version.strip())
    if not match:
        raise ValueError('Unrecognized Forever build; check the source manually')
    return version.strip() if int(match[1]) > current_build else ''


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
    if observation['interface'] == state['interface']:
        return None  # A new build alone does not make the TOC out of date.
    if observation['build'] <= state['build']:
        raise ValueError('New Interface must come from a newer build')
    major, minor, patch = map(int, version.split('.'))
    new = dict(state, interface=observation['interface'], build=observation['build'],
               addon_version=f'{major}.{minor}.{patch + 1}')
    updated = re.sub(r'^## Interface: .+$', f"## Interface: {new['interface']}", toc, flags=re.MULTILINE)
    updated = re.sub(r'^## Version: .+$', f"## Version: {new['addon_version']}", updated, flags=re.MULTILINE)
    return new, updated


def stage(root, observation):
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
    folder = root / 'addon/BetterForeverNames'
    listed = [line.strip() for line in toc.splitlines() if line.strip() and not line.startswith('#')]
    if not listed or not any(line.endswith('.lua') for line in listed):
        raise ValueError('No runtime Lua files in TOC')
    for name in listed:
        path = (folder / name.replace('\\', '/')).resolve()
        if not path.is_relative_to(folder.resolve()) or not path.is_file():
            raise ValueError(f'Invalid TOC file: {name}')
    destination.mkdir(parents=True, exist_ok=True)
    suffix = '-preview' if preview else ''
    archive = destination / f"BetterForeverNames-{state['addon_version']}{suffix}.zip"
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
    parser.add_argument('--watch', action='store_true', help='Print a newer Forever mirror build, without inferring Interface or changing files')
    args = parser.parse_args()
    if args.watch:
        if args.package or args.preview or args.feed or args.observation:
            parser.error('--watch cannot be combined with update/package options')
        state = json.loads((ROOT / 'compatibility.json').read_text(encoding='utf-8'))
        with urlopen(BUILD_URL, timeout=30) as response:
            version = response.read(128).decode('ascii')
        print(newer_build(version, state['build']))
        return
    if args.package:
        print(package(ROOT, ROOT / 'dist', preview=args.preview))
        return
    if args.preview:
        parser.error('--preview requires --package')
    if bool(args.feed) == bool(args.observation):
        parser.error('Specify exactly one of --feed or --observation')
    if args.feed:
        if not args.feed.startswith('https://'):
            raise ValueError('Feed must use HTTPS')
        with urlopen(args.feed, timeout=30) as response:
            if not response.geturl().startswith('https://'):
                raise ValueError('Feed redirected away from HTTPS')
            raw = response.read(65537)
            if len(raw) > 65536:
                raise ValueError('Feed response too large')
            observation = json.loads(raw)
    else:
        observation = json.loads(args.observation.read_text(encoding='utf-8'))
    print('Staged compatibility patch' if stage(ROOT, observation) else 'No Interface change')


if __name__ == '__main__':
    main()
