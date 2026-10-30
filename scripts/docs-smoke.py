"""Compile the getting-started workflow using the documented public CLI release."""
from pathlib import Path
import os
import subprocess
import tempfile

with tempfile.TemporaryDirectory(prefix='pluto-docs-') as temporary:
    root = Path(temporary).resolve()
    env = {**os.environ, 'GOWORK': 'off', 'GOBIN': str(root / 'bin')}
    def run(*args, cwd=root):
        subprocess.run(args, cwd=cwd, env=env, check=True)
    run('go', 'install', 'github.com/plutoframework/cli/cmd/pluto@v0.14.0')
    binary = str(root / 'bin/pluto')
    run(binary, '--no-input', 'init', 'mission-control', '--name', 'mission-control',
        '--module', 'example.com/mission-control', '--env-prefix', 'MISSION_CONTROL_',
        '--no-docker', '--no-mise', '--no-fnox')
    app = root / 'mission-control'
    run(binary, '--no-input', 'add', 'endpoint', 'launches', 'List', '--method', 'GET',
        '--path', '/api/launches', '--name', 'List launches', '--description',
        'List launches visible to the verified caller.', '--permission', 'launches:read', cwd=app)
    run(binary, '--no-input', 'add', 'state', 'launches', cwd=app)
    run('go', 'test', './internal/domain/...', cwd=app)
    run('go', 'build', './...', cwd=app)
    run('go', 'run', './cmd/openapi', '-check', cwd=app)
print('PASS: documented CLI workflow compiles with published modules')
