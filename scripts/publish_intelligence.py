import argparse
import html
import json
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INDEX_PATH = ROOT / "index.html"
REPORTS_PATH = ROOT / "data" / "reports.json"
NAV_PATH = ROOT / "data" / "nav.json"
PLACEHOLDER_IMAGE = "assets/report-covers/report-placeholder-thumb.svg"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def esc(value: str) -> str:
    return html.escape(value or "", quote=True)


def ensure_reports(reports):
    normalized = []
    for report in reports:
        use_placeholder = bool(report.get("use_placeholder", False))
        image = report.get("image", "").strip()
        image_exists = bool(image) and (ROOT / image).exists()
        if use_placeholder or not image_exists:
            image = PLACEHOLDER_IMAGE

        title = report.get("heading") or report.get("title") or "Untitled report"
        summary = report.get("description") or report.get("summary") or ""

        normalized.append(
            {
                "topic": report.get("topic", "market-structure"),
                "type": report.get("type", "insight-brief"),
                "audience": report.get("audience", "strategy"),
                "title": report.get("title", title),
                "summary": report.get("summary", summary),
                "image": image,
                "image_alt": report.get("image_alt", f"Cover of {title}"),
                "meta": report.get("meta", ""),
                "heading": title,
                "description": summary,
                "href": report.get("href", "#"),
                "cta": report.get("cta", "Read full brief"),
                "menu_href": report.get("menu_href", report.get("href", "#")),
                "menu_label": report.get("menu_label", title),
                "use_placeholder": use_placeholder,
            }
        )
    return normalized


def render_nav_item(item):
    label = esc(item.get("label", ""))
    href = esc(item.get("href", "#"))
    dropdown = item.get("dropdown")
    if not dropdown:
        return f'<a href="{href}">{label}</a>'

    dropdown_items = []
    for child in dropdown:
        dropdown_items.append(
            f'      <li><a href="{esc(child.get("href", "#"))}">{esc(child.get("label", ""))}</a></li>'
        )

    return "\n".join(
        [
            '<div class="nav-item has-dropdown">',
            f'  <a href="{href}">{label}</a>',
            '  <ul class="nav-dropdown">',
            *dropdown_items,
            '  </ul>',
            '</div>',
        ]
    )


def render_intelligence_dropdown(item, reports):
    max_items = int(item.get("maxItems", 12))
    links = reports[:max_items]

    rows = []
    for report in links:
        rows.append(
            f'      <li><a href="{esc(report["menu_href"])}">{esc(report["menu_label"])}</a></li>'
        )

    label = esc(item.get("label", "Intelligence"))
    href = esc(item.get("href", "index.html"))
    return "\n".join(
        [
            '<div class="nav-item has-dropdown">',
            f'  <a href="{href}">{label}</a>',
            '  <ul class="nav-dropdown nav-dropdown-right">',
            *rows,
            '  </ul>',
            '</div>',
        ]
    )


def render_cards(reports):
    blocks = []
    for r in reports:
        blocks.append(
            "\n".join(
                [
                    f'<article class="card" data-topic="{esc(r["topic"])}" data-type="{esc(r["type"])}" data-audience="{esc(r["audience"])}" data-title="{esc(r["title"])}" data-summary="{esc(r["summary"])}">',
                    '  <figure class="card-media">',
                    f'    <img src="{esc(r["image"])}" alt="{esc(r["image_alt"])}" loading="lazy" />',
                    '  </figure>',
                    '  <div class="card-body">',
                    f'    <p class="meta">{esc(r["meta"])}</p>',
                    f'    <h3>{esc(r["heading"])}</h3>',
                    f'    <p>{esc(r["description"])}</p>',
                    f'    <a href="{esc(r["href"])}" target="_blank" rel="noopener noreferrer">{esc(r["cta"])}</a>',
                    '  </div>',
                    '</article>',
                ]
            )
        )
    return "\n\n        ".join(blocks)


def update_index(reports, nav):
    html_text = INDEX_PATH.read_text(encoding="utf-8")

    left_rows = "\n        ".join(render_nav_item(item) for item in nav.get("left", []))
    left_nav = '\n'.join([
        '<nav class="nav nav-left" aria-label="Primary navigation left">',
        f'  {left_rows}',
        '</nav>',
    ])

    right_rows = []
    for item in nav.get("right", []):
        if item.get("dropdownFromReports"):
            right_rows.append(render_intelligence_dropdown(item, reports))
        elif item.get("dropdown"):
            label = esc(item.get("label", ""))
            href = esc(item.get("href", "#"))
            dropdown_items = [
                f'      <li><a href="{esc(child.get("href", "#"))}">{esc(child.get("label", ""))}</a></li>'
                for child in item["dropdown"]
            ]
            right_rows.append("\n".join([
                '<div class="nav-item has-dropdown">',
                f'  <a href="{href}">{label}</a>',
                '  <ul class="nav-dropdown nav-section-links">',
                *dropdown_items,
                '  </ul>',
                '</div>',
            ]))
        else:
            right_rows.append(f'<a href="{esc(item.get("href", "#"))}">{esc(item.get("label", ""))}</a>')

    right_nav = '\n'.join([
        '<nav id="primary-mobile-nav" class="nav nav-right" aria-label="Primary navigation right">',
        '  ' + '\n  '.join(right_rows),
        '  <!-- PRIMARY-RIGHT-LINKS-START -->',
        '<!-- PRIMARY-RIGHT-LINKS-END -->',
        '</nav>',
    ])

    cards_html = render_cards(reports)

    html_text = re.sub(
        r'<nav class="nav nav-left" aria-label="Primary navigation left">.*?</nav>',
        left_nav,
        html_text,
        count=1,
        flags=re.S,
    )
    html_text = re.sub(
        r'<nav[^>]*class="nav nav-right"[^>]*aria-label="Primary navigation right"[^>]*>.*?</nav>',
        right_nav,
        html_text,
        count=1,
        flags=re.S,
    )

    html_text = re.sub(
        r'<div class="cards" id="report-cards">.*?</div>\s*<p id="no-results"',
        '<div class="cards" id="report-cards">\n        ' + cards_html + '\n      </div>\n      <p id="no-results"',
        html_text,
        count=1,
        flags=re.S,
    )

    html_text = re.sub(
        r'<p id="results-count" class="results-count" aria-live="polite">.*?</p>',
        f'<p id="results-count" class="results-count" aria-live="polite">Showing {len(reports)} of {len(reports)} briefs</p>',
        html_text,
        count=1,
        flags=re.S,
    )

    INDEX_PATH.write_text(html_text, encoding="utf-8")


def write_artifacts(reports):
    artifacts = ROOT / "artifacts"
    artifacts.mkdir(exist_ok=True)

    menu_items = [f'<li><a href="{esc(r["menu_href"])}">{esc(r["menu_label"])}</a></li>' for r in reports[:12]]
    snippet = "\n".join(menu_items)
    (artifacts / "godaddy-intelligence-menu-snippet.html").write_text(snippet + "\n", encoding="utf-8")

    summary = [
        "Intelligence publish output",
        f"- Reports rendered: {len(reports)}",
        "- Index updated: index.html",
        "- GoDaddy nav snippet: artifacts/godaddy-intelligence-menu-snippet.html",
        "",
        "If you update GoDaddy nav manually, paste snippet items into the Intelligence dropdown in the GoDaddy builder.",
    ]
    (artifacts / "publish-summary.txt").write_text("\n".join(summary) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Publish intelligence index from structured data.")
    parser.add_argument("--reports", default=str(REPORTS_PATH), help="Path to reports JSON")
    parser.add_argument("--nav", default=str(NAV_PATH), help="Path to nav JSON")
    args = parser.parse_args()

    reports_data = load_json(Path(args.reports))
    nav_data = load_json(Path(args.nav))

    reports = ensure_reports(reports_data.get("reports", []))
    update_index(reports, nav_data)
    write_artifacts(reports)

    print(f"Published {len(reports)} reports to index.html")
    print("Generated artifacts/godaddy-intelligence-menu-snippet.html")


if __name__ == "__main__":
    main()
