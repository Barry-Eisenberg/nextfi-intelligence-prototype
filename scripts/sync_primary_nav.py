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

REPORTS_DIR = Path(__file__).resolve().parent.parent / "reports"

# Google Analytics. Injected at build time so a newly authored report is tagged
# without anyone having to remember to paste the snippet into its <head>.
GA_MEASUREMENT_ID = "G-J8Z8PKZL3N"
GA_SNIPPET = """
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id={id}"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());

  gtag('config', '{id}');
</script>
""".format(id=GA_MEASUREMENT_ID)

CHARSET_RE = re.compile(r"<meta[^>]*charset=[^>]*>", re.I)
HEAD_RE = re.compile(r"<head\b[^>]*>", re.I)


def load_nav() -> dict:
    return json.loads(NAV_JSON_PATH.read_text(encoding="utf-8"))


def build_nav_item(item: dict) -> str:
    label = html.escape(item["label"])
    href = html.escape(item["href"], quote=True)
    dropdown = item.get("dropdown")
    cta = item.get("cta", False)
    dropdown_right = item.get("dropdownRight", False)

    if not dropdown:
        cls = ' class="nav-cta"' if cta else ""
        return f'  <a{cls} href="{href}">{label}</a>'

    dropdown_cls = 'nav-dropdown nav-section-links' if dropdown_right else 'nav-dropdown'
    items_html = "\n".join(
        f'      <li><a href="{html.escape(d["href"], quote=True)}">{html.escape(d["label"])}</a></li>'
        for d in dropdown
    )
    return (
        '        <div class="nav-item has-dropdown">\n'
        f'  <a href="{href}">{label}</a>\n'
        f'  <ul class="{dropdown_cls}">\n'
        f'{items_html}\n'
        '  </ul>\n'
        '</div>'
    )


def build_left_nav(nav: dict) -> str:
    items_html = "\n".join(build_nav_item(item) for item in nav["left"])
    right_block = f"{RIGHT_START}\n\n{RIGHT_END}"
    return (
        '      <nav id="primary-mobile-nav" class="nav nav-right" aria-label="Primary navigation">\n'
        f'{items_html}\n'
        f'  {right_block}\n'
        '</nav>'
    )


def replace_region(document: str, start_marker: str, end_marker: str, replacement: str) -> str:
    pattern = re.compile(re.escape(start_marker) + r".*?" + re.escape(end_marker), re.DOTALL)
    replacement_block = f"{start_marker}\n{replacement}\n{end_marker}"
    updated, count = pattern.subn(replacement_block, document, count=1)
    if count != 1:
        raise RuntimeError(f"Could not replace region between {start_marker} and {end_marker}")
    return updated


def ensure_ga_tag(path: Path) -> bool:
    """Add the gtag snippet to path's <head> unless it is already there.

    Idempotent, so it is safe to run on every build. The snippet goes after
    <meta charset> when there is one, keeping the charset declaration first.
    """
    with path.open("r", encoding="utf-8", newline="") as fh:
        document = fh.read()

    if GA_MEASUREMENT_ID in document:
        return False

    head = document[:4000]
    anchor = CHARSET_RE.search(head) or HEAD_RE.search(head)
    if anchor is None:
        print(f"[sync_primary_nav] No <head> anchor in {path.name}; GA tag skipped.")
        return False

    snippet = GA_SNIPPET.replace("\n", "\r\n") if "\r\n" in head else GA_SNIPPET
    with path.open("w", encoding="utf-8", newline="") as fh:
        fh.write(document[: anchor.end()] + snippet + document[anchor.end() :])
    return True


def sync_ga_tags() -> None:
    pages = [INDEX_PATH, *sorted(REPORTS_DIR.glob("*.html"))]
    tagged = 0
    for page in pages:
        try:
            if ensure_ga_tag(page):
                tagged += 1
                print(f"[sync_primary_nav] Added GA tag to {page.name}.")
        except OSError as exc:
            # Never fail the build over analytics.
            print(f"[sync_primary_nav] Could not tag {page.name}: {exc}")
    if not tagged:
        print("[sync_primary_nav] GA tag already present on all pages.")


def main() -> int:
    sync_ga_tags()

    try:
        nav = load_nav()
        left_nav = build_left_nav(nav)
    except (OSError, json.JSONDecodeError, KeyError, RuntimeError) as exc:
        print(f"[sync_primary_nav] Skipped nav sync: {exc}")
        return 1

    index_html = INDEX_PATH.read_text(encoding="utf-8")
    updated = replace_region(index_html, LEFT_START, LEFT_END, left_nav)

    if updated != index_html:
        INDEX_PATH.write_text(updated, encoding="utf-8")
        print("[sync_primary_nav] Updated shared navigation from nav.json.")
    else:
        print("[sync_primary_nav] Shared navigation already up to date.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
