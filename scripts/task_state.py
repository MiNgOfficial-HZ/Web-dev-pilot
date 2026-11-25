"""Save resumable task checkpoints without overwriting an existing task."""
import argparse
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path

PHASES = ['discovered', 'implemented', 'verified', 'previewed', 'pr-opened', 'released', 'live-verified', 'blocked']

def save(file, data):
    file.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(dir=file.parent, suffix='.tmp')
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as out:
            json.dump(data, out, ensure_ascii=False, indent=2)
        os.replace(temporary, file)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['init', 'update', 'status'])
    parser.add_argument('task_dir')
    parser.add_argument('--goal')
    parser.add_argument('--phase', choices=PHASES)
    parser.add_argument('--note', default='')
    parser.add_argument('--evidence', action='append', default=[])
    args = parser.parse_args()
    file = Path(args.task_dir).resolve() / 'state.json'
    if args.action == 'init':
        if file.exists():
            parser.error('Task already exists; use status or update')
        if not args.goal:
            parser.error('--goal is required for init')
        data = {'schema': 1, 'goal': args.goal, 'phase': 'discovered', 'events': []}
    else:
        data = json.loads(file.read_text(encoding='utf-8'))
    if args.action == 'update':
        if not args.phase:
            parser.error('--phase is required for update')
        data['phase'] = args.phase
    if args.action != 'status':
        data['events'].append({'time_utc': datetime.now(timezone.utc).isoformat(), 'phase': data['phase'], 'note': args.note, 'evidence': args.evidence})
        save(file, data)
    print(json.dumps(data, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
