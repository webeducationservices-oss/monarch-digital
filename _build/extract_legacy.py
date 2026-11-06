#!/usr/bin/env python3
"""One-time capture of the existing blog posts before the rebrand rebuild.

Reads blog/<slug>/index.html for every post that is NOT one of the new
_build/content/blog/*.md posts and writes _build/content/legacy/<slug>.json.
The article body is kept exactly as published (including client-written posts).
Re-running is safe: an existing legacy JSON is never overwritten.
"""
import html
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BLOG = os.path.join(ROOT, "blog")
OUT = os.path.join(ROOT, "_build", "content", "legacy")
NEW = {f[:-3] for f in os.listdir(os.path.join(ROOT, "_build", "content", "blog")) if f.endswith(".md")}
os.makedirs(OUT, exist_ok=True)


def grab(pattern, text, flags=re.S):
    m = re.search(pattern, text, flags)
    return m.group(1).strip() if m else ""


for slug in sorted(os.listdir(BLOG)):
    path = os.path.join(BLOG, slug, "index.html")
    if slug in NEW or not os.path.isfile(path):
        continue
    dest = os.path.join(OUT, f"{slug}.json")
    if os.path.exists(dest):
        print(f"keep  {slug} (already captured)")
        continue
    page = open(path, encoding="utf-8").read()
    hero = re.search(r'<section class="blog-post-hero">.*?<img src="([^"]+)"', page, re.S)
    body = grab(r'<article class="blog-article">(.*?)</article>', page)
    record = {
        "slug": slug,
        "title": html.unescape(grab(r"<h1[^>]*>(.*?)</h1>", page)),
        "date": grab(r'"datePublished":\s*"([^"]+)"', page),
        "category_original": html.unescape(grab(r'class="blog-post-cat">([^<]*)<', page)),
        "description": html.unescape(grab(r'<meta name="description" content="([^"]*)"', page)),
        "hero": hero.group(1) if hero else "",
        "body": body,
    }
    if not (record["title"] and record["body"] and record["date"]):
        raise SystemExit(f"could not parse {slug}: {[k for k, v in record.items() if not v]}")
    with open(dest, "w", encoding="utf-8") as fh:
        json.dump(record, fh, indent=2, ensure_ascii=False)
    print(f"saved {slug} ({record['date']}, {len(body)} chars, hero {record['hero']})")
