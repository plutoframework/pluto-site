"""Verify assembled local links, fragments, assets and search at the Pages base."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote

ROOT = Path(__file__).resolve().parents[1] / '_site'
BASE = '/pluto-site/'

class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.ids = set()

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            self.ids.add(attrs['id'])
        for key, value in attrs.items():
            if key in ('href', 'src') and value:
                self.links.append(value)

pages = {}
for page in ROOT.rglob('*.html'):
    parsed = Links()
    parsed.feed(page.read_text())
    pages[page.resolve()] = parsed

count = 0
for page, parsed in pages.items():
    for link in parsed.links:
        url = urlsplit(link)
        if url.scheme or url.netloc:
            continue
        path = unquote(url.path)
        if not path:
            target = page
        elif path.startswith('/'):
            assert path.startswith(BASE), f'Incorrect Pages base: {page}: {link}'
            target = ROOT / path[len(BASE):]
        else:
            target = page.parent / path
        if target.is_dir():
            target /= 'index.html'
        assert target.is_file(), f'Missing target: {page}: {link}'
        if url.fragment and target.suffix == '.html':
            assert unquote(url.fragment) in pages[target.resolve()].ids, f'Missing fragment: {page}: {link}'
        count += 1
assert (ROOT / 'docs/pagefind/pagefind.js').is_file(), 'Search index missing'
print(f'PASS: {count} local links/assets/fragments and search index')

# Check that every exported topic and index link resolves without an HTML fallback.
import re
source = Path(__file__).resolve().parents[1] / 'docs/src/content/docs'
exports = []
for page in source.rglob('*.md'):
    target = ROOT / 'docs' / page.relative_to(source)
    assert target.is_file(), f'Missing Markdown export: {target}'
    content = target.read_text()
    assert content.startswith('# ') and not content.startswith('---'), target
    exports.append(target)
for page in exports + [ROOT / 'llms.txt', ROOT / 'docs/llms.txt']:
    for link in re.findall(r'\]\((https://[^)]+)\)', page.read_text()):
        url = urlsplit(link)
        if url.netloc != 'plutoframework.github.io' or not url.path.startswith(BASE):
            continue
        target = ROOT / unquote(url.path[len(BASE):])
        if target.is_dir():
            target /= 'index.html'
        assert target.is_file(), f'Missing export target: {page}: {link}'
print(f'PASS: {len(exports)} Markdown topics and agent indexes')
