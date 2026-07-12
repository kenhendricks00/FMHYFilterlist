"""Generate explicit URL aliases by resolving a maintained source list."""

import argparse
import json
import sys
from pathlib import Path
from typing import Callable, Iterable
from urllib.parse import urlsplit, urlunsplit
from urllib.request import Request, urlopen


USER_AGENT = "FMHYFilterlist redirect checker/1.0"


def normalize_url(url: str) -> str:
    """Return a stable HTTP(S) URL suitable for comparison and JSON output."""
    parts = urlsplit(url.strip())
    if parts.scheme.lower() not in {"http", "https"} or not parts.hostname:
        raise ValueError(f"Expected an absolute HTTP(S) URL: {url}")
    if parts.username or parts.password:
        raise ValueError(f"Credentials are not allowed in redirect URLs: {url}")

    hostname = parts.hostname.lower()
    port = parts.port
    default_port = (parts.scheme.lower() == "http" and port == 80) or (
        parts.scheme.lower() == "https" and port == 443
    )
    netloc = hostname if port is None or default_port else f"{hostname}:{port}"
    path = parts.path.rstrip("/")
    return urlunsplit((parts.scheme.lower(), netloc, path, parts.query, ""))


def resolve_redirect(url: str, timeout: float = 15.0) -> str:
    """Follow redirects and return the final response URL."""
    request = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=timeout) as response:
        return response.geturl()


def read_sources(path: Path) -> list[str]:
    """Read non-empty, non-comment URL lines and reject duplicates."""
    sources = []
    seen = set()
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        value = line.strip()
        if not value or value.startswith("!") or value.startswith("#"):
            continue
        normalized = normalize_url(value)
        if normalized in seen:
            raise ValueError(f"Duplicate URL on line {line_number}: {normalized}")
        seen.add(normalized)
        sources.append(value)
    return sources


def generate_aliases(
    sources: Iterable[str], resolver: Callable[[str], str] = resolve_redirect
) -> list[dict[str, str]]:
    """Resolve sources into stable, sorted source-to-target alias records."""
    aliases = []
    for source in sources:
        normalized_source = normalize_url(source)
        normalized_target = normalize_url(resolver(source))
        if normalized_source != normalized_target:
            aliases.append(
                {"source": normalized_source, "target": normalized_target}
            )
    return sorted(aliases, key=lambda alias: (alias["source"], alias["target"]))


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Resolve maintained URLs and generate filterlist-redirects.json."
    )
    parser.add_argument(
        "source_file",
        nargs="?",
        default="redirect-sources.txt",
        help="input file containing one URL per line",
    )
    parser.add_argument(
        "--output",
        default="filterlist-redirects.json",
        help="generated JSON output path",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    source_path = Path(args.source_file)
    output_path = Path(args.output)
    aliases = generate_aliases(read_sources(source_path))
    output_path.write_text(
        json.dumps(aliases, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(f"Generated {len(aliases)} redirect aliases in {output_path}.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        raise SystemExit(1)
