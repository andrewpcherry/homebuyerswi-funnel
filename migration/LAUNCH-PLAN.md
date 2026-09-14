# Kustom launch and SEO migration plan

Status: replacement website preview, 14 September 2026. Existing production site remains on Carrot. No DNS, campaign, lead destination or tracking settings have been changed.

## Preserve before moving

The public sitemap provided 149 URLs. Every listed path has a corresponding generated page; 126 existing articles are imported. Metadata, source content and the proposed one-to-one route map are saved alongside this document. The homepage is redesigned and rewritten; other imported content retains the existing wording in a simplified layout. This is a public crawl, not a complete Carrot database/export or Search Console inventory.

Before migration, obtain the current Carrot export, Search Console and analytics landing-page reports, redirect rules, verification files and DNS record inventory. Reconcile pages outside the sitemap, feeds, category archives, attachments, image URLs, downloads and existing redirects. Preserve the exact www hostname, paths, titles, canonical intent, internal links and important content wherever possible. Review the rewritten homepage against actual search performance before launch.

Imported article images currently retain their existing Carrot CDN URLs. The primary brand photos and font are local. Copy or otherwise preserve all remaining image/download assets before cancelling Carrot; inventory externally hosted media and confirm their continued availability. Imported legacy advice and privacy text require an editorial/policy review for the new platform. No claim is made that all existing wording is current legal or financial advice.

Choose final production hosting and editing workflow. Build against `/` instead of the GitHub preview prefix, retain every required route, configure real HTTP 301 redirects only for deliberately changed URLs, and verify correct 200/301/404 responses. Preserve email DNS records. Prepare TLS, staging access, backup and rollback before changing web records. A domain registrar transfer is not necessarily required to point web DNS at new hosting.

## Inquiry and conversion acceptance

The preview assessment is local demonstration logic. It does not transmit, save to a CRM, send email/SMS or fire production events. Its completion screen explicitly says no inquiry was sent; SMS consent is optional and recorded separately in the in-memory draft.

Before launch, connect the agreed client lead destination through a server-side endpoint. Validate and normalize inputs server-side; apply abuse protection, deduplication and delivery retries. Show successful submission only after the receiving system confirms acceptance; provide a recoverable error and direct phone option on failure. Keep credentials out of the browser. Preserve source, landing page, consent wording/version/timestamp and attribution parameters, including the advertising click/reference identifiers supported by the final measurement integration.

Test one clearly labelled synthetic submission end-to-end into the actual receiving system, including failure/retry and duplicate handling. Verify the client can see and act on the lead. Review the final privacy notice and consent controls against the actual data flow and registered SMS program. Only then wire the approved conversion event to confirmed successful lead receipt. Attach the correct conversion event to the intended campaign and verify it in the live event stream; avoid double counting browser/server signals. Do not fire a lead conversion on a button click or a visit to a thank-you URL.

## Approval and cutover

1. Review the design with Andrew, then show Riz the preview. No message has been sent from this task.
2. Reconcile and test the final URL/content/asset inventory and production lead/tracking integration.
3. Obtain Riz’s approval and authorized DNS access after the site is accepted. Preserve mail-related records and keep the old hosting available for rollback.
4. Remove preview notices and noindex only on the approved production deployment. Keep staging noindex. Publish a production sitemap with canonical production URLs and preserve search verification.
5. Validate the live pages, redirects, assets, mobile layouts and a confirmed inquiry immediately after cutover; monitor Search Console, indexing, traffic and lead delivery.

SEO migration can preserve URLs, content and signals; unchanged rankings cannot be guaranteed. Google recommends preparing/testing the new site, mapping URLs, retaining assets, and monitoring after migration. Where URLs stay the same, hosting migration guidance also applies.

Sources: https://developers.google.com/search/docs/crawling-indexing/site-move-with-url-changes and https://developers.google.com/search/docs/crawling-indexing/site-move-no-url-changes
