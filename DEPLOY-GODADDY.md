# GoDaddy Deploy Checklist (HTML Site)

## 1. Upload package contents

Upload these files and folders to your GoDaddy target directory:

- `index.html`
- `styles.css`
- `reports/`
- `assets/`
- `scripts/`

If this section is the site root, upload directly to root. If this is a subpath, upload into that folder (for example `/intelligence/`).

## 2. Validate required paths

Open these URLs after upload:

- `/index.html` (or `/intelligence/index.html`)

## 3. Verify assets

- Logo renders in the top header on hub and report pages.
- Favicon appears in browser tab.
- Card filter buttons and search input work.
- PDF download links open correctly.

## 4. Optional routing polish

If GoDaddy supports rewrite rules and you want cleaner URLs (without `.html`), configure rewrites after initial upload. Keep this version as direct `.html` links for reliability.

## 5. Nav sync between Netlify and GoDaddy

Before deploy, run:

```powershell
python scripts/publish_intelligence.py
```

Then:

1. Deploy updated files to Netlify (Intelligence site).
2. Open `artifacts/godaddy-intelligence-menu-snippet.html`.
3. Paste those `<li>` rows into the Intelligence dropdown in the GoDaddy website builder.

This keeps Intelligence menu links aligned across both hosting stacks.
