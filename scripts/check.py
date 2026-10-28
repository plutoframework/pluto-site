"""Check internal URLs, source sizes and local CSS assets without dependencies."""
from html.parser import HTMLParser
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.links = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            assert attrs["id"] not in self.ids, f"Duplicate ID: {attrs['id']}"
            self.ids.add(attrs["id"])
        for key in ("href", "src"):
            if key in attrs:
                self.links.append(attrs[key])
        if "aria-controls" in attrs:
            self.links.append("#" + attrs["aria-controls"])


page = Page()
page.feed((ROOT / "index.html").read_text())
for link in page.links:
    if link.startswith(("https://", "http://", "mailto:")):
        continue
    if link.startswith("#"):
        assert link[1:] in page.ids, f"Missing anchor: {link}"
    else:
        assert not link.startswith("/"), f"Root URL breaks Pages subpath: {link}"
        assert (ROOT / link).exists(), f"Missing file: {link}"
for link in re.findall(r"url\(['\"]?([^)'\"]+)", (ROOT / "styles.css").read_text()):
    assert (ROOT / link).is_file(), f"Missing CSS asset: {link}"
for path in ROOT.rglob("*"):
    if any(part in {"node_modules", ".git", "_site"} for part in path.relative_to(ROOT).parts):
        continue
    if path.suffix in (".html", ".css", ".js", ".py", ".yml"):
        assert len(path.read_text().splitlines()) < 1000, str(path)
assert (ROOT / "assets/social.png").is_file(), "Missing social image"
print(f"PASS: {len(page.links)} URLs/references, CSS assets, source size, social image")
