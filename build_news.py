#!/usr/bin/env python3
"""Build the Guttmann Lab news pages from news-posts.json.

Reads news-posts.json (list of posts, newest anywhere in the list) and writes, into the
output directory (default: current directory):
  news.html                  the news index
  news-<slug>.html           one page per post
  feed.xml                   Atom/RSS style feed (RSS 2.0)
  sitemap.xml                home page, CV, news index, and every post

Post fields: slug, title, date (YYYY-MM-DD), category, summary (plain text, one or two
sentences), keywords (list), body_html (paragraphs, h2, ul, a tags only), sources (optional
list of {"title","url"}).
"""
import json, sys, html, os
from datetime import datetime

SITE = "https://guttmannlab.org"
OUT = sys.argv[2] if len(sys.argv) > 2 else "."
SRC = sys.argv[1] if len(sys.argv) > 1 else "news-posts.json"
GA = "G-XFWF5H8X3L"
ORCID = "https://orcid.org/0000-0001-5553-3099"
SCHOLAR = "https://scholar.google.com/citations?user=3hWVD18AAAAJ"
e = html.escape

posts = json.load(open(SRC, encoding="utf-8"))
posts.sort(key=lambda p: p["date"], reverse=True)


def pretty(d):
    return datetime.strptime(d, "%Y-%m-%d").strftime("%B %-d, %Y")


def rfc822(d):
    return datetime.strptime(d, "%Y-%m-%d").strftime("%a, %d %b %Y 12:00:00 GMT")


CSS = """
:root{--blue:#004C97;--green:#007A33;--gold:#FFB81C;--ink:#1f2933;--muted:#5b6770}
*{box-sizing:border-box}
body{margin:0;font-family:system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif;color:var(--ink);line-height:1.65;background:#f6f8fb}
a{color:var(--blue)}
.skip{position:absolute;left:-999px}.skip:focus{left:8px;top:8px;background:#fff;padding:8px;z-index:9}
header.site{background:var(--blue);color:#fff;padding:18px 20px}
header.site .in{max-width:880px;margin:0 auto;display:flex;flex-wrap:wrap;gap:12px 28px;align-items:center;justify-content:space-between}
header.site a{color:#fff;text-decoration:none}
header.site .brand{font-weight:700;font-size:1.25rem}
header.site nav a{margin-right:18px;font-size:.98rem;text-decoration:underline;text-underline-offset:3px}
main{max-width:880px;margin:0 auto;padding:30px 20px 50px}
h1{color:var(--blue);line-height:1.2;margin:.2em 0 .3em;font-size:2rem}
h2{color:var(--blue);margin-top:1.8em;font-size:1.35rem}
.meta{color:var(--muted);font-size:.95rem;margin-bottom:1.4em}
.tag{display:inline-block;background:#e6eef7;color:var(--blue);border-radius:999px;padding:2px 12px;font-size:.85rem;margin-right:8px}
article.card{background:#fff;border:1px solid #dde5ee;border-left:6px solid var(--green);border-radius:10px;padding:20px 24px;margin:0 0 20px}
article.card h2{margin:.2em 0 .3em;font-size:1.3rem}
article.card h2 a{text-decoration:none}
article.card p{margin:.4em 0}
.post{background:#fff;border:1px solid #dde5ee;border-radius:12px;padding:10px 32px 28px}
.post p,.post li{font-size:1.06rem}
.sources{border-top:1px solid #dde5ee;margin-top:2em;padding-top:1em;font-size:.95rem}
.back{display:inline-block;margin-top:24px}
footer.site{background:#1a1a2e;color:#adb5bd;padding:28px 20px;font-size:.95rem}
footer.site .in{max-width:880px;margin:0 auto}
footer.site a{color:#cdd6df}
@media(max-width:600px){.post{padding:6px 18px 22px}h1{font-size:1.65rem}}
"""


def head(title, desc, path, kind="website", extra_ld="", date=None):
    url = SITE + "/" + path
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<meta name="author" content="Dr. Rodney Guttmann">
<meta name="robots" content="index, follow, max-image-preview:large">
<link rel="canonical" href="{url}">
<link rel="alternate" type="application/rss+xml" title="Guttmann Research Lab News" href="{SITE}/feed.xml">
<meta property="og:type" content="{kind}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE}/lab-logo.png">
<meta property="og:site_name" content="Guttmann Research Lab">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{e(title)}">
<meta name="twitter:description" content="{e(desc)}">
<meta name="twitter:image" content="{SITE}/lab-logo.png">
{extra_ld}
<script async src="https://www.googletagmanager.com/gtag/js?id={GA}"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('js',new Date());gtag('config','{GA}');</script>
<style>{CSS}</style>
</head>
<body>
<a class="skip" href="#main">Skip to main content</a>
<header class="site"><div class="in">
<a class="brand" href="{SITE}/">Guttmann Research Lab</a>
<nav aria-label="Main"><a href="{SITE}/">Lab home</a><a href="{SITE}/news.html">News</a><a href="{SITE}/guttmann-cv.pdf">CV (PDF)</a></nav>
</div></header>
<main id="main">
"""


FOOT = f"""</main>
<footer class="site"><div class="in">
<p>Guttmann Research Lab, Department of Biology, University of West Florida.
<a href="{SITE}/">guttmannlab.org</a> | <a href="{ORCID}">ORCID</a> | <a href="{SCHOLAR}">Google Scholar</a> | <a href="{SITE}/feed.xml">News feed</a></p>
</div></footer>
</body>
</html>
"""


def post_page(p):
    path = f"news-{p['slug']}.html"
    ld = {
        "@context": "https://schema.org",
        "@type": "BlogPosting",
        "headline": p["title"],
        "description": p["summary"],
        "datePublished": p["date"],
        "dateModified": p.get("modified", p["date"]),
        "mainEntityOfPage": f"{SITE}/{path}",
        "image": f"{SITE}/lab-logo.png",
        "keywords": ", ".join(p.get("keywords", [])),
        "author": {"@type": "Person", "name": "Rodney Guttmann", "url": SITE + "/",
                   "sameAs": [ORCID, SCHOLAR]},
        "publisher": {"@type": "Organization", "name": "Guttmann Research Lab",
                      "url": SITE + "/", "logo": {"@type": "ImageObject", "url": f"{SITE}/lab-logo.png"}},
    }
    ld_tag = '<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False) + "</script>"
    src = ""
    if p.get("sources"):
        items = "".join(f'<li><a href="{e(s["url"])}">{e(s["title"])}</a></li>' for s in p["sources"])
        src = f'<div class="sources"><strong>Sources</strong><ul>{items}</ul></div>'
    body = f"""<article class="post">
<h1>{e(p["title"])}</h1>
<p class="meta"><span class="tag">{e(p["category"])}</span><time datetime="{p["date"]}">{pretty(p["date"])}</time> by Rodney Guttmann</p>
{p["body_html"]}
{src}
</article>
<a class="back" href="{SITE}/news.html">&larr; All news</a>
"""
    return path, head(p["title"] + " | Guttmann Research Lab", p["summary"], path, "article", ld_tag) + body + FOOT


def index_page():
    ld = {"@context": "https://schema.org", "@type": "Blog", "name": "Guttmann Research Lab News",
          "url": f"{SITE}/news.html", "publisher": {"@type": "Organization", "name": "Guttmann Research Lab"},
          "blogPost": [{"@type": "BlogPosting", "headline": p["title"], "datePublished": p["date"],
                        "url": f"{SITE}/news-{p['slug']}.html"} for p in posts]}
    ld_tag = '<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False) + "</script>"
    cards = ""
    for p in posts:
        cards += f"""<article class="card">
<p class="meta"><span class="tag">{e(p["category"])}</span><time datetime="{p["date"]}">{pretty(p["date"])}</time></p>
<h2><a href="{SITE}/news-{p['slug']}.html">{e(p["title"])}</a></h2>
<p>{e(p["summary"])}</p>
</article>
"""
    desc = "News, research explainers and program updates from the Guttmann Research Lab at the University of West Florida: Alzheimer's disease research, undergraduate research, and the NeuroNauts Scholars Program."
    body = f"""<h1>Lab news and research updates</h1>
<p class="meta">Plain language research explainers, caregiver resources and program updates from the Guttmann Research Lab at the University of West Florida. <a href="{SITE}/feed.xml">Subscribe with the news feed</a>.</p>
{cards}"""
    return head("News and Research Updates | Guttmann Research Lab", desc, "news.html", "website", ld_tag) + body + FOOT


def feed():
    items = ""
    for p in posts[:30]:
        url = f"{SITE}/news-{p['slug']}.html"
        items += f"""<item>
<title>{e(p["title"])}</title>
<link>{url}</link>
<guid isPermaLink="true">{url}</guid>
<pubDate>{rfc822(p["date"])}</pubDate>
<category>{e(p["category"])}</category>
<description>{e(p["summary"])}</description>
</item>
"""
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
<channel>
<title>Guttmann Research Lab News</title>
<link>{SITE}/news.html</link>
<description>Research explainers, caregiver resources and program updates from the Guttmann Research Lab at the University of West Florida.</description>
<language>en-us</language>
<lastBuildDate>{rfc822(posts[0]["date"])}</lastBuildDate>
{items}</channel>
</rss>
"""


def sitemap():
    latest = posts[0]["date"]
    rows = [(f"{SITE}/", latest, "weekly", "1.0"),
            (f"{SITE}/news.html", latest, "weekly", "0.8"),
            (f"{SITE}/guttmann-cv.pdf", "2026-11-24", "yearly", "0.5")]
    rows += [(f"{SITE}/news-{p['slug']}.html", p.get("modified", p["date"]), "monthly", "0.6") for p in posts]
    body = "".join(f"  <url>\n    <loc>{u}</loc>\n    <lastmod>{d}</lastmod>\n    <changefreq>{c}</changefreq>\n    <priority>{pr}</priority>\n  </url>\n"
                   for u, d, c, pr in rows)
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{body}</urlset>\n'


def write(name, text):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(text)
    print("wrote", name)


for p in posts:
    n, t = post_page(p)
    write(n, t)
write("news.html", index_page())
write("feed.xml", feed())
write("sitemap.xml", sitemap())
