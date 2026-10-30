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
