import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPORTS_PATH = ROOT / "data" / "reports.json"


def load_reports():
    data = json.loads(REPORTS_PATH.read_text(encoding="utf-8"))
    return data.get("reports", [])


def save_reports(reports):
    REPORTS_PATH.write_text(json.dumps({"reports": reports}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def extract_from_markdown(path: Path):
    text = path.read_text(encoding="utf-8")

    title_match = re.search(r"^#\s+(.+)$", text, re.M)
    title = title_match.group(1).strip() if title_match else "Untitled report"

    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    summary = ""
    for p in paragraphs:
        if not p.startswith("#"):
            summary = re.sub(r"\s+", " ", p)
            break

    if len(summary) > 320:
        summary = summary[:317].rstrip() + "..."

    return title, summary


def main():
    parser = argparse.ArgumentParser(description="Append a report to data/reports.json")
    parser.add_argument("--title", help="Card heading/title")
    parser.add_argument("--summary", help="1-2 sentence summary")
    parser.add_argument("--meta", required=True, help="Meta line, e.g. April 2026 · AI Strategy · Audience: C-Suite")
    parser.add_argument("--href", required=True, help="PDF or report URL")
    parser.add_argument("--topic", required=True, help="Topic value(s), comma-separated")
    parser.add_argument("--type", required=True, dest="content_type", help="Content type: insight-brief|explainer|market-note|deep-dive")
    parser.add_argument("--audience", required=True, help="Audience value(s), comma-separated")
    parser.add_argument("--image", default="", help="Thumbnail path; leave blank to use placeholder")
    parser.add_argument("--menu-label", default="", help="Optional shorter Intelligence dropdown label")
    parser.add_argument("--menu-href", default="", help="Optional Intelligence dropdown URL override")
    parser.add_argument("--from-md", default="", help="Optional markdown from Content Builder to auto-fill title+summary")
    args = parser.parse_args()

    title = args.title or ""
    summary = args.summary or ""

    if args.from_md:
        md_title, md_summary = extract_from_markdown(Path(args.from_md))
        if not title:
            title = md_title
        if not summary:
            summary = md_summary

    if not title or not summary:
        raise SystemExit("You must provide title+summary, or pass --from-md with parsable content.")

    report = {
        "topic": args.topic,
        "type": args.content_type,
        "audience": args.audience,
        "title": title,
        "summary": summary,
        "image": args.image,
        "image_alt": f"Cover of {title}",
        "meta": args.meta,
        "heading": title,
        "description": summary,
        "href": args.href,
        "cta": "Read full brief",
        "menu_label": args.menu_label or title,
        "menu_href": args.menu_href or args.href,
    }

    reports = load_reports()
    reports.insert(0, report)
    save_reports(reports)

    print(f"Added report: {title}")
    print("Now run: python scripts/publish_intelligence.py")


if __name__ == "__main__":
    main()
