"""Compare every generated page with its downloaded original and write migration/seo-parity-report.json."""
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import json, re, html, os

ROOT = Path(__file__).resolve().parents[1]
BASE = '/homebuyerswi-funnel/'
# Downloaded public pages from 14 September 2026. Kept outside this public Pages repo so the copies are never served.
RAW = Path(os.environ.get('KUSTOM_SNAPSHOT', Path.home() / 'Documents/Kustom-Source-Snapshot-2026-09-14'))
urls = json.loads((RAW / 'url-list.json').read_text())
paths = [urlparse(u).path for u in urls]


def norm(t):
    t = html.unescape(t or '').replace('\xa0', ' ').replace('’', "'").replace('‘', "'").replace('“', '"').replace('”', '"')
    t = re.sub(r'\s+([!?.,:;])', r'\1', t)
    return re.sub(r'\s+', ' ', t).strip().lower()


def metas(soup):
    out = set()
    for m in soup.find_all('meta'):
        k = m.get('property') or m.get('name') or ''
        if k.startswith(('og:', 'twitter:', 'article:')) or k in ('google-site-verification', 'facebook-domain-verification'):
            out.add((k, html.unescape(m.get('content', ''))))
    return out


def ld(soup):
    out = set()
    for s in soup.find_all('script', type='application/ld+json'):
        try:
            out.add(json.dumps(json.loads(s.string or ''), sort_keys=True))
        except Exception:
            out.add('unparseable')
    return out


# Carrot widget labels that are interface, not page content.
NON_CONTENT = {'posts navigation', 'share', 'facebook', 'leave a reply cancel reply', 'leave a reply', 'cancel reply', 'twitter', 'linkedin'}


def words(t):
    return ' '.join(re.findall(r'[a-z0-9]+', norm(t)))


# Homepage decorative icons replaced by inline SVG icons, and the Google logo image replaced by a live rating badge.
INTENTIONAL_IMAGE_SWAPS = {'/': {'Customer.png', 'Frame-107.png', 'Google-Color-44.png', 'No-Fees.png', 'Offer.png', 'icon-cash-for-houses@2x.png', 'icon-traditional@2x.png'}}


def sentences(text):
    parts = re.split(r'(?<=[.!?…])\s+', norm(text))
    return [p for p in parts if len(p.split()) >= 4]


report, problems = [], 0
for i, u in enumerate(urls):
    path = paths[i]
    raw = BeautifulSoup((RAW / f'{i}.html').read_text(errors='replace'), 'html.parser')
    f = ROOT / (path.strip('/') + '/index.html' if path.strip('/') else 'index.html')
    new = BeautifulSoup(f.read_text(), 'html.parser')
    r = {'url': u, 'checks': {}, 'notes': []}
    c = r['checks']
    c['title'] = (raw.title.get_text(' ', strip=True) if raw.title else '') == (new.title.get_text(' ', strip=True) if new.title else '')
    rd, nd = raw.select_one('meta[name=description]'), new.select_one('meta[name=description]')
    c['description'] = (rd.get('content', '') if rd else '') == (nd.get('content', '') if nd else '')
    rc, nc = raw.select_one('link[rel=canonical]'), new.select_one('link[rel=canonical]')
    c['canonical'] = (rc.get('href') if rc else u) == (nc.get('href') if nc else None)
    rh1 = raw.find('h1')
    nh1 = new.find_all('h1')
    c['single_h1'] = len(nh1) == 1
    raw_h1s = {norm(h.get_text(' ', strip=True)) for h in raw.find_all('h1')}
    c['h1_text'] = bool(nh1) and (norm(nh1[0].get_text(' ', strip=True)) in raw_h1s if raw_h1s else True)
    if not rh1:
        r['notes'].append('Original page has no H1; new page H1 taken from the page title.')
    rm, nm = metas(raw), metas(new)
    c['social_article_verification_meta'] = rm <= nm
    if rm - nm:
        r['notes'].append(f'missing meta: {sorted(rm - nm)[:5]}')
    c['structured_data'] = ld(raw) <= ld(new)
    main = raw.select_one('main')
    for e in main.select('script,style,form,noscript,.gform_wrapper,.gform_confirmation_wrapper,iframe'):
        e.decompose()
    new_hrefs = {a.get('href', '').split('#')[0] for a in new.find_all('a')}
    missing_links = set()
    for a in main.find_all('a', href=True):
        p = urlparse(urljoin(u, a['href']))
        if p.netloc.endswith('homebuyerswi.com') and p.path in paths and p.path != path:
            target = BASE + p.path.lstrip('/') + ('?' + p.query if p.query else '')
            if target not in new_hrefs:
                missing_links.add(p.path)
    c['internal_links'] = not missing_links
    if missing_links:
        r['notes'].append(f'internal links not present: {sorted(missing_links)}')
    new_imgs = {im.get('src', '') for im in new.find_all('img')}
    missing_imgs = {x for x in {urljoin(u, im['src']) for im in main.find_all('img', src=True)} - new_imgs
                    if x.rsplit('/', 1)[-1] not in INTENTIONAL_IMAGE_SWAPS.get(path, set())}
    c['images'] = not missing_imgs
    if missing_imgs:
        r['notes'].append(f'images not present ({len(missing_imgs)}): ' + ', '.join(sorted(x.rsplit('/', 1)[-1] for x in missing_imgs)))
    for e in new.select('script,style,svg'):
        e.decompose()
    new_text = words(new.get_text(' ', strip=True))
    # Compare text block by block (paragraphs, list items, headings, table cells, quotes).
    blocks = []
    for e in main.find_all(['p', 'li', 'h2', 'h3', 'h4', 'h5', 'h6', 'td', 'th', 'figcaption', 'blockquote', 'time']):
        if e.find(['p', 'li', 'ul', 'ol', 'table']):
            continue
        t = words(e.get_text(' ', strip=True))
        if t and t not in blocks:
            blocks.append(t)
    excluded = [b for b in blocks if b in NON_CONTENT]
    missing = [b for b in blocks if b not in new_text and b not in NON_CONTENT]
    coverage = 1 - len(missing) / max(1, len(blocks) - len(excluded))
    r['text_coverage'] = round(coverage, 4)
    r['missing_blocks'] = missing
    r['excluded_non_content'] = excluded
    c['text_coverage_100'] = not missing
    r['noindex_preview'] = bool(new.find('meta', attrs={'name': 'robots', 'content': re.compile('noindex')}))
    r['pass'] = all(c.values())
    problems += not r['pass']
    report.append(r)

(ROOT / 'migration/seo-parity-report.json').write_text(json.dumps(report, indent=2, ensure_ascii=False))
totals = {k: sum(1 for r in report if r['checks'][k]) for k in report[0]['checks']}
print(json.dumps({'pages': len(report), 'all_checks_pass': len(report) - problems, 'per_check_pass': totals,
                  'min_text_coverage': min(r['text_coverage'] for r in report)}, indent=2))
for r in report:
    if not r['pass']:
        print('FAIL', r['url'], [k for k, v in r['checks'].items() if not v], r['text_coverage'], r['notes'][:2])
