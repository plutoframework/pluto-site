"""Assemble the unchanged static landing page and built Starlight documentation."""
from pathlib import Path
import shutil
import runpy
root = Path(__file__).resolve().parents[1]
out = root / '_site'
if out.exists():
    shutil.rmtree(out)
out.mkdir()
for name in ('index.html', 'styles.css', 'responsive.css', 'script.js', 'robots.txt', 'sitemap.xml'):
    shutil.copy2(root / name, out / name)
shutil.copytree(root / 'assets', out / 'assets')
shutil.copytree(root / 'docs/dist', out / 'docs')
runpy.run_path(str(root / 'scripts/export-markdown.py'))

# Publish discoverable canonical URLs for documentation as well as the homepage.
urls = ['https://plutoframework.github.io/pluto-site/']
urls += ['https://plutoframework.github.io/pluto-site/docs/' + str(p.parent.relative_to(out / 'docs')) .replace('\\', '/').removeprefix('.') + '/' for p in (out / 'docs').rglob('index.html')]
urls = sorted(set(u.replace('docs//', 'docs/') for u in urls))
(out / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + ''.join(f'  <url><loc>{url}</loc></url>\n' for url in urls) + '</urlset>\n')
