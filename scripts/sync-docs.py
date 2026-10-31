"""Refresh reference pages from explicit, committed sibling repository revisions.

Fetch sibling origin/main branches before refreshing published references; CI builds the checked-in snapshots.
No working-tree content or secret files are read.
"""
from pathlib import Path
import hashlib
import json
import re
import subprocess
from doc_markdown import map_prose

ROOT = Path(__file__).resolve().parents[1]
SOURCES = [
    ('cli/reference', 'CLI reference', 'pluto-cli', 'docs/REFERENCE.md'),
    ('frontend/state', 'Typed UI state', 'pluto-frontend', 'docs/REFERENCE.md'),
    ('frontend/profiles', 'React and UI libraries', 'pluto-cli', 'docs/FRONTEND.md'),
    ('frontend/themes', 'TOML themes', 'pluto-cli', 'docs/THEMES.md'),
    ('frontend/registries', 'Custom component registries', 'pluto-cli', 'docs/COMPONENT-REGISTRIES.md'),
    ('backend/features', 'Feature flags', 'pluto-core', 'features/README.md'),
    ('backend/core', 'Core: pagination, idempotency and cache', 'pluto-core', 'docs/REFERENCE.md'),
    ('backend/state', 'State machines', 'pluto-core', 'state/README.md'),
    ('backend/telemetry', 'OpenTelemetry', 'pluto-core', 'telemetry/README.md'),
    ('backend/auth', 'Authentication', 'pluto-auth', 'docs/REFERENCE.md'),
    ('backend/authentication', 'Account authentication', 'pluto-auth', 'docs/AUTHENTICATION.md'),
    ('backend/oidc', 'OIDC and Google sign-in', 'pluto-auth', 'docs/OIDC.md'),
    ('backend/auth-roadmap', 'Authentication roadmap', 'pluto-auth', 'docs/ROADMAP.md'),
    ('backend/credentials', 'Local credential lifecycle', 'pluto-auth', 'docs/LOCAL-CREDENTIALS.md'),
    ('backend/rbac', 'Roles and permissions', 'pluto-rbac', 'docs/REFERENCE.md'),
    ('backend/jobs', 'Jobs and transactional outbox', 'pluto-jobs', 'docs/REFERENCE.md'),
    ('backend/agents', 'Typed AI agents', 'pluto-agent', 'docs/REFERENCE.md'),
    ('example', 'Purchasing application walkthrough', 'pluto-example', 'docs/REFERENCE.md'),
]

def git(repo, *args):
    return subprocess.check_output(['git', '-C', str(repo), *args], text=True).strip()

manifest = []
for slug, title, directory, filename in SOURCES:
    repo = ROOT.parent / directory
    sha = git(repo, 'rev-parse', 'refs/remotes/origin/main')
    remote = git(repo, 'remote', 'get-url', 'origin').removesuffix('.git')
    source = subprocess.check_output(['git', '-C', str(repo), 'show', f'{sha}:{filename}'], text=True)
    for match in re.finditer(
        r'<!-- example-source: ([^\n]+) -->\s*```go\n(.*?)\n```\s*<!-- /example-source -->',
        source, re.S,
    ):
        expected = subprocess.check_output(
            ['git', '-C', str(repo), 'show', f'{sha}:{match[1]}'], text=True)
        if match[2].strip() != expected.strip():
            raise ValueError(f'Example drift in {filename}: {match[1]}')
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
    source = map_prose(source, lambda prose: re.sub(r'(\]\()([^\s)]+)(\))', link, prose))
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
