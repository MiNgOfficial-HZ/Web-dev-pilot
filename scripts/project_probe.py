"""Read-only project inventory. Never opens database or environment-file contents."""
import argparse
import json
import shutil
import subprocess
from pathlib import Path

SKIP = {'.git', 'node_modules', '.venv', 'venv', 'vendor', 'uploads', 'dist', '.next'}

def probe(root):
    root = Path(root).resolve()
    if not root.is_dir():
        raise ValueError('Project directory does not exist')
    files, pending = [], [root]
    while pending and len(files) < 5000:
        current = pending.pop()
        for entry in sorted(current.iterdir()):
            if entry.is_symlink():
                continue
            if entry.is_dir() and entry.name not in SKIP and not entry.name.startswith('.'):
                pending.append(entry)
            elif entry.is_file():
                files.append(entry.relative_to(root).as_posix())
    candidates = [p for p in files if Path(p).name in {'AGENTS.md', 'package.json', 'SKILL.md', 'wrangler.jsonc', 'wrangler.toml', 'README.md'} or (p.startswith('scripts/') and Path(p).suffix in {'.mjs', '.py'})]
    result = {
        'root': str(root),
        'project_state': 'empty' if not files else 'has_files',
        'file_count': len(files),
        'tools': {name: bool(shutil.which(name)) for name in ('git', 'node', 'npm', 'python')},
        'candidates': candidates,
        'inventory_limit_reached': len(files) >= 5000,
    }
    if shutil.which('git'):
        proc = subprocess.run(['git', '-C', str(root), 'status', '--short'], capture_output=True, text=True, timeout=20)
        result['git_status'] = proc.stdout.strip() if proc.returncode == 0 else 'Not an accessible Git worktree'
    return result

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('project')
    args = parser.parse_args()
    print(json.dumps(probe(args.project), ensure_ascii=False, indent=2))
