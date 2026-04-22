# NextFi Intelligence Prototype (Localhost)

## Run locally

From this folder, run either command:

```powershell
python -m http.server 8080
```

or

```powershell
py -m http.server 8080
```

Then open:

- http://localhost:8080/

## Included pages

- `index.html` - Intelligence hub
- `reports/*.html` - legacy report summary pages retained temporarily for rollback safety
- `scripts/hub.js` - lightweight topic filter + keyword search on the hub

## Current reading flow

- Hub cards now open source PDFs directly in a new tab.
- Card CTA label standard: `Read full brief`.
- Fuller report descriptions are embedded on cards (`data-summary` + card copy), so users can evaluate relevance before opening the PDF.

## Branding assets copied

- `assets/logos/logo-horizontal-primary.svg` (active header logo)
- `assets/logos/logo-horizontal-reversed.svg`
- `assets/logos/logo-monogram-navy.svg`
- `assets/logos/logo-globe-brand.svg`
- `assets/hero/primary-site-hero.png` (active hub hero image, sourced from primary site)
- `assets/favicons/favicon.ico`
- `assets/favicons/apple-touch-icon.png`

## GoDaddy deployment

- See `DEPLOY-GODADDY.md` for the upload checklist.

## Publish workflow (recommended)

Use the data-driven publisher so report cards and nav menus stay consistent.

Source files:

- `data/reports.json` - report metadata for cards and Intelligence dropdown
- `data/nav.json` - left/right nav structure for the Intelligence site

Publish command:

```powershell
python scripts/publish_intelligence.py
```

Outputs:

- Updates `index.html` cards and nav menus from data files
- Generates `artifacts/godaddy-intelligence-menu-snippet.html` for manual paste into the GoDaddy Intelligence dropdown
- Generates `artifacts/publish-summary.txt`

### Placeholder image behavior

- If a report image path is missing or file is not found, publish uses:
	- `assets/report-covers/report-placeholder-thumb.svg`
- Runtime fallback in `scripts/hub.js` also swaps broken images to the same placeholder.

## Content Builder integration

Your content builder (`https://nextfi-content-builder.onrender.com/`) can be the upstream source of report content.

Near-term flow:

1. Generate the report/PDF in the content builder.
2. Add one report object to `data/reports.json`.
3. Set `image` to a generated thumbnail if available, or leave blank to use placeholder.
4. Run `python scripts/publish_intelligence.py`.
5. Copy `artifacts/godaddy-intelligence-menu-snippet.html` into the GoDaddy nav builder for the primary site.

Fast-add helper:

```powershell
python scripts/add_report.py --from-md "C:\path\to\content-builder-export.md" --meta "April 2026 · AI Strategy · Audience: C-Suite, Strategy" --href "https://.../your-new-report.pdf" --topic "ai-strategy" --type "insight-brief" --audience "c-suite,strategy"
python scripts/publish_intelligence.py
```

If `--image` is omitted, the publisher uses the placeholder thumbnail automatically.

## Category tagging model

The hub now uses structured metadata on each report card:

- `data-topic` (required, one or more values, comma-separated)
- `data-type` (required, one value)
- `data-audience` (required, comma-separated list)

Current controlled values:

- Topic: `ai-strategy`, `enterprise-architecture`, `market-structure`, `tokenization`
- Content type: `insight-brief`, `explainer`, `market-note`, `deep-dive`
- Audience: `c-suite`, `strategy`, `risk`, `treasury`, `technology`

Filtering behavior in `scripts/hub.js` combines:

- keyword search (title + summary)
- topic filter

The filtering controls are rendered above the Featured Brief in a simplified layout:

- Topic pills (single-select)
- Text search in the top navigation bar (McKinsey-style pattern)

The goal is reduced cognitive load while preserving fast discovery.

The hub also uses a left-justified page hero with a companion image panel to create a clearer editorial entry point.

## Methodology for topic tagging

Use this workflow before adding any new report to the hub:

1. Classify the report by primary intent:
	- `ai-strategy`: AI deployment, operating model, governance, enterprise adoption.
	- `enterprise-architecture`: integration standards, system design, orchestration patterns.
	- `market-structure`: liquidity, settlement, intermediaries, macro or market plumbing.
	- `tokenization`: digital assets, stablecoins, DLT rails, tokenized securities.
2. Assign one or more `data-topic` values per card (comma-separated) when the brief is truly cross-domain.
3. Set `data-type` to one editorial format: `insight-brief`, `explainer`, `market-note`, or `deep-dive`.
4. Set `data-audience` as a comma-separated list using only controlled values:
	- `c-suite`, `strategy`, `risk`, `treasury`, `technology`.
5. Write `data-summary` in 1-2 sentences with the key decision signal so keyword search remains high quality.
6. Keep topic pills and controlled values synchronized:
	- if you add a new topic value, add a matching topic pill in `index.html` and update filter labels.
7. QA check after tagging:
	- verify the report appears under `All topics`.
	- verify it appears in each assigned topic filter.
	- verify it does not appear in unassigned topic filters.
	- verify a keyword from the title or summary returns the report.

Practical tie-breaker rule:

- Use one topic when secondary themes are minor.
- Use multi-topic tagging only when two themes are both central to the executive action.

## Per-report card images

Card images use dedicated pre-cropped thumbnail files (`*-thumb.png`) in `assets/report-covers/`. Each thumbnail is a pixel-precise crop of the hero visual from the original cover, with title text and footer stripped.

- Card `<img>` elements reference `*-thumb.png` directly.
- CSS uses `object-position: center center` — no per-card overrides needed.
- To update a card image: replace or regenerate the corresponding `*-thumb.png` using the Pillow crop script pattern from the session history.

Original full-page cover files (`*-cover.png`) are retained in the same folder for reference.

## Header standard for new pages

When adding new pages, keep this exact structure to preserve responsive behavior at desktop, tablet, and mobile breakpoints:

```html
<header class="topbar" aria-label="Primary">
	<a class="brand" href="index.html" aria-label="NextFi Intelligence home">
		<img src="assets/logos/logo-horizontal-primary.svg" alt="NextFi Advisors" />
	</a>
	<nav class="nav" aria-label="Main navigation">
		<a href="https://nextfiadvisors.com/services">Services</a>
		<a href="https://nextfiadvisors.com/our-work">Our Work</a>
		<a href="https://nextfiadvisors.com/contact">Contact</a>
	</nav>
</header>
```

For report-detail pages in the `reports/` folder, use `../assets/logos/logo-horizontal-primary.svg` and keep the same `topbar`, `brand`, and `nav` classes.
