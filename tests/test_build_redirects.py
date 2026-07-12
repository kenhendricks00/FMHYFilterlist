import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import build_redirects


class BuildRedirectsTests(unittest.TestCase):
    def test_normalize_url_preserves_paths_and_removes_fragments(self):
        self.assertEqual(
            build_redirects.normalize_url(
                "HTTPS://Example.COM/path/?query=value#section"
            ),
            "https://example.com/path?query=value",
        )

    def test_generate_aliases_omits_unchanged_urls_and_sorts_results(self):
        sources = [
            "https://second.example/old",
            "https://same.example/",
            "https://first.example/old",
        ]
        destinations = {
            sources[0]: "https://destination.example/two/",
            sources[1]: "https://same.example/",
            sources[2]: "https://destination.example/one",
        }

        aliases = build_redirects.generate_aliases(
            sources, resolver=destinations.__getitem__
        )

        self.assertEqual(
            aliases,
            [
                {
                    "source": "https://first.example/old",
                    "target": "https://destination.example/one",
                },
                {
                    "source": "https://second.example/old",
                    "target": "https://destination.example/two",
                },
            ],
        )

    def test_main_writes_generated_json_from_source_file(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source_file = root / "redirect-sources.txt"
            output_file = root / "filterlist-redirects.json"
            source_file.write_text(
                "! comment\nhttps://alienflix.net/\n\n", encoding="utf-8"
            )

            with patch.object(
                build_redirects,
                "resolve_redirect",
                return_value="https://hdtodayz.net/",
            ):
                result = build_redirects.main(
                    [str(source_file), "--output", str(output_file)]
                )

            self.assertEqual(result, 0)
            self.assertEqual(
                json.loads(output_file.read_text(encoding="utf-8")),
                [
                    {
                        "source": "https://alienflix.net",
                        "target": "https://hdtodayz.net",
                    }
                ],
            )


if __name__ == "__main__":
    unittest.main()
