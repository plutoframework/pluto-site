"""Check that source links resolve without rewriting Go generics or literals."""
import re
import unittest
from doc_markdown import map_prose


class SnapshotLinks(unittest.TestCase):
    def test_preserves_fenced_code_and_resolves_prose(self):
        code = '```go\npayload, err := jobs.Decode[OrderCreated](job)\n```'
        shell = '```sh\nprintf "%s" "[guide](relative.md)"\n```'
        source = '[Guide](relative.md)\n\n' + code + '\n\n' + shell
        actual = map_prose(source, lambda prose: re.sub(
            r'\]\(([^)]+)\)', r'](https://example.test/\1)', prose))
        self.assertIn('[Guide](https://example.test/relative.md)', actual)
        self.assertIn(code, actual)
        self.assertIn(shell, actual)


if __name__ == '__main__':
    unittest.main()
