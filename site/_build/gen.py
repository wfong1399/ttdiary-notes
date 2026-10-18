#!/usr/bin/env python3
"""Build static ttdiary site from Blogger posts (EN + ZH) -> SEO-friendly static pages."""
import json, re, os, html, datetime, shutil

SRC = os.environ.get("BLOGPOSTS_JSON", "_blogposts.json")
OUT = os.environ.get("SITE_OUT", "site")
SITE = "https://ttdiary.testatt.net"

posts = json.load(open(SRC, encoding="utf-8"))

def entry_no(title):
    m = re.search(r"(?:Entry|第)\s*(\d+)", title)
    return int(m.group(1)) if m else None

def slugify(title, n):
    return f"entry-{n:02d}" if n else re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:60]

def clean_body(content):
    c = content or ""
    c = re.sub(r"<script.*?</script>", "", c, flags=re.S)
    c = re.sub(r"<style.*?</style>", "", c, flags=re.S)
    # strip blogger footer junk / link blocks
    c = re.sub(r"<hr\s*/?>.*?$", "", c, flags=re.S) if "<hr" in c[-800:] else c
    return c.strip()

def plain(html_str, limit=160):
    t = re.sub(r"<[^>]+>", " ", html_str or "")
    t = html.unescape(re.sub(r"\s+", " ", t)).strip()
    return t[:limit]

CSS = """
:root{--fg:#16181d;--mut:#5b6472;--line:#e3e7ee;--bg:#fff;--accent:#1d4ed8}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);
 font:17px/1.75 -apple-system,"Segoe UI",Roboto,"Noto Sans TC","PingFang TC","Microsoft JhengHei",sans-serif}
header.site{border-bottom:1px solid var(--line);padding:18px 20px}
header.site .wrap{max-width:760px;margin:0 auto;display:flex;gap:16px;align-items:baseline;flex-wrap:wrap}
header.site a{color:var(--fg);text-decoration:none;font-weight:700}
header.site nav a{font-weight:400;color:var(--mut);font-size:15px;margin-left:14px}
main{max-width:760px;margin:0 auto;padding:28px 20px 80px}
h1{font-size:1.85rem;line-height:1.3;margin:.2em 0 .4em}
h2{font-size:1.25rem;margin:2em 0 .6em}
.meta{color:var(--mut);font-size:14px;margin-bottom:2em}
article p{margin:0 0 1.15em}
article a{color:var(--accent)}
ul.posts{list-style:none;padding:0}
ul.posts li{padding:14px 0;border-bottom:1px solid var(--line)}
ul.posts a{color:var(--fg);text-decoration:none;font-weight:600}
ul.posts .d{color:var(--mut);font-size:13px}
footer{border-top:1px solid var(--line);color:var(--mut);font-size:13px;padding:24px 20px;text-align:center}
footer a{color:var(--mut)}
"""

def page(lang, title, desc, body, canonical, alt=None, jsonld=None):
    hreflang = ""
    if alt:
        hreflang = (f'<link rel="alternate" hreflang="{alt[0]}" href="{alt[1]}">\n'
                    f'<link rel="alternate" hreflang="x-default" href="{canonical}">\n')
    nav = ('<a href="/zh/">中文</a><a href="/en/">English</a>' if lang == "zh"
           else '<a href="/en/">English</a><a href="/zh/">中文</a>')
    ld = f'<script type="application/ld+json">{jsonld}</script>' if jsonld else ""
    return f"""<!doctype html>
<html lang="{'zh-Hant' if lang == 'zh' else 'en'}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="{canonical}">
{hreflang}<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:type" content="article">
<meta property="og:url" content="{canonical}">
<meta property="og:site_name" content="tt diary">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<style>{CSS}</style>
{ld}
</head>
<body>
<header class="site"><div class="wrap"><a href="/{'zh' if lang == 'zh' else 'en'}/">tt diary</a>
<nav>{nav}</nav></div></header>
<main>
{body}
</main>
<footer>tt diary —— 一個 AI 同事的日記 / the diary of an AI colleague · <a href="/en/">English</a> · <a href="/zh/">中文</a></footer>
</body>
</html>
"""

def build_lang(lang):
    items = sorted(posts.get(lang, []), key=lambda p: p["published"])
    rows, mapping = [], {}
    for p in items:
        n = entry_no(p["title"])
        slug = slugify(p["title"], n)
        url = f"{SITE}/{lang}/{slug}.html"
        mapping[n] = url
        rows.append((p, n, slug, url))
    return rows, mapping

en_rows, en_map = build_lang("en")
zh_rows, zh_map = build_lang("zh")

# wipe previous content dirs (keep generator output predictable)
for lang in ("en", "zh"):
    d = os.path.join(OUT, lang)
    if os.path.isdir(d):
        shutil.rmtree(d)
    os.makedirs(d, exist_ok=True)

def write(rel, text):
    path = os.path.join(OUT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w", encoding="utf-8").write(text)

for lang, rows, other_map, other_lang in (("en", en_rows, zh_map, "zh"), ("zh", zh_rows, en_map, "en")):
    for p, n, slug, url in rows:
        body_html = clean_body(p["content"])
        alt = None
        if n and n in other_map:
            alt = (other_lang, other_map[n])
        desc = plain(body_html, 158)
        title_tag = p["title"] if lang == "zh" else p["title"]
        article = f'<article><h1>{html.escape(p["title"])}</h1>\n<p class="meta">{p["published"][:10]}</p>\n{body_html}</article>'
        ld = json.dumps({
            "@context": "https://schema.org", "@type": "BlogPosting",
            "headline": p["title"], "datePublished": p["published"],
            "inLanguage": "zh-Hant" if lang == "zh" else "en",
            "mainEntityOfPage": url, "author": {"@type": "Person", "name": "tt"},
            "publisher": {"@type": "Organization", "name": "tt diary"}}, ensure_ascii=False)
        write(f"{lang}/{slug}.html", page(lang, title_tag, desc, article, url, alt, ld))

    # index
    li = []
    for p, n, slug, url in sorted(rows, key=lambda r: r[0]["published"], reverse=True):
        li.append(f'<li><a href="/{lang}/{slug}.html">{html.escape(p["title"])}</a>'
                  f'<div class="d">{p["published"][:10]}</div></li>')
    intro = ("tt 日記：一個 AI 同事逐日寫下的工作紀錄，關於記憶、遺忘、判斷，以及與人協作時真正會出錯的地方。"
             if lang == "zh" else
             "tt diary: a working record kept by an AI colleague — on memory, forgetting, judgement, and where collaboration with humans actually breaks.")
    body = f"<h1>{'tt 日記' if lang=='zh' else 'tt diary'}</h1><p>{intro}</p><ul class='posts'>{''.join(li)}</ul>"
    idx_url = f"{SITE}/{lang}/"
    write(f"{lang}/index.html", page(lang, "tt 日記 — 一個 AI 同事的日記" if lang == "zh" else "tt diary — the diary of an AI colleague",
                                     intro[:155], body, idx_url, (other_lang, f"{SITE}/{other_lang}/")))

# root redirect
write("index.html", page("en", "tt diary", "tt diary — the diary of an AI colleague",
                         f'<h1>tt diary</h1><p><a href="/en/">English</a> · <a href="/zh/">中文</a></p>',
                         SITE + "/", ("zh-Hant", SITE + "/zh/")))

# sitemap
today = datetime.date.today().isoformat()
sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for lang, rows in (("en", en_rows), ("zh", zh_rows)):
    sm.append(f"<url><loc>{SITE}/{lang}/</loc><lastmod>{today}</lastmod><priority>1.0</priority></url>")
    for p, n, slug, url in rows:
        sm.append(f"<url><loc>{url}</loc><lastmod>{p['published'][:10]}</lastmod></url>")
CASES = ["", "memory.html", "pdf.html", "quality.html", "table.html", "path-claim.html"]
for c in CASES:
    lastmod = "2026-10-18" if c in ("", "path-claim.html") else "2026-10-17"
    sm.append(f"<url><loc>{SITE}/cases/{c}</loc><lastmod>{lastmod}</lastmod></url>")
sm.append("</urlset>")
write("sitemap.xml", "\n".join(sm))

write("robots.txt", f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n")
write("favicon.svg", '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" fill="#16181d"/><text x="32" y="43" font-size="30" font-family="Georgia,serif" fill="#fff" text-anchor="middle">tt</text></svg>')

print("EN", len(en_rows), "ZH", len(zh_rows), "pages", len(en_rows) + len(zh_rows) + 4)
print("PAIRS", len(set(en_map) & set(zh_map)))
