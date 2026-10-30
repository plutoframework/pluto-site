"""Export canonical documentation as small, individually fetchable Markdown files."""
from pathlib import Path
from urllib.parse import urlsplit
import json
import posixpath
import re

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'docs/src/content/docs'
OUTPUT = ROOT / '_site/docs'
BASE = 'https://plutoframework.github.io/pluto-site/docs/'
pages = {p.relative_to(SOURCE).with_suffix('').as_posix(): p
         for p in SOURCE.rglob('*.md')}
index = ['# Pluto documentation', '',
         '> Fetch only the Markdown topic needed for the task.', '',
         'Reference pages record their upstream revision. Match examples to installed versions.', '',
         '## Topics', '']
for slug, path in sorted(pages.items()):
    _, metadata, body = path.read_text().split('---', 2)
    title = re.search(r'^title: (.+)$', metadata, re.M)[1]
    title = json.loads(title) if title.startswith('"') else title.strip("'")

    # Leave code examples intact; resolve authored links outside fenced blocks.
    def rewrite(match):
        target = match[2]
        url = urlsplit(target)
        if url.scheme or url.netloc or target.startswith('#'):
            return match[0]
        if target.startswith('/pluto-site/docs/'):
            resolved = target.removeprefix('/pluto-site/docs/')
        elif target.startswith('/'):
            return match[1] + 'https://plutoframework.github.io' + target + match[3]
        else:
            resolved = posixpath.normpath(posixpath.join('' if slug == 'index' else slug, url.path))
        resolved = resolved.rstrip('/').removesuffix('.md')
        if resolved in ('.', ''):
            resolved = 'index'
        elif resolved not in pages and resolved + '/index' in pages:
            resolved += '/index'
        if resolved in pages:
            suffix = ('?' + url.query if url.query else '') + ('#' + url.fragment if url.fragment else '')
            return match[1] + BASE + resolved + '.md' + suffix + match[3]
        raise ValueError(f'Unresolved Markdown link in {slug}: {target}')

    parts = re.split(r'(^```[^\n]*\n.*?^```[^\n]*$)', body, flags=re.M | re.S)
    for i in range(0, len(parts), 2):
        parts[i] = re.sub(r'(\]\()([^\s)]+)(\))', rewrite, parts[i])
    output = OUTPUT / (slug + '.md')
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(f'# {title}\n\n' + ''.join(parts).strip() + '\n')
    index.append(f'- [{title}]({BASE}{slug}.md)')
(OUTPUT / 'llms.txt').write_text('\n'.join(index) + '\n')
(ROOT / '_site/llms.txt').write_text(
    '# Pluto\n\n- [Documentation index](' + BASE + 'llms.txt)\n'
    '- [Installable agent skills](https://github.com/plutoframework/pluto-skills)\n')
print(f'Exported {len(pages)} Markdown topics and two agent indexes.')
