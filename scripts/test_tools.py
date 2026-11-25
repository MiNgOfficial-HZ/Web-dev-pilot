"""Offline checks in temporary directories; never changes a real project."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import unittest
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from install import install
from project_probe import probe
from http_check import check, validate_url

class ToolsTest(unittest.TestCase):
    def test_probe_excludes_dependencies_and_secrets(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            empty = root / 'empty'
            empty.mkdir()
            empty_data = probe(empty)
            self.assertEqual(empty_data['project_state'], 'empty')
            self.assertEqual(empty_data['file_count'], 0)
            (root / 'node_modules').mkdir()
            (root / 'node_modules/package.json').write_text('{}')
            (root / 'package.json').write_text('{}')
            (root / '.env').write_text('SECRET=do-not-copy')
            data = probe(root)
            self.assertEqual(data['candidates'], ['package.json'])
            self.assertNotIn('do-not-copy', json.dumps(data))

    def test_checkpoint_roundtrip_and_refuse_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            script = Path(__file__).with_name('task_state.py')
            def run(*args):
                return subprocess.run([sys.executable, str(script), *args], capture_output=True, text=True)
            self.assertEqual(run('init', directory, '--goal', 'demo').returncode, 0)
            self.assertNotEqual(run('init', directory, '--goal', 'overwrite').returncode, 0)
            self.assertEqual(run('update', directory, '--phase', 'verified', '--note', 'local check').returncode, 0)
            data = json.loads(run('status', directory).stdout)
            self.assertEqual(data['goal'], 'demo')
            self.assertEqual(data['phase'], 'verified')

    def test_installer_refuses_existing_target(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / 'source'
            source.mkdir()
            (source / 'SKILL.md').write_text('demo')
            target = install(source, root / 'skills')
            self.assertTrue((target / 'SKILL.md').exists())
            with self.assertRaises(ValueError):
                install(source, root / 'skills')

    def test_http_success_mismatch_and_not_found(self):
        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                self.send_response(404 if self.path == '/missing' else 200)
                self.end_headers()
                self.wfile.write(b'<h1>Sample site</h1>')
            def log_message(self, *args):
                pass
        server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            url = 'http://127.0.0.1:' + str(server.server_port)
            opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
            self.assertTrue(check(url + '/?token=hidden', 'Sample site', opener=opener)['ok'])
            self.assertNotIn('token', json.dumps(check(url + '/?token=hidden', opener=opener)))
            self.assertFalse(check(url, 'Absent', opener=opener)['ok'])
            self.assertEqual(check(url + '/missing', opener=opener)['status'], 404)
        finally:
            server.shutdown()
            server.server_close()
        with self.assertRaises(ValueError):
            validate_url('https://user:password@example.com')

if __name__ == '__main__':
    unittest.main()
