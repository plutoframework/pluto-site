"""Format/check Go fences, including excerpts, with pinned Pluto formatters.

Complete source examples also pass their owning repository's gci and wsl checks.
"""
from pathlib import Path
import argparse
import re
import subprocess
import textwrap

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--write', action='store_true')
parser.add_argument('paths', nargs='*', type=Path)
args = parser.parse_args()
version = subprocess.check_output(['golangci-lint', 'version', '--short'], text=True).strip()
if version != '2.15.0':
    raise SystemExit('Go documentation formatting requires golangci-lint 2.15.0')
paths = args.paths or sorted((ROOT / 'docs/src/content/docs').rglob('*.md'))
fence = re.compile(r'(^```go[^\n]*\n)(.*?)(^```[^\n]*$)', re.M | re.S)


def formatted(code):
    variants = [('', code, '')] if re.search(r'^package ', code, re.M) else []
    variants += [('package documentation\n\n', code, '')]
    variants += [('package documentation\n\nfunc excerpt() {\n', code, '\n}\n')]
    for prefix, original, suffix in variants:
        source = prefix + original + suffix
        parse = subprocess.run(['gofmt'], input=source, capture_output=True, text=True)
        if parse.returncode:
            continue
        result = subprocess.run(
            ['golangci-lint', 'fmt', '--stdin', '--config', str(ROOT / '.golangci.docs.yml')],
            input=source, capture_output=True, text=True, check=True)
        value = result.stdout
        if prefix.endswith('func excerpt() {\n'):
            value = value.split('func excerpt() {\n', 1)[1].rsplit('\n}', 1)[0]
            value = textwrap.dedent(value)
        elif prefix:
            value = value.split('package documentation\n', 1)[1]
        return value.strip('\n') + '\n'
    raise ValueError('Go excerpt cannot be parsed; use complete source or label pseudocode explicitly')


changes = []
count = 0
for path in paths:
    def replace(match):
        global count
        count += 1
        try:
            result = formatted(match[2])
        except ValueError as error:
            raise ValueError(f'{path}: {error}\n{match[2][:100]}') from error
        if result != match[2]:
            changes.append(str(path))
        return match[1] + result + match[3]
    source = path.read_text()
    updated = fence.sub(replace, source)
    if args.write and updated != source:
        path.write_text(updated)
if changes and not args.write:
    raise SystemExit('Go examples need formatting:\n' + '\n'.join(sorted(set(changes))))
print(f'{"Formatted" if args.write else "PASS:"} {count} Go fences; {len(changes)} changed')
