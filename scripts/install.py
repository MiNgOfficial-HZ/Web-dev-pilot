"""Install this bundle into an explicit skills directory; never overwrite."""
import argparse
import shutil
from pathlib import Path

def install(source, destination):
    source = Path(source).resolve()
    target = Path(destination).expanduser().resolve() / 'web-dev-pilot'
    if target.exists():
        raise ValueError('web-dev-pilot already exists; choose another destination or review it manually')
    if source == target or source in target.parents:
        raise ValueError('Destination must be outside the source bundle')
    shutil.copytree(source, target, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    return target

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--skills-dir', required=True, help='Actual skills directory supported by your AI client')
    args = parser.parse_args()
    try:
        target = install(Path(__file__).resolve().parents[1], args.skills_dir)
    except ValueError as error:
        parser.error(str(error))
    print('Installed: ' + str(target))
    print('Refresh skills or reopen your AI client, then invoke $web-dev-pilot.')
