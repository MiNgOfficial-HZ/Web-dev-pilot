"""Validate local resource links and create a distributable ZIP outside this skill."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import zipfile

def package(source, output):
    source, output = Path(source).resolve(), Path(output).resolve()
    if source in output.parents or source == output:
        raise ValueError('ZIP must be outside the skill folder')
    if output.exists():
        raise ValueError('ZIP already exists; choose a new version filename')
    for markdown in source.rglob('*.md'):
        for target in re.findall(r'\]\(([^)]+)\)', markdown.read_text(encoding='utf-8')):
            if '://' not in target and not target.startswith('#'):
                if not (markdown.parent / target.split('#')[0]).exists():
                    raise ValueError('Missing resource link in ' + markdown.name + ': ' + target)
    files = sorted(p for p in source.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc')
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
        for file in files:
            archive.write(file, source.name + '/' + file.relative_to(source).as_posix())
    with zipfile.ZipFile(output) as archive:
        if archive.testzip():
            raise ValueError('ZIP integrity check failed')
    return {'zip': str(output), 'files': len(files), 'bytes': output.stat().st_size, 'sha256': hashlib.sha256(output.read_bytes()).hexdigest()}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output')
    args = parser.parse_args()
    print(json.dumps(package(Path(__file__).resolve().parents[1], args.output), ensure_ascii=False, indent=2))
