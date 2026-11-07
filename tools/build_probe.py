"""Build the separate diagnostic addon; does not bypass production release gates."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parents[1]


def build(destination):
    source = ROOT / 'probes/BetterForeverNamesProbe'
    destination.mkdir(parents=True, exist_ok=True)
    archive = destination / 'BetterForeverNamesProbe-0.1.0.zip'
    with ZipFile(archive, 'w', ZIP_DEFLATED) as output:
        for name in ('BetterForeverNamesProbe.toc', 'Probe.lua'):
            output.write(source / name, f'BetterForeverNamesProbe/{name}')
    return archive


if __name__ == '__main__':
    print(build(ROOT / 'dist'))
