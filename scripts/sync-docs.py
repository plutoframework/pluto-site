"""Refresh reference pages from explicit, committed sibling repository revisions.

Run locally to review upstream changes; CI builds the checked-in snapshots.
No working-tree content or secret files are read.
"""
from pathlib import Path
import hashlib
import json
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
SOURCES = [
    ('cli/reference', 'CLI reference', 'pluto-cli', 'README.md'),
    ('frontend/state', 'Typed UI state', 'pluto-frontend', 'README.md'),
    ('frontend/profiles', 'React and UI libraries', 'pluto-cli', 'docs/FRONTEND.md'),
    ('frontend/themes', 'TOML themes', 'pluto-cli', 'docs/THEMES.md'),
    ('frontend/registries', 'Custom component registries', 'pluto-cli', 'docs/COMPONENT-REGISTRIES.md'),
    ('backend/features', 'Feature flags', 'pluto-cli', 'docs/FEATURE-FLAGS.md'),
    ('backend/core', 'Core: pagination, idempotency and cache', 'pluto-core', 'README.md'),
    ('backend/state', 'State machines', 'pluto-core', 'state/README.md'),
    ('backend/telemetry', 'OpenTelemetry', 'pluto-core', 'telemetry/README.md'),
    ('backend/auth', 'Authentication', 'pluto-auth', 'README.md'),
    ('backend/credentials', 'Local credential lifecycle', 'pluto-auth', 'docs/LOCAL-CREDENTIALS.md'),
    ('backend/rbac', 'Roles and permissions', 'pluto-rbac', 'README.md'),
    ('backend/jobs', 'Jobs and transactional outbox', 'pluto-jobs', 'README.md'),
    ('backend/agents', 'Typed AI agents', 'pluto-agent', 'README.md'),
    ('example', 'Purchasing application walkthrough', 'pluto-example', 'README.md'),
]

def git(repo, *args):
    return subprocess.check_output(['git', '-C', str(repo), *args], text=True).strip()

manifest = []
for slug, title, directory, filename in SOURCES:
    repo = ROOT.parent / directory
    sha = git(repo, 'rev-parse', 'HEAD')
    remote = git(repo, 'remote', 'get-url', 'origin').removesuffix('.git')
    source = subprocess.check_output(['git', '-C', str(repo), 'show', f'{sha}:{filename}'], text=True)
    version = git(repo, 'describe', '--tags', '--always', sha)
    url = f'{remote}/blob/{sha}/{filename}'
    # Relative source links resolve against their original repository, not /docs/.
    def link(match):
        target = match[2]
        if target.startswith(('https:', 'http:', '#', 'mailto:', '//')):
            return match[0]
        if target.startswith('/Users/'):
            return match[1] + remote + '/tree/' + sha + match[3]
        from posixpath import normpath, dirname, join
        path = normpath(join(dirname(filename), target))
        return match[1] + f'{remote}/blob/{sha}/{path}' + match[3]
    source = re.sub(r'(\]\()([^\s)]+)(\))', link, source)
    source = re.sub(r'^# .+\n', '', source, count=1)
    content = (f'---\ntitle: {json.dumps(title)}\ndescription: {json.dumps(title + " for the Pluto framework.")}\n---\n\n'
               f'> Reference snapshot: **{version}** · [Source at `{sha[:7]}`]({url}). '
               'Commands and integration limits below belong to this revision.\n\n' + source)
    dest = ROOT / 'docs/src/content/docs' / (slug + '.md')
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(content)
    manifest.append(dict(page=slug, repository=remote, revision=sha, source=filename,
                         version=version, sha256=hashlib.sha256(source.encode()).hexdigest()))
(ROOT / 'docs/sources.json').write_text(json.dumps(manifest, indent=2) + '\n')
print(f'Synchronized {len(manifest)} committed reference pages.')
