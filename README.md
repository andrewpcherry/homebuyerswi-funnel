# Kustom Property Solutions — replacement website preview

Preview: https://andrewpcherry.github.io/homebuyerswi-funnel/

A complete static website preview, built from the existing Kustom funnel and public homebuyerswi.com content. The current production site and DNS are unchanged.

- v2 design across every page (15 September 2026): dark brand heroes, the six-situation picker, per-situation colours, Google rating badge (4.4 stars, 13 reviews, read 15 September 2026). The homepage is built around the original homepage’s H1, headings and copy.
- All 149 sitemap paths represented, including 126 blog articles, company, service area, privacy, comparison and FAQ pages. Source snapshot: 14 September 2026.
- Existing multi-situation assessment at `get-a-cash-offer-today/`; supports inherited, condition, deadline, rental, moving and comparing, including combinations. Original root `?s=` links continue into the matching branch.
- Searchable resource library.
- Preview pages marked noindex. Contact fields are demonstration-only, make no network request and emit no conversion events. Completion explicitly says no inquiry was sent. Do not send paid traffic here.

## SEO carry-over

Every page keeps its original title, meta description, canonical, H1, body text, internal links, images, Open Graph/Twitter/article tags, Google and Facebook verification tags and JSON-LD structured data. `python3 site-source/seo_parity.py` compares each generated page with its downloaded original and writes `migration/seo-parity-report.json`. `migration/sitemap-production.xml` lists the 149 production URLs for launch day.

## Files

`assets/site.css` and `assets/site.js` supply shared presentation and interactions. Generated pages are static HTML. `site-source/build.py` generates the site from the downloaded public sitemap pages; the original funnel is retained as its input. The source-content and metadata snapshot is in `migration/`.

`migration/url-map.csv` maps each current sitemap URL to the identical proposed production URL and its preview URL. It is not a DNS change or an installed redirect configuration.

See `migration/LAUNCH-PLAN.md` for the remaining migration and measurement gates. Production deployment requires choosing the final hosting/CMS, replacing the preview base path and noindex settings, verified inquiry delivery, a successful conversion test, and client approval before DNS changes.
