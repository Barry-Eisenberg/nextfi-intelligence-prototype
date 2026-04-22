from __future__ import annotations

import html
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen


BASE_URL = "https://nextfiadvisors.com/"
INDEX_PATH = Path(__file__).resolve().parent.parent / "index.html"

LEFT_START = "<!-- PRIMARY-NAV-LEFT-START -->"
LEFT_END = "<!-- PRIMARY-NAV-LEFT-END -->"
RIGHT_START = "<!-- PRIMARY-RIGHT-LINKS-START -->"
RIGHT_END = "<!-- PRIMARY-RIGHT-LINKS-END -->"


class AnchorCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.anchors: list[tuple[str, str]] = []
        self._href: str | None = None
        self._text_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "a":
            return
        attr_map = dict(attrs)
        self._href = attr_map.get("href")
        self._text_parts = []

    def handle_data(self, data: str) -> None:
        if self._href is not None:
            self._text_parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag != "a" or self._href is None:
            return
        text = " ".join(part.strip() for part in self._text_parts if part.strip())
        if text:
            self.anchors.append((text, self._href))
        self._href = None
        self._text_parts = []


def normalize_label(label: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(label or "")).strip().lower()


def fetch_primary_html() -> str:
    request = Request(
        BASE_URL,
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; NextFiNavSync/1.0)",
            "Accept": "text/html,application/xhtml+xml",
        },
    )
    with urlopen(request, timeout=20) as response:
        return response.read().decode("utf-8", errors="replace")


def collect_link_map(source_html: str) -> dict[str, str]:
    parser = AnchorCollector()
    parser.feed(source_html)
    links: dict[str, str] = {}
    for text, href in parser.anchors:
        key = normalize_label(text)
        if key and key not in links:
            links[key] = urljoin(BASE_URL, href)
    return links


def required_link(links: dict[str, str], label: str) -> str:
    key = normalize_label(label)
    href = links.get(key)
    if not href:
        raise KeyError(label)
    return href


def build_left_nav(links: dict[str, str]) -> str:
    about_items = ["Services", "Why Us", "Who We Are", "Contact"]
    case_study_items = [
        "FI Tokenization Op Model",
        "Stablecoin Payments Model",
        "Demand for Tokenized RWA",
        "RWA Distribution Model",
    ]

    about_html = "\n".join(
        f'      <li><a href="{html.escape(required_link(links, label), quote=True)}">{html.escape(label)}</a></li>'
        for label in about_items
    )
    case_html = "\n".join(
        f'      <li><a href="{html.escape(required_link(links, label), quote=True)}">{html.escape(label)}</a></li>'
        for label in case_study_items
    )

    return (
        '      <nav class="nav nav-left" aria-label="Primary navigation left">\n'
        f'  <a href="{html.escape(required_link(links, "Home"), quote=True)}">Home</a>\n'
        '        <div class="nav-item has-dropdown">\n'
        f'  <a href="{html.escape(required_link(links, "Why Us"), quote=True)}">About</a>\n'
        '  <ul class="nav-dropdown">\n'
        f'{about_html}\n'
        '  </ul>\n'
        '</div>\n'
        '        <div class="nav-item has-dropdown">\n'
        f'  <a href="{html.escape(required_link(links, "Our Work"), quote=True)}">Case Studies</a>\n'
        '  <ul class="nav-dropdown">\n'
        f'{case_html}\n'
        '  </ul>\n'
        '</div>\n'
        '</nav>'
    )


def build_right_links(links: dict[str, str]) -> str:
    sfts_href = required_link(links, "SftS")
    convergence_href = required_link(links, "Convergence")
    return (
        f'  <a href="{html.escape(sfts_href, quote=True)}">SFTS</a>\n'
        f'  <a href="{html.escape(convergence_href, quote=True)}">Convergence</a>'
    )


def replace_region(document: str, start_marker: str, end_marker: str, replacement: str) -> str:
    pattern = re.compile(re.escape(start_marker) + r".*?" + re.escape(end_marker), re.DOTALL)
    replacement_block = f"{start_marker}\n{replacement}\n{end_marker}"
    updated, count = pattern.subn(replacement_block, document, count=1)
    if count != 1:
        raise RuntimeError(f"Could not replace region between {start_marker} and {end_marker}")
    return updated


def main() -> int:
    try:
        primary_html = fetch_primary_html()
        links = collect_link_map(primary_html)
        left_nav = build_left_nav(links)
        right_links = build_right_links(links)
    except (URLError, TimeoutError, KeyError, RuntimeError) as exc:
        print(f"[sync_primary_nav] Skipped nav sync: {exc}")
        return 0

    index_html = INDEX_PATH.read_text(encoding="utf-8")
    updated = replace_region(index_html, LEFT_START, LEFT_END, left_nav)
    updated = replace_region(updated, RIGHT_START, RIGHT_END, right_links)

    if updated != index_html:
        INDEX_PATH.write_text(updated, encoding="utf-8")
        print("[sync_primary_nav] Updated shared navigation from primary site.")
    else:
        print("[sync_primary_nav] Shared navigation already up to date.")
    return 0


if __name__ == "__main__":
    sys.exit(main())