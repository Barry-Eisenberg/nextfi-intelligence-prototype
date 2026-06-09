from __future__ import annotations

import html
import json
import re
import sys
from pathlib import Path


INDEX_PATH = Path(__file__).resolve().parent.parent / "index.html"
NAV_JSON_PATH = Path(__file__).resolve().parent.parent / "data" / "nav.json"

LEFT_START = "<!-- PRIMARY-NAV-LEFT-START -->"
LEFT_END = "<!-- PRIMARY-NAV-LEFT-END -->"
RIGHT_START = "<!-- PRIMARY-RIGHT-LINKS-START -->"
RIGHT_END = "<!-- PRIMARY-RIGHT-LINKS-END -->"


def load_nav() -> dict:
    return json.loads(NAV_JSON_PATH.read_text(encoding="utf-8"))


def build_nav_item(item: dict) -> str:
    label = html.escape(item["label"])
    href = html.escape(item["href"], quote=True)
    dropdown = item.get("dropdown")
    if not dropdown:
        return f'  <a href="{href}">{label}</a>'
    items_html = "\n".join(
        f'      <li><a href="{html.escape(d["href"], quote=True)}">{html.escape(d["label"])}</a></li>'
        for d in dropdown
    )
    return (
        '        <div class="nav-item has-dropdown">\n'
        f'  <a href="{href}">{label}</a>\n'
        '  <ul class="nav-dropdown">\n'
        f'{items_html}\n'
        '  </ul>\n'
        '</div>'
    )


def build_left_nav(nav: dict) -> str:
    items_html = "\n".join(build_nav_item(item) for item in nav["left"])
    return (
        '      <nav class="nav nav-left" aria-label="Primary navigation left">\n'
        f'{items_html}\n'
        '</nav>'
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
        nav = load_nav()
        left_nav = build_left_nav(nav)
    except (OSError, json.JSONDecodeError, KeyError, RuntimeError) as exc:
        print(f"[sync_primary_nav] Skipped nav sync: {exc}")
        return 1

    index_html = INDEX_PATH.read_text(encoding="utf-8")
    updated = replace_region(index_html, LEFT_START, LEFT_END, left_nav)
    # RIGHT_START/RIGHT_END region is reserved for additional links; leave empty.
    updated = replace_region(updated, RIGHT_START, RIGHT_END, "")

    if updated != index_html:
        INDEX_PATH.write_text(updated, encoding="utf-8")
        print("[sync_primary_nav] Updated shared navigation from nav.json.")
    else:
        print("[sync_primary_nav] Shared navigation already up to date.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
