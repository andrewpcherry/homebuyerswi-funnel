"""Generate the Kustom Property Solutions replacement website preview.

Inputs: the public sitemap URL list and the downloaded public pages (one HTML file per URL),
plus site-source/funnel-original.html for the multi-situation assessment.

SEO carry-over per page, taken verbatim from the downloaded original:
title, meta description, canonical intent, H1, body content, internal links, images and alts,
Open Graph / Twitter / article metas, search-engine verification metas and JSON-LD structured data.
Preview pages stay noindex until the approved production deployment.
Run site-source/seo_parity.py after building to compare every page against its original.
"""
from pathlib import Path
from bs4 import BeautifulSoup, Comment
from urllib.parse import urlparse, urljoin
import json, re, html, csv, copy

ROOT = Path(__file__).resolve().parents[1]
BASE = '/homebuyerswi-funnel/'
ORIGIN = 'https://www.homebuyerswi.com'
RAW = Path('/private/tmp/kustom-raw')
urls = json.loads(Path('/private/tmp/kustom-url-list.json').read_text())
paths = [urlparse(x).path for x in urls]
esc = html.escape
CSS_V = '20260915f'

# Google Business Profile, read 2026-09-15 from the listing Andrew supplied: 4.4 stars, 13 reviews.
GOOGLE_URL = 'https://www.google.com/maps/place/Kustom+Property+Solutions,+LLC/@42.9506009,-88.1444982,17z/data=!3m1!4b1!4m6!3m5!1s0x880509beb1b6aaab:0x8f73591c1bb93736!8m2!3d42.9506009!4d-88.1444982!16s%2Fg%2F11ggsgj7nk'
G_RATING, G_COUNT = '4.4', '13'
PHONE, TEL = '(262) 432-1760', 'tel:+12624321760'
# Name, address and phone as published in Kustom's own LocalBusiness structured data.
ADDRESS = '5165 S. Brennan Drive<br>New Berlin, Wisconsin 53146'


def link(path=''):
    return BASE + path.lstrip('/')


def norm(t):
    return re.sub(r'\s+', ' ', (t or '').replace('\xa0', ' ')).strip()


ICONS = '''<svg width="0" height="0" style="position:absolute" aria-hidden="true">
<symbol id="i-inherited" viewBox="0 0 24 24"><path d="M3 11.5 12 4l9 7.5"/><path d="M5.5 9.8V20h13V9.8"/><path d="M12 17.2s-3-1.8-3-3.9a1.6 1.6 0 0 1 3-.8 1.6 1.6 0 0 1 3 .8c0 2.1-3 3.9-3 3.9Z"/></symbol>
<symbol id="i-condition" viewBox="0 0 24 24"><path d="M14.7 6.3a4 4 0 0 0 5 5L12 19a2.1 2.1 0 0 1-3-3l7.7-7.7"/><path d="m4 4 5 5"/><path d="M3 7.5 7.5 3"/></symbol>
<symbol id="i-deadline" viewBox="0 0 24 24"><circle cx="12" cy="13" r="8"/><path d="M12 9v4l2.5 2.5"/><path d="M9.5 2.5h5"/></symbol>
<symbol id="i-rental" viewBox="0 0 24 24"><circle cx="8" cy="15" r="4.5"/><path d="m11.2 11.8 8.3-8.3"/><path d="m16.5 6.5 2.5 2.5"/><path d="m14 9 2 2"/></symbol>
<symbol id="i-moving" viewBox="0 0 24 24"><path d="M2.5 6.5h11v10h-11z"/><path d="M13.5 10h4.2l3.8 3.6v2.9h-8"/><circle cx="6.5" cy="17.5" r="2"/><circle cx="17" cy="17.5" r="2"/></symbol>
<symbol id="i-comparing" viewBox="0 0 24 24"><path d="M12 3v18"/><path d="M7 21h10"/><path d="M5 7h14"/><path d="m5 7-3 6.5a3.2 3.2 0 0 0 6 0Z"/><path d="m19 7-3 6.5a3.2 3.2 0 0 0 6 0Z"/></symbol>
<symbol id="i-arrow" viewBox="0 0 24 24"><path d="M5 12h14"/><path d="m13 6 6 6-6 6"/></symbol>
<symbol id="i-phone" viewBox="0 0 24 24"><path d="M21 16.4v3a2 2 0 0 1-2.2 2A19.8 19.8 0 0 1 2.6 5.2 2 2 0 0 1 4.6 3h3a2 2 0 0 1 2 1.7c.1.9.4 1.8.7 2.7a2 2 0 0 1-.5 2.1L8.6 10.7a16 16 0 0 0 4.7 4.7l1.2-1.2a2 2 0 0 1 2.1-.5c.9.3 1.8.6 2.7.7a2 2 0 0 1 1.7 2Z"/></symbol>
<symbol id="i-pin" viewBox="0 0 24 24"><path d="M12 21s-7-6.2-7-11.5a7 7 0 0 1 14 0C19 14.8 12 21 12 21Z"/><circle cx="12" cy="9.5" r="2.5"/></symbol>
<symbol id="i-check" viewBox="0 0 24 24"><path d="m5 12.5 4.5 4.5L19 7.5"/></symbol>
<symbol id="i-hammer" viewBox="0 0 24 24"><path d="m15 12-8.5 8.5a2.1 2.1 0 0 1-3-3L12 9"/><path d="m17.6 15 4.4-4.4-6.6-6.6-4.4 4.4Z"/></symbol>
<symbol id="i-cash" viewBox="0 0 24 24"><rect x="2.5" y="6" width="19" height="12" rx="2"/><circle cx="12" cy="12" r="2.6"/><path d="M6 12h.01M18 12h.01"/></symbol>
<symbol id="i-calendar" viewBox="0 0 24 24"><rect x="3" y="4.5" width="18" height="16" rx="2"/><path d="M3 9.5h18M8 2.5v4M16 2.5v4"/></symbol>
<symbol id="i-hand" viewBox="0 0 24 24"><path d="M12 21a8 8 0 1 0 0-16 8 8 0 0 0 0 16Z"/><path d="m9 12.5 2 2 4-4.5"/></symbol>
<symbol id="i-user" viewBox="0 0 24 24"><circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/></symbol>
<symbol id="i-doc" viewBox="0 0 24 24"><path d="M14 3H6.5A1.5 1.5 0 0 0 5 4.5v15A1.5 1.5 0 0 0 6.5 21h11a1.5 1.5 0 0 0 1.5-1.5V8Z"/><path d="M14 3v5h5M9 13h6M9 17h4"/></symbol>
<symbol id="i-smile" viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="M8.5 14.5a4.5 4.5 0 0 0 7 0M9 9.5h.01M15 9.5h.01"/></symbol>
<symbol id="i-book" viewBox="0 0 24 24"><path d="M4 5.5A2.5 2.5 0 0 1 6.5 3H20v15H6.5A2.5 2.5 0 0 0 4 20.5Z"/><path d="M4 20.5A2.5 2.5 0 0 0 6.5 23H20v-5"/></symbol>
</svg>'''

SITUATIONS = [
    ('inherited', 'violet', 'I inherited it', 'Estate', 'An inherited house', 'A family property, belongings to sort, and decisions to make. Often from out of state.'),
    ('condition', 'gold', 'It needs a lot of work', 'Condition', 'More repairs than you want', 'An aging roof, foundation problems, or a house that needs work.'),
    ('deadline', 'crimson', 'I’m up against a deadline', 'Time pressure', 'A deadline to work around', 'Payments, a move, or another reason time matters.'),
    ('rental', 'brand', 'It’s a rental I’m done with', 'Landlord', 'Ready to leave a rental behind', 'Tenants, maintenance, and a property you’re ready to let go.'),
    ('moving', 'emerald', 'I’m moving by a date', 'Timeline', 'A change in your life', 'Relocating, downsizing, or figuring out your next chapter.'),
    ('comparing', 'slate-l', 'Just weighing it up', 'Comparing', 'Just exploring your options', 'Compare a direct sale with listing, side by side, without committing to anything.'),
]
AREAS = [('Milwaukee', 'sell-your-house/'), ('Waukesha', 'we-buy-houses-waukesha-wi/'), ('New Berlin', 'we-buy-houses-new-berlin-wi/'),
         ('Wauwatosa', 'we-buy-houses-wauwatosa-wi/'), ('Racine', 'we-buy-houses-racine-wi/'), ('Greenfield', 'we-buy-houses-greenfield-wi/')]
QUIZ = link('get-a-cash-offer-today/')


def icon(name, cls=''):
    return f'<svg{" class=%s" % chr(34) + cls + chr(34) if cls else ""}><use href="#i-{name}"/></svg>'


def btn(label='See my selling options', href=QUIZ, cls='btn'):
    return f'<a class="{cls}" href="{href}">{label} {icon("arrow")}</a>'


def g_badge(cls=''):
    return (f'<a class="g-badge {cls}" href="{GOOGLE_URL}" target="_blank" rel="noopener">'
            f'<span class="g-logo" aria-hidden="true">G</span><b>{G_RATING}</b>'
            f'<span class="stars" style="--rating:{G_RATING}" aria-hidden="true">★★★★★</span>'
            f'<small>{G_COUNT} Google reviews</small></a>')


def chips(cls='chips'):
    return f'<div class="{cls}">' + ''.join(
        f'<a class="chip" style="--c:var(--{c})" href="{QUIZ}?s={k}#quiz"><i>{icon(k)}</i><span>{label}</span>{icon("arrow", "go")}</a>'
        for k, c, label, *_ in SITUATIONS) + '</div>'


def header():
    nav = [('How it works', 'how-we-buy-houses/'), ('Meet Riz', 'our-company/'), ('Seller stories', 'testimonials/'), ('Resources', 'blog/'), ('FAQs', 'faq/')]
    return (f'{ICONS}<a class="skip" href="#main">Skip to content</a>'
            f'<div class="preview-bar">Website preview <span>Forms are in demonstration mode · No inquiries are sent</span></div>'
            f'<header class="site-header" data-header><div class="container nav">'
            f'<a class="logo" href="{link()}"><img src="{link("img/logo-blue.svg")}" alt="Kustom Property Solutions home" width="195" height="68"></a>'
            f'<nav id="navigation" aria-label="Main navigation">' + ''.join(f'<a href="{link(p)}">{n}</a>' for n, p in nav) + '</nav>'
            f'<div class="nav-right"><a class="nav-phone" href="{TEL}">{icon("phone")}<span><small>Talk to a local buyer</small>{PHONE}</span></a>'
            f'<a class="btn btn-sm" href="{QUIZ}">See my options</a>'
            f'<button class="menu-toggle" aria-expanded="false" aria-controls="navigation"><span></span><span></span><span class="sr">Menu</span></button></div>'
            f'</div></header>')


def closing():
    return (f'<section class="closing"><div class="closing-rings"><span></span><span></span><span></span></div>'
            f'<div class="container closing-inner reveal"><p class="eyebrow light">Your house. Your next chapter.</p>'
            f'<h2>Let’s work out what makes sense for you.</h2><p>A few questions. A real conversation. No obligation to sell.</p>'
            f'<div class="closing-actions">{btn(cls="btn btn-lg")}<a class="btn-ghost" href="{TEL}">{icon("phone")}{PHONE}</a></div>'
            f'<ul class="closing-checks"><li>{icon("check")}No repairs</li><li>{icon("check")}No agent commissions</li><li>{icon("check")}No pressure</li></ul></div></section>')


def footer(sticky=True):
    s = (f'<div class="sticky-cta" data-sticky><a class="call" href="{TEL}" aria-label="Call {PHONE}">{icon("phone")}</a>{btn()}</div>' if sticky else '')
    return (f'<footer class="site-footer"><div class="container footer-grid">'
            f'<div class="footer-brand"><span class="logo-chip"><img src="{link("img/logo-blue.svg")}" alt="Kustom Property Solutions" width="195" height="68"></span>'
            f'<p>Local home buyers.<br>Milwaukee &amp; southeastern Wisconsin.</p>{g_badge("dark")}</div>'
            f'<div><b>Explore</b><a href="{link("our-company/")}">Our company</a><a href="{link("how-we-buy-houses/")}">How it works</a><a href="{link("compare/")}">Compare your options</a><a href="{link("testimonials/")}">Seller stories</a><a href="{link("contact-us/")}">Contact us</a></div>'
            f'<div><b>For homeowners</b><a href="{link("blog/")}">Seller resources</a><a href="{link("selling-an-inherited-property-wisconsin/")}">Inherited a property</a><a href="{link("can-i-sell-my-house-in-foreclosure-in-wisconsin/")}">Facing foreclosure</a><a href="{link("faq/")}">Frequently asked questions</a><a href="{link("privacy/")}">Privacy policy</a></div>'
            f'<div><b>We buy houses in</b>' + ''.join(f'<a href="{link(p)}">{n}</a>' for n, p in AREAS) + '</div>'
            f'<div><b>Start a conversation</b><a class="footer-phone" href="{TEL}">{PHONE}</a><p>Kustom Property Solutions<br>{ADDRESS}</p></div>'
            f'</div><div class="container footer-bottom">© 2026 Kustom Property Solutions <span>Website preview · No inquiries are sent from this preview.</span></div></footer>'
            f'{s}<script src="{link("assets/site.js?v=" + CSS_V)}" defer></script>')


def page(title, body, path='', description='', seo='', extra='', body_cls='', sticky=True):
    canonical = f'{ORIGIN}/{path.lstrip("/")}'
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>{esc(title)}</title><meta name="description" content="{esc(description)}"><meta name="robots" content="noindex,nofollow">'
            f'<link rel="canonical" href="{canonical}">{seo}<meta name="theme-color" content="#021D27">'
            f'<link rel="icon" href="{link("img/favicon.png")}"><link rel="apple-touch-icon" href="{link("img/favicon.png")}">'
            f'<link rel="preload" href="{link("assets/source-sans.woff2")}" as="font" type="font/woff2" crossorigin>'
            f'<link rel="stylesheet" href="{link("assets/site.css?v=" + CSS_V)}"><script>document.documentElement.classList.add("js")</script>{extra}</head>'
            f'<body class="{body_cls}">{header()}<main id="main">{body}</main>{closing()}{footer(sticky)}</body></html>')


def write(path, content):
    p = ROOT / (path.strip('/') + '/index.html' if path.strip('/') else 'index.html')
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)


def seo_head(soup):
    """Carry the original page's social, article, verification and structured-data tags verbatim."""
    out = []
    for m in soup.find_all('meta'):
        key = m.get('property') or m.get('name') or ''
        if key.startswith(('og:', 'twitter:', 'article:')) or key in ('google-site-verification', 'facebook-domain-verification'):
            attr = 'property' if m.get('property') else 'name'
            out.append(f'<meta {attr}="{esc(key)}" content="{esc(m.get("content", ""))}">')
    for l in soup.find_all('link', rel=True):
        if 'next' in l['rel'] or 'prev' in l['rel']:
            out.append(f'<link rel="{" ".join(l["rel"])}" href="{esc(l.get("href", ""))}">')
    for sc in soup.find_all('script', type='application/ld+json'):
        data = (sc.string or '').strip()
        if data:
            out.append('<script type="application/ld+json">' + data.replace('</', '<\\/') + '</script>')
    return ''.join(out)


def clean(main, u, unwrap=True):
    """Strip Carrot forms, scripts and layout wrappers; keep text, headings, links and images."""
    for e in main.select('script,style,iframe,form,noscript,svg,button,input,textarea,select,.gform_wrapper,.gform_confirmation_wrapper,#comments,.comments-area,.wp-block-spacer,.carrot-blocks-form,.sharedaddy'):
        e.decompose()
    for e in main.find_all(string=lambda t: isinstance(t, Comment)):
        e.extract()
    for e in main.find_all(True):
        e.attrs = {k: v for k, v in e.attrs.items() if k in ['href', 'src', 'alt', 'title', 'colspan', 'rowspan', 'id']}
        if e.name == 'h1':
            e.name = 'h2'
        if e.name == 'img':
            e['loading'] = 'lazy'
            e['decoding'] = 'async'
            if e.get('src'):
                e['src'] = urljoin(u, e['src'])
        if e.name == 'a':
            href = e.get('href', '')
            parsed = urlparse(urljoin(u, href))
            if parsed.netloc in ['www.homebuyerswi.com', 'homebuyerswi.com'] and not parsed.path.startswith('/wp-content/') and parsed.path in paths:
                e['href'] = link(parsed.path) + ('?' + parsed.query if parsed.query else '') + ('#' + parsed.fragment if parsed.fragment else '')
            if href.lower().startswith(('javascript:', 'data:')):
                e.attrs.pop('href', None)
    if unwrap:
        for e in reversed(main.find_all(['div', 'section', 'span'])):
            e.unwrap()
    return main


def tidy_content(main, heading):
    """Presentation-only structure: the page H1 lives in the hero, so drop an identical demoted copy,
    and lift a blog post's date and author into the hero. No other wording is removed."""
    meta = {}
    first = main.find(['h2'])
    header_el = main.find('header')
    if header_el is not None:
        t = header_el.find('time')
        if t:
            meta['date'] = norm(t.get_text())
        for p in header_el.find_all('p'):
            if norm(p.get_text()).startswith('By '):
                meta['author'] = p.decode_contents()
        h = header_el.find('h2')
        if h is not None and norm(h.get_text()).lower() == norm(heading).lower():
            header_el.decompose()
            first = None
    if first is not None and norm(first.get_text()).lower() == norm(heading).lower():
        first.decompose()
    for ul in main.find_all('ul'):
        hrefs = [a.get('href', '') for a in ul.find_all('a')]
        if hrefs and all(('sharer' in h or 'intent/tweet' in h or 'linkedin.com/share' in h) for h in hrefs):
            ul['class'] = 'share'
        elif hrefs and all('facebook.com/kustomproperty' in h for h in hrefs):
            ul['class'] = 'social'
    for f in main.find_all('footer'):
        f['class'] = 'prose-footer'
    return meta


def aside_card():
    return (f'<aside class="side"><div class="side-card"><p class="side-title">What’s going on with the house?</p>{chips("chips chips-side")}'
            f'<a class="side-call" href="{TEL}">{icon("phone")}<span><small>Rather talk it through?</small>{PHONE}</span></a></div>'
            f'<div class="side-trust">{g_badge()}<p>{icon("pin")}Local to Milwaukee &amp; southeastern Wisconsin</p></div></aside>')


def page_hero(heading, crumb, lede='', meta_html='', extra=''):
    return (f'<section class="page-hero"><div class="hero-glow g1"></div><div class="hero-dots"></div><div class="container">'
            f'<nav class="crumbs" aria-label="Breadcrumb"><a href="{link()}">Home</a><span>/</span>{crumb}</nav>'
            f'<h1>{esc(heading)}</h1>{lede}{meta_html}{extra}</div></section>')


# --------------------------------------------------------------------------------------------
# Read every downloaded page
# --------------------------------------------------------------------------------------------
manifest, failures, pages, raw = [], [], [], {}
for i, u in enumerate(urls):
    f = RAW / f'{i}.html'
    path = urlparse(u).path
    if not f.exists():
        failures.append({'url': u, 'reason': 'download missing'})
        continue
    soup = BeautifulSoup(f.read_text(errors='replace'), 'html.parser')
    main = soup.select_one('main')
    if main is None:
        failures.append({'url': u, 'reason': 'main content not found'})
        continue
    title = soup.title.get_text(' ', strip=True) if soup.title else path.strip('/').replace('-', ' ').title()
    desc = soup.select_one('meta[name="description"]')
    description = desc.get('content', '') if desc else ''
    h1 = main.find('h1') or soup.find('h1')
    heading = norm(h1.get_text(' ', strip=True)) if h1 else title.split('|')[0].strip()
    hero_lines = []
    hero_h1 = next((norm(h.get_text(' ', strip=True)) for h in soup.find_all('h1') if not h.find_parent('main')), '')
    hc = soup.select_one('.hero-content')
    if hc is not None and not main.find('h1'):
        for e in hc.find_all(['p', 'h2', 'h3']):
            t = norm(e.get_text(' ', strip=True))
            if t and not t.lower().startswith('fill out the short form'):
                hero_lines.append(t)
    raw[path] = {'url': u, 'soup': soup, 'seo': seo_head(soup)}
    home_main = copy.copy(main) if path == '/' else None
    clean(main, u)
    meta = tidy_content(main, heading)
    content = main.decode_contents()
    canonical = (soup.select_one('link[rel="canonical"]') or {}).get('href', u)
    manifest.append({'url': u, 'path': path, 'title': title, 'h1': heading, 'description': description, 'canonical': canonical,
                     'preview_url': 'https://andrewpcherry.github.io' + link(path), 'status': 'preserved path; v2 layout',
                     'source_text_chars': len(main.get_text(' ', strip=True))})
    pages.append({'path': path, 'title': title, 'heading': heading, 'description': description, 'content': content,
                  'meta': meta, 'hero_lines': hero_lines, 'hero_h1': hero_h1, 'home_main': home_main})

blogs = [p for p in pages if p['path'].startswith('/blog/') and p['path'] != '/blog/']
colors = ['violet', 'gold', 'crimson', 'brand-d', 'emerald', 'slate']

# --------------------------------------------------------------------------------------------
# Standard pages and articles
# --------------------------------------------------------------------------------------------
for idx, p in enumerate(pages):
    path = p['path']
    if path in ['/', '/blog/', '/get-a-cash-offer-today/', '/thank-you/']:
        continue
    is_blog = path.startswith('/blog/')
    label = p['hero_h1'] if p['hero_h1'] and p['hero_h1'].lower() != p['heading'].lower() else 'Kustom Property Solutions'
    crumb = f'<a href="{link("blog/")}">Seller resources</a>' if is_blog else f'<span>{esc(label)}</span>'
    meta_html = ''
    if p['meta']:
        bits = []
        if p['meta'].get('author'):
            bits.append(f'<span>{icon("user")}{p["meta"]["author"]}</span>')
        if p['meta'].get('date'):
            bits.append(f'<span>{icon("calendar")}{esc(p["meta"]["date"])}</span>')
        meta_html = '<div class="post-meta">' + ''.join(bits) + '</div>'
    lede = ''.join(f'<p class="page-lede">{esc(t)}</p>' for t in p['hero_lines'][1:] if norm(t).lower() != p['heading'].lower())
    related = ''
    if is_blog:
        bi = blogs.index(p)
        picks = [blogs[(bi + k) % len(blogs)] for k in (1, 2, 3)]
        related = ('<section class="section related"><div class="container"><div class="head"><p class="eyebrow">Keep reading</p><h2>More seller resources</h2></div><div class="resource-grid">'
                   + ''.join(f'<a class="resource-card" style="--c:var(--{colors[(bi + k) % 6]})" href="{link(r["path"])}"><i>{icon("book")}</i><h3>{esc(r["heading"])}</h3><p>{esc(r["description"][:150])}</p><span class="more">Read article {icon("arrow")}</span></a>'
                           for k, r in enumerate(picks)) + '</div></div></section>')
    side = '' if path == '/privacy/' else aside_card()
    body = (page_hero(p['heading'], crumb, lede, meta_html)
            + f'<div class="container article-grid{" no-side" if not side else ""}"><article class="prose">{p["content"]}</article>{side}</div>' + related)
    write(path, page(p['title'], body, path, p['description'], raw[path]['seo'], body_cls='inner'))

# --------------------------------------------------------------------------------------------
# Blog index
# --------------------------------------------------------------------------------------------
bp = next(p for p in pages if p['path'] == '/blog/')
blog_cards = ''.join(
    f'<a class="resource-card" style="--c:var(--{colors[k % 6]})" href="{link(r["path"])}"><i>{icon("book")}</i>'
    f'<span class="date">{esc(r["meta"].get("date", ""))}{" · " + esc(BeautifulSoup(r["meta"]["author"], "html.parser").get_text(" ", strip=True)) if r["meta"].get("author") else ""}</span><h2>{esc(r["heading"])}</h2><p>{esc(r["description"][:170])}</p><span class="more">Read article {icon("arrow")}</span></a>'
    for k, r in enumerate(blogs))
blog_body = (page_hero(bp['heading'], '<span>Seller resources</span>',
                       '<p class="page-lede big">A little clarity for your next move. Kustom’s articles on selling a house, inherited properties, repairs, foreclosure and life changes.</p>',
                       extra='<div class="search"><label class="sr" for="resource-search">Find a resource</label>' + icon('book') +
                             f'<input type="search" id="resource-search" placeholder="Search {len(blogs)} articles: try inherited, repairs, or Milwaukee"></div>')
             + f'<div class="container resource-grid library">{blog_cards}</div><p id="no-results" hidden class="container no-results">No matching articles. Try a different word.</p>')
write('blog/', page(bp['title'], blog_body, 'blog/', bp['description'], raw['/blog/']['seo'], body_cls='inner'))

# --------------------------------------------------------------------------------------------
# Thank-you (production wording kept; preview notice on top)
# --------------------------------------------------------------------------------------------
tp = next(p for p in pages if p['path'] == '/thank-you/')
notice = '<div class="preview-callout"><b>Website preview.</b> No inquiry has been sent. On the live site this page confirms a received inquiry.</div>'
write('thank-you/', page(tp['title'], page_hero(tp['heading'], '<span>Kustom Property Solutions</span>', extra=notice)
                         + f'<div class="container article-grid"><article class="prose">{tp["content"]}</article>{aside_card()}</div>',
                         'thank-you/', tp['description'], raw['/thank-you/']['seo'], body_cls='inner'))

# --------------------------------------------------------------------------------------------
# Assessment (the proven multi-situation funnel, isolated in an iframe) and its page
# --------------------------------------------------------------------------------------------
original = (ROOT / 'site-source/funnel-original.html').read_text()
style = re.search(r'<style>(.*?)</style>', original, re.S).group(1)
quiz = original[original.index('<section id="quiz">'):]
quiz = quiz[:quiz.index('</section>') + 10]
scripts = '\n'.join(re.findall(r'<script>(.*?)</script>', original, re.S))
scripts = scripts.replace('var ASSISTANT_ON = true', 'var ASSISTANT_ON = false').replace('const ASSISTANT_ON = true', 'const ASSISTANT_ON = false')
scripts = scripts.replace('https://www.homebuyerswi.com/privacy/', link('privacy/'))
scripts = re.sub(r'function doneHtml\(\)\{.*?\n\}', '''function doneHtml(){return '<div class="fade done"><div class="tick">✓</div><h3>You’ve reached the end of the preview.</h3><p>Your answers stayed in this browser. No inquiry was sent and no callback has been requested.</p><p>In the live site, this step will confirm that Kustom has actually received your inquiry.</p><a class="btn btn-line" href="../resource-page/" target="_top">Explore seller resources</a></div>';}''', scripts, flags=re.S)
scripts = scripts.replace('label="Sent"', 'label="Preview complete"')
scripts = scripts.replace('if(consent&&!consent.checked) problems.push("the tick box so we are allowed to contact you");', '')
scripts = scripts.replace('consent:{given:true,', 'consent:{given:!!(consent && consent.checked),')
scripts = scripts.replace('I agree to receive text messages', '(Optional) I agree to receive text messages')
scripts = scripts.replace('if(window.console) console.info("[lead payload]", lead);', '/* Preview only: no transmission, PII logging or conversion event. */')
scripts = re.sub(r'function getGuide\(e\)\{[^\n]+\}', 'function getGuide(e){ e.preventDefault(); top.location.href="../resource-page/"; return false; }', scripts)
scripts = scripts.replace('"Send Me The Guide":"Send This And Call Me Back"', '"Finish Preview":"Finish Preview"')
scripts = scripts.replace('No obligation. Not a listing agreement. Not a commitment to sell.', 'Preview only. Please use made-up contact details. No information is sent.')
quiz = quiz.replace('Most people are in more than one situation at once.', 'What’s happening with your house?')
quiz = re.sub(r'<p class="sec-p">.*?</p>', '<p class="sec-p">Choose everything that applies. We’ll ask a few relevant questions so the next conversation starts in the right place.</p><p class="preview-note">This is a demonstration. Please use made-up details. No inquiry will be sent.</p>', quiz, count=1, flags=re.S)
quiz_v2 = (ROOT / 'site-source/quiz-v2.css').read_text()
funnel_doc = ('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow">'
              '<title>Explore your selling options | Kustom</title>'
              f'<style>@font-face{{font-family:"Source Sans 3";src:url("{link("assets/source-sans.woff2")}") format("woff2");font-weight:200 900;font-display:swap}}'
              + style + '\n' + quiz_v2 + '</style></head><body>' + quiz + '<script>' + scripts + '</script>'
              '<script>new ResizeObserver(()=>{parent.postMessage({type:"kustom-height",height:document.body.scrollHeight},location.origin)}).observe(document.body);</script></body></html>')
write('assessment/', funnel_doc)

gp = next(p for p in pages if p['path'] == '/get-a-cash-offer-today/')
quiz_h1 = re.sub(r'\s+([!?.,])', r'\1', gp['heading'])
quiz_hero = (f'<section class="page-hero quiz-hero"><div class="hero-glow g1"></div><div class="hero-dots"></div><div class="container">'
             f'<nav class="crumbs" aria-label="Breadcrumb"><a href="{link()}">Home</a><span>/</span><span>Get a cash offer</span></nav>'
             f'<h1>{esc(quiz_h1)}</h1>'
             f'<div class="quiz-trust"><span>{icon("check")}About two minutes</span><span>{icon("check")}No obligation</span><a href="{TEL}">{icon("phone")}{PHONE}</a>{g_badge("dark")}</div></div></section>')
quiz_frame = (f'<section class="quiz-wrap" id="quiz"><div class="container"><div class="quiz-card"><iframe id="assessment-frame" title="Property situation assessment" src="{link("assessment/")}" loading="eager"></iframe></div></div></section>')
quiz_more = (f'<section class="section quiz-more"><div class="container article-grid no-side"><article class="prose">{gp["content"]}</article></div></section>')
frame_js = '<script>addEventListener("DOMContentLoaded",()=>{const f=document.getElementById("assessment-frame");f.src+="?"+new URLSearchParams(location.search).toString();addEventListener("message",e=>{if(e.origin===location.origin&&e.source===f.contentWindow&&e.data?.type==="kustom-height"&&Number.isFinite(e.data.height))f.style.height=Math.max(520,e.data.height+10)+"px";});});</script>'
write('get-a-cash-offer-today/', page(gp['title'], quiz_hero + quiz_frame + quiz_more, 'get-a-cash-offer-today/', gp['description'],
                                      raw['/get-a-cash-offer-today/']['seo'], extra=frame_js, body_cls='inner quiz-page', sticky=False))

# --------------------------------------------------------------------------------------------
# Homepage: v2 design built around the original homepage's headings and copy
# --------------------------------------------------------------------------------------------
hp = next(p for p in pages if p['path'] == '/')
hm = clean(hp['home_main'], urls[0], unwrap=False)


def el(prefix, name='p'):
    for e in hm.find_all(name):
        if norm(e.get_text(' ', strip=True)).startswith(prefix):
            return e
    raise SystemExit(f'Homepage fragment not found: {prefix}')


def inner(prefix, name='p'):
    return el(prefix, name).decode_contents()


def ul_after(prefix, name='p'):
    return el(prefix, name).find_next('ul').decode_contents()


def img(prefix_src):
    for e in hm.find_all('img'):
        if prefix_src in e.get('src', ''):
            return e
    raise SystemExit(f'Homepage image not found: {prefix_src}')


def img_tag(prefix_src, cls=''):
    e = img(prefix_src)
    return f'<img{" class=%s" % chr(34) + cls + chr(34) if cls else ""} src="{e["src"]}" alt="{esc(e.get("alt", ""))}" loading="lazy" decoding="async">'


area_p = ['Waukesha WI', 'New Berlin WI', 'Wauwatosa WI', 'Racine WI', 'Greenfield, WI']
reason_cols = [('Any Reason', 'violet', 'inherited'), ('Any Condition', 'gold', 'condition'), ('Any Challenge', 'crimson', 'deadline')]
why = [('No Repairs', 'gold', 'hammer'), ('No Agents', 'brand', 'user'), ('No Contracts', 'violet', 'doc'), ('No Worries', 'emerald', 'smile')]
community_imgs = ['humanity-first', '3B22959A', '224511A3', '353385A9', 'IMG_4899']
h1_text = hp['heading']

home = f'''
<section class="hero">
  <div class="hero-glow g1"></div><div class="hero-glow g2"></div><div class="hero-dots"></div>
  <div class="container hero-grid">
    <div class="hero-copy">
      <p class="pill"><span class="pulse"></span>Milwaukee &amp; southeastern Wisconsin · Local cash buyer</p>
      <h1><span class="h1-top">Sell your house fast</span> <span class="h1-bottom">in <span class="mark">Milwaukee, Wisconsin<svg viewBox="0 0 300 24" preserveAspectRatio="none" aria-hidden="true"><path d="M3 17C60 7 180 3 297 12"/></svg></span></span></h1>
      <ul class="hero-points"><li>{icon("check")}No fees</li><li>{icon("check")}No commissions</li><li>{icon("check")}You choose the closing date</li></ul>
      <p class="lede">Put more cash in your pocket. You’ll get a fair offer and we pay all costs. Tell us what’s going on and we’ll show you a straightforward way to sell as-is.</p>
      <div class="picker"><p class="picker-title">What’s going on with the house? <span>Pick one to start</span></p>{chips()}
        <p class="picker-foot">More than one fits? You can tell us about all of them. <a href="{TEL}">Or call {PHONE}</a></p></div>
    </div>
    <div class="hero-visual">
      <div class="arch-ring"></div>
      <figure class="arch"><img src="{link("assets/rizwan-ahmad.jpg")}" alt="Rizwan Ahmad, founder of Kustom Property Solutions, on the Milwaukee lakefront" width="900" height="1200" fetchpriority="high"></figure>
      <div class="float-card hello"><span class="avatar-dot"></span><div><small>Your local buyer</small><b>Hi, I’m Riz.</b></div></div>
      <blockquote class="float-card quote"><p>“Riz did everything he said he would do, when he said he would.”</p><footer>Jim A. · sold an inherited house</footer></blockquote>
      {g_badge("float-card rating")}
    </div>
  </div>
</section>

<section class="benefits"><div class="container"><ul class="benefit-card">
  <li style="--c:var(--gold)"><i>{icon("hammer")}</i><div><b>Sell as-is</b><span>Leave the repairs to us</span></div></li>
  <li style="--c:var(--brand)"><i>{icon("cash")}</i><div><b>A direct cash offer</b><span>No listing or showings</span></div></li>
  <li style="--c:var(--emerald)"><i>{icon("calendar")}</i><div><b>Your closing date</b><span>Tell us what works for you</span></div></li>
  <li style="--c:var(--violet)"><i>{icon("hand")}</i><div><b>Always your choice</b><span>No obligation to accept</span></div></li>
</ul></div></section>

<section class="section intro">
  <div class="container intro-grid">
    <div class="intro-copy reveal">
      <p class="eyebrow">We buy houses with cash</p>
      <h2>{inner("“I Need To Sell My House Fast", "h2")}</h2>
      <p class="big">{inner("We Buy Houses With Cash Anywhere")}</p>
      <p>{inner("Sell your Milwaukee house without hassle")}</p>
      <p>{inner("Stop the frustration of your unwanted property")}</p>
      <div class="callout" style="--c:var(--brand)"><h3>{inner("Cash For Homes Regardless Of The Situation", "h3")}</h3><p>{inner("Avoiding foreclosure")}</p></div>
    </div>
    <div class="intro-visual reveal">
      <figure class="tilt">{img_tag("HawleyRd")}</figure>
      <div class="intro-badge">{icon("pin")}<span><b>Milwaukee</b> and southeastern Wisconsin</span></div>
    </div>
  </div>
</section>

<section class="section situations">
  <div class="container">
    <div class="head reveal"><p class="eyebrow">Start with your situation</p><h2>There’s more to a house <br class="d">than its address.</h2>
      <p>Every situation asks different questions, so every one gets its own path. Choose what brought you here.</p></div>
    <div class="bento">''' + ''.join(
    f'<a class="tile{" wide" if k in ("inherited", "comparing") else ""}{" dark" if k == "comparing" else ""} reveal" style="--c:var(--{"brand-d" if c == "brand" else c});--s:var(--{"brand" if c == "brand" else c.replace("-l", "")}-soft)" href="{QUIZ}?s={k}#quiz"><span class="tag">{tag}</span><i>{icon(k)}</i><h3>{t}</h3><p>{d}</p><span class="start">{"Compare my options" if k == "comparing" else "Start here"} {icon("arrow")}</span></a>'
    for k, c, _, tag, t, d in SITUATIONS) + f'''</div>
  </div>
</section>

<section class="section mke">
  <div class="mke-glow"></div>
  <div class="container mke-grid">
    <div class="mke-copy reveal">
      <p class="eyebrow light">Why Milwaukee is different</p>
      <h2>{inner("We Are Your Local Milwaukee Market Experts", "h2")}</h2>
      <p>{inner("Milwaukee’s homes are notably old")}</p>
      <div class="stats">
        <div style="--c:var(--amber)"><b data-count="34.67" data-dec="2" data-suffix="%">34.67%</b><span>of Milwaukee homes were built before 1939</span></div>
        <div style="--c:#39C3F2"><b data-count="7.52" data-dec="2" data-suffix="%">7.52%</b><span>were built in 2000 or later</span></div>
        <div style="--c:#FF7A80"><b data-count="100000" data-dec="0" data-suffix="+">100,000+</b><span>Milwaukee homes contain lead-based paint</span></div>
      </div>
    </div>
    <div class="mke-visual reveal">
      <figure>{img_tag("IMG_2950")}</figure>
      <div class="grid-card"><div class="house-grid" data-grid aria-hidden="true"></div>
        <div class="legend"><span style="--c:var(--amber)">Built before 1939</span><span style="--c:#39C3F2">2000 or later</span><span style="--c:rgba(255,255,255,.28)">Everything in between</span></div>
        <small>Each square is about 1% of Milwaukee’s homes.</small></div>
    </div>
  </div>
  <div class="container problems reveal">
    <div class="problems-card"><p class="problems-title">{inner("Common Problems in Milwaukee Homes")}</p><p>{inner("Lead paint")}</p></div>
    <div class="problems-side"><p>{inner("If you need to sell your house, we’d like")}</p>
      <p class="areas-title">{icon("pin")}{inner("We also specialize in buying houses in")}</p>
      <div class="areas dark">''' + ''.join(f'<span>{inner(a)}</span>' for a in area_p) + f'''</div></div>
  </div>
</section>

<section class="section reasons">
  <div class="container">
    <div class="head center reveal"><p class="eyebrow">Any house. Any story.</p><h2>We buy houses for <span class="grad">any reason, any condition, any challenge.</span></h2></div>
    <div class="reason-grid">''' + ''.join(
    f'<div class="reason reveal" style="--c:var(--{c});--s:var(--{c}-soft)"><i>{icon(ic)}</i><h3>{inner(h, "h3")}</h3><ul class="checks">{ul_after(h, "h3")}</ul></div>'
    for h, c, ic in reason_cols) + f'''</div>
    <div class="reason-foot reveal"><p>{inner("We can close this week")}</p><p class="call-line">{inner("Give us a call at")}</p></div>
  </div>
</section>

<section class="section why">
  <div class="container">
    <div class="why-head reveal"><div><p class="eyebrow">A direct sale vs. a listing</p><h2>{inner("Why Choose Kustom Property Solutions", "h2")}</h2></div><p>{inner("We can buy your Milwaukee house with cash")}</p></div>
    <div class="why-grid">''' + ''.join(
    f'<div class="why-card reveal" style="--c:var(--{c})"><i>{icon(ic)}</i><h3>{inner(t)}</h3><p>{el(t).find_next("p").decode_contents()}</p></div>'
    for t, c, ic in why) + f'''</div>
    <div class="why-foot reveal"><p>{inner("Even if an agent can’t sell your house")}</p><p class="bonus">{inner("And as a bonus")}</p></div>
  </div>
</section>

<section class="section compare">
  <div class="container">
    <div class="head reveal"><p class="eyebrow">Side by side</p><h2>{inner("What Are The Benefits Of Selling My House For Cash", "h2")}</h2><p>{inner("Kustom Property Solutions provides the fastest option")}</p></div>
    <div class="compare-grid">
      <div class="compare-card cash reveal"><span class="ribbon">Kustom</span><i>{icon("cash")}</i><h3>{inner("Sell With Our Cash Offer Program")}</h3><p class="sub">{inner("Sell your house to Kustom Property Solutions")}</p><p>{inner("Get a fair cash offer so you can sell")}</p><ul class="checks">{ul_after("Get a fair cash offer so you can sell")}</ul></div>
      <div class="compare-card trad reveal"><i>{icon("calendar")}</i><h3>{inner("Sell The Traditional Way")}</h3><p class="sub">{inner("Listing your house with an agent")}</p><p>{inner("The time, money, and stress of listing")}</p><ul class="crosses">{ul_after("The time, money, and stress of listing")}</ul></div>
    </div>
  </div>
</section>

<section class="section process">
  <div class="container">
    <div class="head center reveal"><p class="eyebrow">A simpler way to sell</p><h2>Three steps. <span class="grad">Room to breathe.</span></h2><p>No fixing up for photos. No weekend showings. Just a conversation about the property and a plan that fits.</p></div>
    <ol class="timeline reveal">
      <li style="--c:var(--brand)"><span class="num">1</span><h3>Tell us about the house</h3><p>Share the condition, your timeline, and what you’d like to happen next. It takes a few minutes.</p></li>
      <li style="--c:var(--violet)"><span class="num">2</span><h3>Review a cash offer</h3><p>We’ll talk through the details and arrange a property visit. You decide whether the offer works for you.</p></li>
      <li style="--c:var(--act)"><span class="num">3</span><h3>Close and move forward</h3><p>Choose an agreed closing date. Sell as-is, without agent commissions or making repairs first.</p></li>
    </ol>
    <div class="differently reveal">
      <figure>{img_tag("milwaukee-1826837")}</figure>
      <div><h3>{inner("We work differently at Kustom Property Solutions")}</h3><p>{inner("We’ll know very quickly if we can help you")}</p><p>{inner("All that hassle can add stress")}</p><p>{inner("When you contact us and submit")}</p></div>
    </div>
  </div>
</section>

<section class="section riz" id="riz">
  <div class="container riz-grid">
    <div class="riz-visual reveal"><div class="blob"></div>
      <figure class="lake"><img src="{link("assets/milwaukee-lakefront.jpg")}" alt="Milwaukee lakefront" width="1024" height="683" loading="lazy"></figure>
      <div class="riz-badge">{img_tag("Rizwan-Ahmad-768x1024")}<div><b>Rizwan Ahmad</b><span>Founder, Kustom Property Solutions</span></div></div></div>
    <div class="riz-copy reveal">
      <p class="eyebrow">Meet your local buyer</p>
      <h2>It starts with a conversation. <em>With Riz.</em></h2>
      <p class="kicker">{inner("Get to Know Kustom Property Solutions")}</p>
      <p>{inner("Kustom Property Solutions is a professional, full-service")}</p>
      <p class="areas-title">{icon("pin")}We buy houses throughout southeastern Wisconsin</p>
      <div class="areas">''' + ''.join(f'<a href="{link(p)}">{n}</a>' for n, p in AREAS) + f'''</div>
      <a class="text-link" href="{link("our-company/")}">Get to know Kustom {icon("arrow")}</a>
    </div>
  </div>
</section>

<section class="section community">
  <div class="container">
    <div class="head center reveal"><p class="eyebrow">Close to home</p><h2 class="h2-like">{inner("We at Kustom Property Solutions Care About Our Milwaukee Community")}</h2></div>
    <div class="community-grid reveal">''' + ''.join(f'<figure class="c{k}">{img_tag(s)}</figure>' for k, s in enumerate(community_imgs)) + f'''</div>
  </div>
</section>

<section class="section stories" id="stories">
  <div class="container">
    <div class="head stories-head reveal"><div><p class="eyebrow">Seller stories</p><h2>People who were where <br class="d">you are now.</h2><p>In their own words, from Kustom’s testimonials page.</p></div>{g_badge("big")}</div>
    <div class="story-grid">
      <figure class="story feature reveal" style="--c:var(--violet)"><span class="tag">Inherited · sold as-is</span>
        <blockquote>“When my sister died in Milwaukee, leaving a rundown house to me, I knew I needed to sell the house as is. I had nine different buyers look at the home. <mark>Riz was very professional and kind.</mark> We closed quickly and without any complications or drama.”</blockquote>
        <figcaption><span class="initial" data-i="J" aria-hidden="true"></span><b>Jim A.</b><small>Minneapolis, MN</small></figcaption></figure>
      <figure class="story reveal" style="--c:var(--emerald)"><span class="tag">Out of state · under 30 days</span>
        <blockquote>“I knew my Dad’s home would not make it through financing in ‘as is’ condition… <mark>We also closed in less than 30 days</mark>, which eliminated a huge burden from my mind.”</blockquote>
        <figcaption><span class="initial" data-i="B" aria-hidden="true"></span><b>Bob B.</b></figcaption></figure>
      <figure class="story reveal" style="--c:var(--gold)"><span class="tag">A parent’s house</span>
        <blockquote>“We tried for months to clear out and fix up her house to get ready to sell… <mark>We were able to just take the items we wanted and he took care of the rest.</mark>”</blockquote>
        <figcaption><span class="initial" data-i="S" aria-hidden="true"></span><b>Susan J.</b><small>Hales Corners, WI</small></figcaption></figure>
      <figure class="story reveal" style="--c:var(--brand)"><span class="tag">A flexible closing</span>
        <blockquote>“I had many questions about how the process worked and you took the time to help me understand. <mark>You were able to accommodate moving the closing up a couple days</mark> so we didn’t have to make a second trip to town.”</blockquote>
        <figcaption><span class="initial" data-i="G" aria-hidden="true"></span><b>Gail R.</b></figcaption></figure>
    </div>
    <a class="text-link reveal" href="{link("testimonials/")}">Read all seller stories {icon("arrow")}</a>
  </div>
</section>

<section class="section longform">
  <div class="container longform-grid">
    <div class="longform-copy reveal">
      <p class="eyebrow">{inner("In short")}</p>
      <p class="big">{inner("No matter what condition your house is in")}</p>
      <p>{inner("Our goal is to help make your life easier")}</p>
      <p class="call-line">{inner("Or Give Us A Call Now At")}</p>
      <h4>{inner("We Pay Cash For Real Estate Properties", "h4")}</h4>
      <p>{inner("We help property owners just like you")}</p>
      <p>{inner("If you simply don’t want to put up with the hassle")}</p>
      <p>{inner("We buy houses in Milwaukee, Wisconsin and surrounding areas")}</p>
    </div>
    <figure class="longform-img reveal">{img_tag("IMG_2870")}</figure>
  </div>
</section>

<section class="section faqs" id="faq">
  <div class="container faq-grid">
    <div class="head reveal"><p class="eyebrow">Good questions. Straight answers.</p><h2>Before you take the next step.</h2><a class="text-link" href="{link("faq/")}">All frequently asked questions {icon("arrow")}</a></div>
    <div class="faq-list reveal">
      <details style="--c:var(--gold)"><summary>Do I need to repair or clean out the house?</summary><p>We buy houses as-is. Tell us about the condition and anything you’d prefer to leave behind so we can discuss it with you.</p></details>
      <details style="--c:var(--violet)"><summary>Is there any obligation to accept an offer?</summary><p>No. Sharing your situation or reviewing an offer does not commit you to selling.</p></details>
      <details style="--c:var(--emerald)"><summary>How quickly could we close?</summary><p>Kustom’s existing offer is a closing in as little as seven days, where the property, title work and agreed terms allow. A later date can work too. We’ll discuss a realistic timeline for your situation.</p></details>
      <details style="--c:var(--brand)"><summary>Would I get more by listing with an agent?</summary><p>A listing may produce a higher sale price. A direct sale can avoid agent commissions, repairs and showings. Compare the likely net proceeds, timing and work involved before deciding.</p></details>
    </div>
  </div>
</section>'''
write('', page(hp['title'], home, '', hp['description'], raw['/']['seo'], body_cls='home'))

# The design review path now points at the live homepage.
(ROOT / 'v2').mkdir(exist_ok=True)
(ROOT / 'v2/index.html').write_text(f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="robots" content="noindex,nofollow"><meta http-equiv="refresh" content="0;url={link()}"><title>Moved</title></head><body><a href="{link()}">Kustom Property Solutions</a></body></html>')
for old in ['v2/v2.css', 'v2/v2.js']:
    if (ROOT / old).exists():
        (ROOT / old).unlink()

(ROOT / 'migration/url-inventory.json').write_text(json.dumps(manifest, indent=2, ensure_ascii=False))
(ROOT / 'migration/import-failures.json').write_text(json.dumps(failures, indent=2))
(ROOT / 'migration/source-content.json').write_text(json.dumps([{k: v for k, v in p.items() if k in ('path', 'title', 'heading', 'description', 'content')} for p in pages], indent=2, ensure_ascii=False))
with (ROOT / 'migration/url-map.csv').open('w') as f:
    w = csv.writer(f)
    w.writerow(['Existing URL', 'Planned production URL', 'Preview URL', 'Action'])
    w.writerows((m['url'], m['url'], m['preview_url'], 'Keep existing path') for m in manifest)
# Production sitemap, ready for launch day. Not referenced by the noindex preview.
(ROOT / 'migration/sitemap-production.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                                                       + ''.join(f'  <url><loc>{esc(m["url"])}</loc></url>\n' for m in manifest) + '</urlset>\n')
(ROOT / '.nojekyll').touch()
(ROOT / 'robots.txt').write_text('User-agent: *\nAllow: /\n# Every preview page has a noindex,nofollow meta directive.\n')
print(f'Built {len(manifest)} preserved routes, {len(blogs)} blog articles, homepage and integrated assessment. Import failures: {len(failures)}')
