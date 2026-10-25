"""Create a "bridge" page for a SafeShare video, to be linked from Google Classroom.

Why: SafeShare sits behind Cloudflare, which blocks Classroom's link-preview
crawler, so the attachment card shows "Just a moment..." instead of the video
title. A page on GitHub Pages carries the real title and thumbnail (Open Graph
tags) and links the pupil on to SafeShare with one tap (no automatic redirect:
Classroom renders the page in a real browser and would follow it).

Usage:
    python -I tools/new_page.py <safeshare-url> [--title "Custom title"] [--slug custom-slug]

Writes docs/<slug>/index.html and rebuilds docs/index.html (list of all pages).
Prints the public URL to paste into Classroom.
"""

import argparse
import html
import re
import sys
import unicodedata
import urllib.request
from pathlib import Path

PAGES_BASE = "https://teacheratwork.github.io/video-classroom"
DOCS = Path(__file__).resolve().parent.parent / "docs"
# A normal browser user agent: with it Cloudflare lets the request through,
# while bot-like agents (Classroom's crawler included) get the challenge page.
BROWSER_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/130.0 Safari/537.36"
)


def fetch(url):
    """Download the SafeShare page, following redirects (app. -> watch.)."""
    req = urllib.request.Request(url, headers={"User-Agent": BROWSER_UA})
    with urllib.request.urlopen(req, timeout=20) as resp:
        return resp.geturl(), resp.read().decode("utf-8", errors="replace")


def meta(page, prop):
    m = re.search(r'property="%s"\s+content="([^"]*)"' % re.escape(prop), page)
    return html.unescape(m.group(1)) if m else None


def slugify(text):
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:60] or "video"


PAGE_TEMPLATE = """<!doctype html>
<html lang="it">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<title>{title}</title>
<meta property="og:type" content="video.other">
<meta property="og:title" content="{title}">
<meta property="og:description" content="Video">
<meta property="og:image" content="{image}">
<meta property="og:url" content="{self_url}">
<meta name="twitter:card" content="summary_large_image">
<style>
  body {{ margin: 0; min-height: 100vh; display: grid; place-items: center;
         font-family: system-ui, sans-serif; background: #f4f6fb; color: #1d2433; }}
  main {{ text-align: center; padding: 16px; max-width: 640px; }}
  a.poster {{ position: relative; display: block; }}
  img {{ width: 100%; border-radius: 12px; display: block; }}
  .play {{ position: absolute; inset: 0; margin: auto; width: 88px; height: 62px;
          border-radius: 16px; background: rgba(26, 115, 232, .9); }}
  .play::after {{ content: ""; position: absolute; left: 36px; top: 17px;
                 border-style: solid; border-width: 14px 0 14px 24px;
                 border-color: transparent transparent transparent #fff; }}
  a.btn {{ display: inline-block; margin-top: 8px; padding: 12px 24px; border-radius: 8px;
          background: #1a73e8; color: #fff; text-decoration: none; font-weight: 600; }}
</style>
</head>
<body>
<main>
  <!-- No automatic redirect: Classroom renders the page in a real browser and
       would follow it to SafeShare (Cloudflare challenge). The pupil taps instead. -->
  <a class="poster" href="{target}"><img src="{image}" alt=""><span class="play"></span></a>
  <h1>{title}</h1>
  <a class="btn" href="{target}">&#9654; Guarda il video</a>
</main>
</body>
</html>
"""

INDEX_TEMPLATE = """<!doctype html>
<html lang="it">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<title>Video per Classroom</title>
<style>body {{ font-family: system-ui, sans-serif; margin: 0 auto; padding: 16px; max-width: 640px; }}</style>
</head>
<body>
<h1>Video per Classroom</h1>
<ul>
{items}
</ul>
</body>
</html>
"""


def rebuild_index():
    items = []
    for page in sorted(DOCS.glob("*/index.html")):
        m = re.search(r"<title>(.*?)</title>", page.read_text(encoding="utf-8"))
        title = m.group(1) if m else page.parent.name
        items.append('  <li><a href="%s/">%s</a></li>' % (page.parent.name, title))
    (DOCS / "index.html").write_text(INDEX_TEMPLATE.format(items="\n".join(items)), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("--title")
    ap.add_argument("--slug")
    args = ap.parse_args()

    target, page = fetch(args.url)
    title = args.title or meta(page, "og:title")
    if not title:
        sys.exit("Title not found on the SafeShare page: pass it with --title")

    # Thumbnail: YouTube's own image when the video comes from YouTube (always
    # reachable), otherwise whatever SafeShare declares.
    yt = re.search(r"youtube\.com/embed/([A-Za-z0-9_-]{11})", page)
    image = ("https://i.ytimg.com/vi/%s/hqdefault.jpg" % yt.group(1)) if yt else meta(page, "og:image")

    slug = args.slug or slugify(title)
    out = DOCS / slug / "index.html"
    if out.exists() and not args.slug:
        # Same title as an existing page: add a suffix rather than overwrite it.
        n = 2
        while (DOCS / ("%s-%d" % (slug, n)) / "index.html").exists():
            n += 1
        slug = "%s-%d" % (slug, n)
        out = DOCS / slug / "index.html"

    self_url = "%s/%s/" % (PAGES_BASE, slug)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(PAGE_TEMPLATE.format(
        title=html.escape(title),
        image=html.escape(image or ""),
        self_url=self_url,
        target=html.escape(target),
    ), encoding="utf-8")
    rebuild_index()

    print("Title: ", title)
    print("Image: ", image)
    print("Target:", target)
    print("URL:   ", self_url)


if __name__ == "__main__":
    main()
