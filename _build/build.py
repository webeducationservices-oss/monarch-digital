#!/usr/bin/env python3
"""Monarch Digital site generator.

  python3 _build/build.py            # build every page
  python3 _build/build.py --check    # build into a temp dir and report, write nothing

Content lives in _build/content/ (pages/*.json, blog/*.md, legacy/*.json).
Every generated page carries the myaieditor inline-edit loader.

Client edits: a page that has an "Edit <file>" commit (made in myaieditor) after the
most recent commit whose message contains [monarch-build] is SKIPPED, so a rebuild
never wipes Christy's changes. Fold her edit into the content files, then rebuild with
MONARCH_OVERWRITE_EDITED=1. Commit generator output with [monarch-build] in the message.
"""
import datetime as dt
import hashlib
import html
import json
import math
import os
import re
import subprocess
import sys

import markdown
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from icons import icon  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTENT = os.path.join(ROOT, "_build", "content")
TODAY = dt.date.today().isoformat()
BUILD_TAG = "[monarch-build]"

SITE = {
    "name": "Monarch Digital",
    "url": "https://www.mymonarchdigital.com",
    "phone": "727-383-6038",
    "phone_href": "tel:+17273836038",
    "email": "info.monarchdigital@gmail.com",
    "base": "Tampa Bay, Florida",
    "tagline": "Hospitality Infrastructure",
    "promise": "We do the work. You guide the process.",
    "form_slug": "monarch-digital",
}

# key, url, menu title, menu blurb, icon
CAPS = [
    ("software", "/custom-restaurant-software/", "Custom Software", "Apps, reservations, host stand, kitchen screens", "code"),
    ("ai", "/ai-for-restaurants/", "AI Assistants", "Operations evaluations and marketing help", "zap"),
    ("training", "/restaurant-staff-training/", "Training and LMS", "Custom online learning for every role", "file-text"),
    ("marketing", "/restaurant-marketing/", "Marketing", "SEO, social, ads, email, and reviews", "target"),
    ("scheduling", "/restaurant-scheduling/", "Scheduling and Labor", "Weekly drafts that protect margin", "calendar"),
    ("operations", "/restaurant-operations-consulting/", "Operations Consulting", "Pacing, turns, prime cost, SOPs", "settings"),
    ("furniture", "/restaurant-furniture/", "Furniture and FF&amp;E", "From floor plan to install", "home"),
    ("uniforms", "/restaurant-uniforms/", "Uniform Programs", "Every role, every location", "tag"),
    ("multilocation", "/multi-location-restaurants/", "Multi-Location", "One standard across every unit", "map"),
]
CAP = {c[0]: c for c in CAPS}

URLS = {"home": "/", "services": "/services/", "casestudy": "/case-study/", "about": "/about/",
        "assessment": "/ai-assessment/", "contact": "/contact/", "blog": "/blog/"}
URLS.update({c[0]: c[1] for c in CAPS})

ALT = {
    "home-detail": "Restaurant team sharing a family meal before service",
    "services-hero": "Restaurant owner and consultant reviewing plans in a dining room",
    "services-detail": "Fabric swatches, a chef coat, a floor plan, and a tablet on a walnut table",
    "software-hero": "Host using a tablet at a restaurant host stand as guests arrive",
    "software-detail": "Server holding a tablet beside a set table",
    "ai-hero": "Restaurant manager reviewing charts on a laptop in the back office",
    "ai-detail": "Smartphone on a bar top showing an assistant conversation",
    "training-hero": "Trainer coaching two new servers with a tablet before service",
    "training-detail": "Chef teaching a line cook how to plate a dish",
    "marketing-hero": "Plated dishes being photographed with a phone for social media",
    "marketing-detail": "Busy restaurant patio at golden hour",
    "scheduling-hero": "General manager reviewing the weekly schedule at the bar after close",
    "scheduling-detail": "Restaurant team in a pre-shift meeting",
    "furniture-hero": "Finished restaurant dining room with walnut tables and leather banquettes",
    "furniture-detail": "Wood, leather, and fabric furniture samples beside a floor plan",
    "uniforms-hero": "Restaurant team in coordinated uniforms",
    "uniforms-detail": "Folded chef coats, aprons, and server shirts on shelves",
    "operations-hero": "Kitchen pass during dinner service",
    "operations-detail": "Restaurant owner reviewing reports and a menu with a calculator",
    "multilocation-hero": "City street at dusk lined with glowing restaurants",
    "multilocation-detail": "Regional manager walking a newly opened location as staff set tables",
    "about-hero": "Monarch butterfly resting on a patio screen at sunrise",
    "about-detail": "Christy Renner, Founder and CEO of Monarch Digital",
    "casestudy-hero": "Snowy mountain village at dusk",
    "casestudy-detail": "Private dining room set for dinner beside a stone fireplace",
    "assessment-hero": "Restaurant owner reading a report on a tablet before opening",
    "contact-hero": "Restaurant entrance glowing at dusk",
    "blog-hero": "Restaurant owner's desk with notebook, menu drafts, and coffee",
}

MOCK_CAPTION = {
    "host": "Host stand with live floor map and waitlist",
    "schedule": "Weekly schedule drafted by department",
    "kitchen": "Kitchen display with ticket timers and pacing",
    "lms": "Training academy with daily progress and trainer sign-off",
    "ai": "AI assistant answering with real data, waiting for a person to confirm",
    "report": "AI restaurant assessment report",
    "brief": "Server tablet guest brief, allergies first",
    "booking": "Guest reservation flow on a phone",
    "marketing": "Marketing dashboard tied to reviews and bookings",
}

REDIRECTS = [
    ("/content-creation", "/restaurant-marketing/"), ("/blogging", "/restaurant-marketing/"),
    ("/email-marketing", "/restaurant-marketing/"), ("/social-media", "/restaurant-marketing/"),
    ("/digital-advertising", "/restaurant-marketing/"), ("/seo-analysis", "/restaurant-marketing/"),
    ("/about-us", "/about/"), ("/our-story", "/about/"), ("/contact-us", "/contact/"),
    ("/our-services", "/services/"), ("/home", "/"), ("/assessment", "/ai-assessment/"),
]
RETIRED_FILES = ["content-creation.html", "blogging.html", "email-marketing.html", "social-media.html",
                 "digital-advertising.html", "seo-analysis.html"]

HEX = hashlib.md5


# ---------------------------------------------------------------- helpers
def esc(s):
    return html.escape(str(s), quote=True)


ALLOWED = re.compile(r"</?(?:a|strong|em)(?:\s+href=\"[^\"]*\")?\s*>", re.I)


def rich(s):
    """Escape body copy but keep <a href>, <strong>, <em> from the content files."""
    s = str(s)
    keep = {}

    def stash(m):
        k = f"\x00{len(keep)}\x00"
        keep[k] = m.group(0)
        return k
    s = ALLOWED.sub(stash, s)
    s = html.escape(s, quote=False)
    for k, v in keep.items():
        s = s.replace(k, v)
    return s.replace("&amp;amp;", "&amp;")


def asset_version(rel):
    with open(os.path.join(ROOT, rel), "rb") as fh:
        return HEX(fh.read()).hexdigest()[:8]


_size_cache = {}


def img_size(rel):
    path = os.path.join(ROOT, rel.lstrip("/"))
    if path not in _size_cache:
        with Image.open(path) as im:
            _size_cache[path] = im.size
    return _size_cache[path]


def variant(rel, width, folder="sized"):
    """Make (once) a resized WebP copy and return its site path."""
    src = os.path.join(ROOT, rel.lstrip("/"))
    name = os.path.splitext(os.path.basename(src))[0]
    out_rel = f"/images/rebrand/{folder}/{name}-{width}.webp"
    out = os.path.join(ROOT, out_rel.lstrip("/"))
    if not os.path.exists(out) or os.path.getmtime(out) < os.path.getmtime(src):
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with Image.open(src) as im:
            im = im.convert("RGB")
            if im.size[0] > width:
                im = im.resize((width, round(im.size[1] * width / im.size[0])), Image.LANCZOS)
            im.save(out, "WEBP", quality=76, method=6)
    return out_rel


def abs_url(path):
    return SITE["url"] + path


def read_time(text):
    words = len(re.findall(r"\w+", re.sub(r"<[^>]+>", " ", text)))
    return max(1, math.ceil(words / 225))


def fmt_date(iso, long=False):
    d = dt.date.fromisoformat(iso[:10])
    return d.strftime("%B %-d, %Y" if long else "%b %-d, %Y")


def ld(obj):
    return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False).replace("</", "<\\/") + "</script>"


# ---------------------------------------------------------------- client-edit guard
def git(*args):
    return subprocess.run(["git", "-C", ROOT, *args], capture_output=True, text=True).stdout


def client_edited(rel):
    if os.environ.get("MONARCH_OVERWRITE_EDITED") == "1" or not os.path.exists(os.path.join(ROOT, rel)):
        return False
    log = git("log", "--format=%s", "--", rel).splitlines()  # newest first
    for subject in log:
        if BUILD_TAG in subject:
            return False
        if subject.startswith(("Edit ", "Create ")) and subject.endswith(rel):
            return True
    return False


# ---------------------------------------------------------------- chrome
def head(title, desc, path, og_image, schema, og_type="website", preload="", extra=""):
    v_css, v_js = asset_version("styles.css"), asset_version("components.js")
    return f"""<!DOCTYPE html>
<html lang="en" class="no-js">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <script>document.documentElement.className='js'</script>
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(desc)}">
  <link rel="canonical" href="{abs_url(path)}">
  <meta property="og:type" content="{og_type}">
  <meta property="og:site_name" content="{SITE['name']}">
  <meta property="og:title" content="{esc(title)}">
  <meta property="og:description" content="{esc(desc)}">
  <meta property="og:url" content="{abs_url(path)}">
  <meta property="og:image" content="{og_image}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{esc(title)}">
  <meta name="twitter:description" content="{esc(desc)}">
  <meta name="twitter:image" content="{og_image}">
  <link rel="icon" href="/favicon.ico" sizes="any">
  <link rel="icon" type="image/png" sizes="32x32" href="/images/favicon-32x32.png">
  <link rel="icon" type="image/png" sizes="16x16" href="/images/favicon-16x16.png">
  <link rel="apple-touch-icon" href="/images/apple-touch-icon.png">
  <link rel="manifest" href="/site.webmanifest">
  <meta name="theme-color" content="#1F1F1F">
  <link rel="preload" as="font" type="font/woff2" href="/fonts/inter-400.woff2" crossorigin>
  <link rel="preload" as="font" type="font/woff2" href="/fonts/montserrat-800.woff2" crossorigin>
{preload}  <link rel="stylesheet" href="/styles.css?v={v_css}">
  <script src="/components.js?v={v_js}" defer></script>
  <script src="/ada-widget.js" data-color="#1F1F1F" data-mobile-bottom="16" defer></script>
  <!-- myaieditor inline-edit loader (no-op for real visitors) -->
  <script src="/mae-edit-loader.js" async></script>
{extra}  {schema}
</head>
<body>
<a class="skip-link" href="#main">Skip to content</a>
"""


def logo(cls=""):
    return f"""<a href="/" class="logo {cls}" aria-label="Monarch Digital home">
        <img src="/images/rebrand/butterfly-mark.webp" alt="" width="42" height="42">
        <span class="logo-text"><span class="logo-name">Monarch Digital</span><span class="logo-tag">{SITE['tagline']}</span></span>
      </a>"""


def header(active=""):
    drop = "".join(
        f'<a href="{u}"><span class="di">{icon(ic, "icon")}</span><span><strong>{t}</strong><span class="dd">{d}</span></span></a>'
        for k, u, t, d, ic in CAPS)
    def cur(key):
        return ' aria-current="page"' if key == active else ""
    m_caps = "".join(f'<a href="{u}">{t}</a>' for k, u, t, d, ic in CAPS)
    return f"""<header class="header" id="header">
    <div class="container header-inner">
      {logo()}
      <nav class="nav" aria-label="Main navigation">
        <div class="nav-drop">
          <button type="button" aria-expanded="false" aria-haspopup="true">Services {icon("chevron-down", "icon")}</button>
          <div class="drop-panel">{drop}<a class="drop-all" href="/services/">See every service {icon("arrow-right", "icon")}</a></div>
        </div>
        <a href="/case-study/"{cur("casestudy")}>Our Work</a>
        <a href="/about/"{cur("about")}>About</a>
        <a href="/blog/"{cur("blog")}>Blog</a>
        <a href="/contact/"{cur("contact")}>Contact</a>
        <a href="/ai-assessment/" class="btn btn-gold nav-cta">Free AI Assessment</a>
      </nav>
      <button class="hamburger" id="hamburger" aria-label="Open menu" aria-expanded="false" aria-controls="mobileNav">
        <span></span><span></span><span></span>
      </button>
    </div>
  </header>
  <nav class="mobile-nav" id="mobileNav" aria-label="Mobile navigation">
    <div class="m-label">Services</div>
    <div class="m-sub">{m_caps}<a href="/services/">All services</a></div>
    <div class="m-label">Company</div>
    <a href="/case-study/">Our Work</a><a href="/about/">About</a><a href="/blog/">Blog</a><a href="/contact/">Contact</a>
    <a href="/ai-assessment/" class="btn btn-gold">Get Your Free AI Assessment</a>
  </nav>
"""


def footer():
    caps = "".join(f'<a href="{u}">{t}</a>' for k, u, t, d, ic in CAPS)
    year = dt.date.today().year
    return f"""
  <footer class="footer">
    <div class="container">
      <div class="footer-grid">
        <div class="footer-brand">
          {logo()}
          <p>Everything your restaurant runs on, from one white-glove team. {SITE['promise']}</p>
        </div>
        <div class="footer-col"><h4>Services</h4>{caps}</div>
        <div class="footer-col"><h4>Company</h4>
          <a href="/services/">All Services</a><a href="/case-study/">Our Work</a><a href="/about/">About</a>
          <a href="/blog/">Blog</a><a href="/ai-assessment/">Free AI Assessment</a><a href="/contact/">Contact</a>
        </div>
        <div class="footer-col"><h4>Contact</h4>
          <a href="{SITE['phone_href']}">{SITE['phone']}</a>
          <a href="mailto:{SITE['email']}">{SITE['email']}</a>
          <a href="/contact/">Based in {SITE['base']}</a>
          <a href="/services/">Serving restaurants nationwide</a>
        </div>
      </div>
      <div class="footer-bottom">
        <span>&copy; {year} Monarch Digital. All rights reserved.</span>
        <span>Protected by reCAPTCHA. <a href="https://policies.google.com/privacy">Privacy</a> &middot; <a href="https://policies.google.com/terms">Terms</a></span>
      </div>
    </div>
  </footer>
</body>
</html>
"""


# ---------------------------------------------------------------- page parts
def cta_btn(c, style="btn-gold"):
    if not c or not c.get("label"):
        return ""
    return f'<a href="{esc(c["href"])}" class="btn {style}">{esc(c["label"])}</a>'


def breadcrumbs(trail):
    """trail: list of (name, path); last item is the current page."""
    parts = []
    for i, (name, path) in enumerate(trail):
        if i == len(trail) - 1:
            parts.append(f"<span aria-current=\"page\">{esc(name)}</span>")
        else:
            parts.append(f'<a href="{path}">{esc(name)}</a>')
    visible = '<nav class="breadcrumbs" aria-label="Breadcrumb">' + "<span>/</span>".join(parts) + "</nav>"
    schema = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": abs_url(p)} for i, (n, p) in enumerate(trail)]}
    return visible, schema


def hero_image_tags(key):
    rel = f"/images/rebrand/{key}-hero.webp"
    small = variant(rel, 900)
    w, h = img_size(rel)
    srcset = f"{small} 900w, {rel} {w}w"
    preload = f'  <link rel="preload" as="image" type="image/webp" imagesrcset="{srcset}" imagesizes="100vw" fetchpriority="high">\n'
    tag = f'<img src="{rel}" srcset="{srcset}" sizes="100vw" alt="{esc(ALT.get(key + "-hero", ""))}" width="{w}" height="{h}" fetchpriority="high" decoding="async">'
    return preload, tag


def page_hero(key, h, trail):
    crumbs, crumb_schema = breadcrumbs(trail)
    preload, tag = hero_image_tags(key)
    eyebrow = f'<div class="eyebrow">{esc(h["eyebrow"])}</div>' if h.get("eyebrow") else ""
    body = f"""  <section class="page-hero" aria-label="{esc(h['h1'])}">
    <div class="page-hero-media">{tag}</div>
    <div class="container">
      {crumbs}
      <div class="hero-copy">
        {eyebrow}
        <h1>{esc(h['h1'])}</h1>
        <p class="hero-sub">{rich(h.get('sub', ''))}</p>
        <div class="btn-row">{cta_btn(h.get('primary_cta'))}{cta_btn(h.get('secondary_cta'), 'btn-ghost')}</div>
      </div>
    </div>
  </section>
"""
    return preload, body, crumb_schema


def media(ref, alt_hint=""):
    kind, _, name = (ref or "").partition(":")
    if kind == "image":
        rel = "/images/christy-hero.webp" if name == "about-detail" else f"/images/rebrand/{name}.webp"
        small = variant(rel, 1000)
        w, h = img_size(small)
        return (f'<figure class="media-photo"><img src="{small}" alt="{esc(ALT.get(name, alt_hint))}" '
                f'width="{w}" height="{h}" loading="lazy" decoding="async"></figure>')
    if kind == "mockup":
        rel = f"/images/rebrand/mock-{name}.webp"
        w, h = img_size(rel)
        cap = f"{MOCK_CAPTION.get(name, 'Software screen')}. Illustrative screen with sample data."
        img = f'<img src="{rel}" alt="{esc(MOCK_CAPTION.get(name, "Software screen"))}" width="{w}" height="{h}" loading="lazy" decoding="async">'
        if name == "booking":
            frame = f'<div class="frame-phone">{img}</div>'
        elif name == "brief":
            frame = f'<div class="frame-tablet">{img}</div>'
        else:
            frame = f'<div class="frame"><div class="frame-bar"><span></span><span></span><span></span></div>{img}</div>'
        return f'<figure class="media-mock">{frame}<figcaption>{esc(cap)}</figcaption></figure>'
    return ""


def section_head(s, center=False, dark=False):
    label = f'<div class="label">{esc(s["label"])}</div>' if s.get("label") else ""
    h2 = f"<h2>{esc(s['h2'])}</h2>" if s.get("h2") else ""
    sub = f"<p>{rich(s['sub'])}</p>" if s.get("sub") else ""
    if not (label or h2 or sub):
        return ""
    return f'<div class="section-head{" center" if center else ""} reveal">{label}{h2}{sub}</div>'


def grid_class(n):
    return "grid-4" if n == 4 else ("grid-2" if n == 2 else "grid-3")


def render_section(s, idx, page_key):
    t = s.get("type")
    bg = "bg-cream" if idx % 2 == 0 else ""
    if t == "intro":
        body = "".join(f"<p>{rich(p)}</p>" for p in s.get("body", []))
        label = f'<div class="label">{esc(s["label"])}</div>' if s.get("label") else ""
        return f"""  <section class="{bg}"><div class="container narrow intro reveal">{label}<h2>{esc(s.get('h2', ''))}</h2><div class="prose">{body}</div></div></section>\n"""
    if t == "split":
        body = "".join(f"<p>{rich(p)}</p>" for p in s.get("body", []))
        ticks = ""
        if s.get("bullets"):
            ticks = '<ul class="ticks">' + "".join(f"<li>{icon('check-circle', 'icon')}<span>{rich(b)}</span></li>" for b in s["bullets"]) + "</ul>"
        label = f'<div class="label">{esc(s["label"])}</div>' if s.get("label") else ""
        rev = " reverse" if s.get("reverse") else ""
        return f"""  <section class="{bg}"><div class="container split{rev}">
    <div class="split-copy reveal">{label}<h2>{esc(s.get('h2', ''))}</h2>{body}{ticks}</div>
    <div class="reveal">{media(s.get('media'), s.get('h2', ''))}</div>
  </div></section>\n"""
    if t in ("features", "cards"):
        items = s.get("items", [])
        cells = ""
        for it in items:
            ic = it.get("icon") or "check-circle"
            inner = f'<div class="feature-icon">{icon(ic, "icon")}</div><h3>{esc(it.get("title", ""))}</h3><p>{rich(it.get("text", ""))}</p>'
            if t == "cards" and it.get("href"):
                cells += f'<a class="feature reveal" href="{esc(it["href"])}">{inner}<span class="card-more">Learn more {icon("arrow-right", "icon")}</span></a>'
            else:
                cells += f'<div class="feature reveal">{inner}</div>'
        return f"""  <section class="{bg}"><div class="container">{section_head(s)}<div class="grid {grid_class(len(items))}">{cells}</div></div></section>\n"""
    if t == "steps":
        items = s.get("items", [])
        cells = "".join(f'<div class="step reveal"><h3>{esc(it.get("title", ""))}</h3><p>{rich(it.get("text", ""))}</p></div>' for it in items)
        return f"""  <section class="bg-dark"><div class="container">{section_head(s, dark=True)}<div class="steps" style="--n:{len(items)}">{cells}</div></div></section>\n"""
    if t == "stats":
        items = s.get("items", [])
        cells = "".join(f'<div class="reveal"><div class="stat-num">{esc(it.get("number", ""))}</div><div class="stat-label">{rich(it.get("label", ""))}</div></div>' for it in items)
        head_html = ""
        if s.get("h2") or s.get("label"):
            head_html = section_head(s, center=True, dark=True)
        return f"""  <section class="stats-band bg-dark"><div class="container">{head_html}<div class="stats" style="--n:{len(items)}">{cells}</div></div></section>\n"""
    if t == "showcase":
        cap = s.get("caption") or MOCK_CAPTION.get(s.get("mockup"), "")
        fig = media("mockup:" + s.get("mockup", "report"))
        if s.get("caption"):
            fig = fig.replace(f"{esc(MOCK_CAPTION.get(s.get('mockup'), 'Software screen'))}. Illustrative", f"{esc(cap.rstrip('.'))}. Illustrative", 1)
        return f"""  <section class="showcase {bg}"><div class="container">{section_head(s, center=True)}<div class="reveal">{fig}</div></div></section>\n"""
    if t == "checklist":
        items = "".join(f"<li>{icon('check-circle', 'icon')}<span>{rich(i)}</span></li>" for i in s.get("items", []))
        return f"""  <section class="{bg}"><div class="container">{section_head(s)}<ul class="checklist reveal">{items}</ul></div></section>\n"""
    if t == "story":
        body = "".join(f"<p>{rich(p)}</p>" for p in s.get("body", []))
        label = f'<div class="label">{esc(s["label"])}</div>' if s.get("label") else ""
        return f"""  <section class="{bg}"><div class="container narrow story reveal">{label}<h2>{esc(s.get('h2', ''))}</h2>{body}</div></section>\n"""
    if t == "butterfly":
        story = open(os.path.join(CONTENT, "butterfly_story.md"), encoding="utf-8").read().strip().split("\n\n")
        paras = "".join(f"<p>{esc(p)}</p>" for p in story)
        lead = f'<p class="hero-sub" style="color:var(--g600)">{rich(s["lead"])}</p>' if s.get("lead") else ""
        return f"""  <section class="{bg}" id="story"><div class="container narrow story">
    <div class="label">{esc(s.get('label', 'Our Story'))}</div><h2>{esc(s.get('h2', 'Why The Butterfly'))}</h2>{lead}
    <div class="butterfly-story">{paras}</div>
    <p style="font-family:var(--font-head);font-weight:700;color:var(--ink)">Christy Renner, Founder and CEO</p>
  </div></section>\n"""
    if t == "testimonials":
        quotes = [
            ("Working with Monarch Digital has been amazing; I never thought that we could run so many marketing campaigns so effectively every week!", "Maria Amalia Robbin", "Business Owner"),
            ("Christy is a wonderful digital marketer for a Pilates Studio. Christy understands Pilates as she is an avid practitioner and brings real insight to every campaign.", "Rosemary Todaro", "Pilates Studio Owner"),
            ("Christy was wonderful to work with. She really took the time to walk me through what she was doing and why. Highly recommend Monarch Digital!", "Fernanda Bapo", "Entrepreneur"),
        ]
        stars = '<div class="stars" aria-label="5 stars">' + icon("star", "icon") * 5 + "</div>"
        cards = "".join(f'<figure class="testimonial reveal">{stars}<blockquote>"{esc(q)}"</blockquote><cite>{esc(n)}<span>{esc(r)}</span></cite></figure>' for q, n, r in quotes)
        s = dict(s, sub=s.get("sub") or "From business owners Christy has worked with over the years.")
        return f"""  <section class="{bg}"><div class="container">{section_head(s, center=True)}<div class="testimonials">{cards}</div></div></section>\n"""
    if t == "cta":
        return cta_band(s)
    raise SystemExit(f"{page_key}: unknown section type {t!r}")


def cta_band(s):
    return f"""  <section class="cta-band"><div class="container reveal">
    <h2>{esc(s.get('h2', ''))}</h2><p>{rich(s.get('sub', ''))}</p>
    <div class="btn-row">{cta_btn(s.get('primary_cta'))}{cta_btn(s.get('secondary_cta'), 'btn-ghost')}</div>
    <div class="cta-contact">Prefer to talk? Call <a href="{SITE['phone_href']}">{SITE['phone']}</a> or email <a href="mailto:{SITE['email']}">{SITE['email']}</a></div>
  </div></section>
"""


def faq_section(items, idx):
    if not items:
        return "", None
    bg = "bg-cream" if idx % 2 == 0 else ""
    rows = "".join(
        f'<details><summary>{esc(i["q"])}{icon("chevron-down", "icon")}</summary><div class="faq-a">{rich(i["a"])}</div></details>'
        for i in items)
    schema = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": i["q"], "acceptedAnswer": {"@type": "Answer", "text": re.sub(r"<[^>]+>", "", i["a"])}}
        for i in items]}
    html_ = f"""  <section class="{bg}" id="faq"><div class="container">
    <div class="section-head center reveal"><div class="label">Questions</div><h2>Frequently Asked Questions</h2></div>
    <div class="faq">{rows}</div>
  </div></section>
"""
    return html_, schema


def related_section(keys, idx):
    keys = [k for k in (keys or []) if k in CAP][:3]
    if not keys:
        return ""
    bg = "bg-cream" if idx % 2 == 0 else ""
    cells = "".join(
        f'<a class="feature reveal" href="{CAP[k][1]}"><div class="feature-icon">{icon(CAP[k][4], "icon")}</div>'
        f'<h3>{CAP[k][2]}</h3><p>{CAP[k][3]}.</p><span class="card-more">Learn more {icon("arrow-right", "icon")}</span></a>'
        for k in keys)
    return f"""  <section class="{bg}"><div class="container">
    <div class="section-head reveal"><div class="label">Keep exploring</div><h2>Related Services</h2></div>
    <div class="grid grid-3">{cells}</div>
  </div></section>
"""


def org_schema():
    return {
        "@context": "https://schema.org", "@type": "ProfessionalService", "@id": SITE["url"] + "/#org",
        "name": SITE["name"], "url": SITE["url"] + "/", "logo": SITE["url"] + "/images/butterfly-hero.png",
        "image": SITE["url"] + "/images/rebrand/og/home-detail.jpg", "telephone": "+1-727-383-6038", "email": SITE["email"],
        "description": "All-in-one restaurant and hospitality partner: custom software, AI assistants, staff training and custom LMS, marketing, scheduling, operations consulting, furniture and FF&E sourcing, and uniform programs.",
        "address": {"@type": "PostalAddress", "addressRegion": "FL", "addressCountry": "US"},
        "areaServed": {"@type": "Country", "name": "United States"},
        "founder": {"@type": "Person", "name": "Christy Renner", "jobTitle": "Founder and CEO"},
        "slogan": SITE["promise"],
    }


# ---------------------------------------------------------------- blog content
def parse_front(text):
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", text, re.S)
    if not m:
        raise ValueError("missing front matter")
    meta = {}
    for line in m.group(1).splitlines():
        mm = re.match(r'^(\w+):\s*"?(.*?)"?\s*$', line)
        if mm:
            meta[mm.group(1)] = mm.group(2).replace('\\"', '"')
    return meta, m.group(2)


def load_posts():
    posts = []
    bdir = os.path.join(CONTENT, "blog")
    for f in sorted(os.listdir(bdir)):
        if not f.endswith(".md"):
            continue
        meta, body_md = parse_front(open(os.path.join(bdir, f), encoding="utf-8").read())
        slug = meta.get("slug") or f[:-3]
        body = markdown.markdown(body_md, extensions=["tables", "sane_lists"])
        hero = f"/images/rebrand/blog-{slug}.webp"
        if not os.path.exists(os.path.join(ROOT, hero.lstrip("/"))):
            hero = "/images/rebrand/blog-hero.webp"  # until its own image is generated
        posts.append({"slug": slug, "title": meta["title"], "date": meta["date"], "category": meta["category"],
                      "description": meta["description"], "service": meta.get("service", ""), "hero": hero,
                      "body": body, "new": True, "read": read_time(body)})
    ldir = os.path.join(CONTENT, "legacy")
    for f in sorted(os.listdir(ldir)):
        rec = json.load(open(os.path.join(ldir, f), encoding="utf-8"))
        posts.append({"slug": rec["slug"], "title": rec["title"], "date": rec["date"], "category": "Marketing",
                      "description": rec["description"], "service": "marketing", "hero": rec["hero"],
                      "body": rec["body"], "new": False, "read": read_time(rec["body"])})
    posts.sort(key=lambda p: p["date"], reverse=True)
    return posts


def post_og(p):
    if p["new"] and os.path.exists(os.path.join(ROOT, f"images/rebrand/og/blog-{p['slug']}.jpg")):
        return abs_url(f"/images/rebrand/og/blog-{p['slug']}.jpg")
    if p["hero"].endswith((".jpg", ".jpeg", ".png")):
        return abs_url(p["hero"])
    return abs_url("/images/rebrand/og/blog-hero.jpg")


def thumb(p):
    return variant(p["hero"], 640, "thumbs")


# ---------------------------------------------------------------- page writers
def write(rel, content, report):
    if client_edited(rel):
        report.append(f"SKIP  {rel} (edited in myaieditor since the last build; fold the edit into content first)")
        return
    path = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(path) or ROOT, exist_ok=True)
    old = open(path, encoding="utf-8").read() if os.path.exists(path) else None
    if old != content:
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(content)
        report.append(f"write {rel}")


def build_content_page(key, data, posts, report):
    path = URLS[key]
    rel = "index.html" if key == "home" else path.strip("/") + ".html"
    schemas = []
    sections = [s for s in data.get("sections", [])]
    final_cta = None
    if sections and sections[-1].get("type") == "cta":
        final_cta = sections.pop()
    else:
        for i, s in enumerate(sections):
            if s.get("type") == "cta":
                final_cta = sections.pop(i)
                break

    if key == "home":
        h = data["hero"]
        preload = '  <link rel="preload" as="image" type="image/webp" href="/images/butterfly-hero.webp" fetchpriority="high">\n'
        eyebrow = f'<div class="eyebrow">{esc(h["eyebrow"])}</div>' if h.get("eyebrow") else ""
        hero_html = f"""  <section class="home-hero" aria-label="Introduction">
    <div class="container home-hero-grid">
      <div class="hero-copy">
        {eyebrow}
        <h1>{esc(h['h1'])}</h1>
        <p class="hero-sub">{rich(h.get('sub', ''))}</p>
        <div class="btn-row">{cta_btn(h.get('primary_cta'))}{cta_btn(h.get('secondary_cta'), 'btn-ghost')}</div>
        <div class="trust-line">{icon('map-pin', 'icon')}Based in {SITE['base']}. Serving restaurants nationwide.</div>
      </div>
      <div class="hero-mark"><img src="/images/butterfly-hero.webp" alt="Monarch Digital butterfly mark" width="800" height="800" fetchpriority="high"></div>
    </div>
  </section>
"""
        schemas += [org_schema(), {"@context": "https://schema.org", "@type": "WebSite", "name": SITE["name"], "url": SITE["url"] + "/"}]
        og = abs_url("/images/rebrand/og/home-detail.jpg")
    else:
        trail = [("Home", "/")]
        if key in CAP:
            trail.append(("Services", "/services/"))
        short = {"services": "Services", "casestudy": "Our Work", "about": "About"}
        crumb = data.get("crumb") or (CAP[key][2].replace("&amp;", "&") if key in CAP else short.get(key)) or data["title"].split("|")[0].strip()
        trail.append((crumb, path))
        preload, hero_html, crumb_schema = page_hero(key, data["hero"], trail)
        schemas.append(crumb_schema)
        og = abs_url(f"/images/rebrand/og/{key}-hero.jpg")
        if key in CAP:
            schemas.append({"@context": "https://schema.org", "@type": "Service", "name": data["hero"]["h1"],
                            "serviceType": re.sub(r"&amp;", "&", CAP[key][2]), "url": abs_url(path), "description": data["description"],
                            "provider": {"@id": SITE["url"] + "/#org", "@type": "ProfessionalService", "name": SITE["name"], "url": SITE["url"] + "/"},
                            "areaServed": {"@type": "Country", "name": "United States"}})
        if key == "about":
            schemas.append({"@context": "https://schema.org", "@type": "AboutPage", "url": abs_url(path), "name": data["title"],
                            "mainEntity": {"@type": "Person", "name": "Christy Renner", "jobTitle": "Founder and CEO",
                                           "worksFor": {"@type": "Organization", "name": SITE["name"], "url": SITE["url"] + "/"},
                                           "image": SITE["url"] + "/images/christy-hero.webp"}})
        if key == "casestudy":
            schemas.append({"@context": "https://schema.org", "@type": "Article", "headline": data["hero"]["h1"],
                            "description": data["description"], "image": og, "url": abs_url(path),
                            "author": {"@type": "Organization", "name": SITE["name"]},
                            "publisher": {"@type": "Organization", "name": SITE["name"], "logo": {"@type": "ImageObject", "url": SITE["url"] + "/images/butterfly-hero.png"}}})

    body = ""
    idx = 0
    for s in sections:
        body += render_section(s, idx, key)
        if s.get("type") not in ("steps", "stats"):
            idx += 1
    if key == "home":
        body += latest_posts_section(posts, idx)
        idx += 1
    faq_html, faq_schema = faq_section(data.get("faq"), idx)
    if faq_html:
        body += faq_html
        schemas.append(faq_schema)
        idx += 1
    if key in CAP:
        body += related_section(data.get("related"), idx)
        idx += 1
        body += reading_section(key, posts, idx)
    if final_cta:
        body += cta_band(final_cta)

    schema_html = "\n  ".join(ld(s) for s in schemas)
    page = head(data["title"], data["description"], path, og, schema_html, preload=preload)
    page += header(key) + f'  <main id="main">\n{hero_html}{body}  </main>\n' + footer()
    write(rel, page, report)


def reading_section(key, posts, idx):
    picks = [p for p in posts if p["new"] and p["service"] == key][:3]
    if len(picks) < 3:
        picks += [p for p in posts if p["new"] and p not in picks][: 3 - len(picks)]
    if not picks:
        return ""
    bg = "bg-cream" if idx % 2 == 0 else ""
    return f"""  <section class="{bg}"><div class="container">
    <div class="section-head reveal"><div class="label">Related reading</div><h2>From the Blog</h2></div>
    <div class="blog-grid">{"".join(post_card(p) for p in picks)}</div>
  </div></section>
"""


def latest_posts_section(posts, idx):
    picks = [p for p in posts if p["new"]][:3]
    if not picks:
        return ""
    bg = "bg-cream" if idx % 2 == 0 else ""
    cards = "".join(post_card(p) for p in picks)
    return f"""  <section class="{bg}"><div class="container">
    <div class="section-head reveal"><div class="label">From the blog</div><h2>Practical Ideas for Restaurant Owners</h2>
    <p>Straight answers on costs, labor, training, software, and getting found. <a href="/blog/" style="color:var(--teal-text);text-decoration:underline">Read every post</a>.</p></div>
    <div class="blog-grid">{cards}</div>
  </div></section>
"""


def post_card(p):
    t = thumb(p)
    w, h = img_size(t)
    return (f'<a class="post-card reveal" href="/blog/{p["slug"]}/" data-cat="{esc(p["category"])}">'
            f'<div class="post-card-thumb"><img src="{t}" alt="{esc(p["title"])}" width="{w}" height="{h}" loading="lazy" decoding="async"></div>'
            f'<div class="post-card-body"><div class="post-card-cat">{esc(p["category"])}</div>'
            f'<div class="post-card-title">{esc(p["title"])}</div>'
            f'<div class="post-card-meta">{fmt_date(p["date"])} &middot; {p["read"]} min read</div></div></a>')


def build_blog_index(posts, report):
    cats = {}
    for p in posts:
        cats[p["category"]] = cats.get(p["category"], 0) + 1
    order = ["Opening a Restaurant", "Operations", "Software & AI", "Training", "Scheduling & Labor",
             "Marketing", "Furniture & Design", "Uniforms", "Multi-Location"]
    names = [c for c in order if c in cats] + sorted(c for c in cats if c not in order)
    buttons = f'<button class="filter-btn active" data-filter="all" aria-pressed="true">All ({len(posts)})</button>' + "".join(
        f'<button class="filter-btn" data-filter="{esc(c)}" aria-pressed="false">{esc(c)} ({cats[c]})</button>' for c in names)
    cards = "".join(post_card(p) for p in posts)
    data = {"eyebrow": "The Monarch Blog", "h1": "Restaurant Operations, Training, and Marketing Ideas",
            "sub": "Practical guides for owners and GMs on opening, costs, labor, software, AI, furniture, uniforms, and getting found.",
            "primary_cta": {"label": "Get Your Free AI Assessment", "href": "/ai-assessment/"}}
    preload, hero_html, crumb_schema = page_hero("blog", data, [("Home", "/"), ("Blog", "/blog/")])
    schema = {"@context": "https://schema.org", "@type": "Blog", "name": "The Monarch Blog", "url": abs_url("/blog/"),
              "publisher": {"@type": "Organization", "name": SITE["name"]}}
    title = "Restaurant Operations and Marketing Blog | Monarch Digital"
    desc = "Practical guides for restaurant owners: opening costs, food and labor cost, training, scheduling, POS and reservations, AI, furniture, uniforms, and marketing."
    page = head(title, desc, "/blog/", abs_url("/images/rebrand/og/blog-hero.jpg"), ld(crumb_schema) + "\n  " + ld(schema), preload=preload)
    page += header("blog") + f"""  <main id="main">
{hero_html}  <section class="bg-cream"><div class="container">
    <div class="blog-filters" id="blogFilters" role="toolbar" aria-label="Filter posts by category">{buttons}</div>
    <div id="postGrid" class="blog-grid">{cards}</div>
  </div></section>
{cta_band({"h2": "Want a Plan for Your Restaurant?", "sub": "Get a free AI assessment of your operations and marketing, then talk it through with Christy.", "primary_cta": {"label": "Get Your Free AI Assessment", "href": "/ai-assessment/"}, "secondary_cta": {"label": "Talk to Christy", "href": "/contact/"}})}  </main>
""" + footer()
    write("blog/index.html", page, report)


def build_post(p, posts, report):
    same = [q for q in posts if q["category"] == p["category"] and q["slug"] != p["slug"]]
    rest = [q for q in posts if q["slug"] != p["slug"] and q not in same]
    related = (same + rest)[:3]
    links = "\n".join(f'          <a class="sidebar-link" href="/blog/{q["slug"]}/">{esc(q["title"])}</a>' for q in related)
    canonical = f"/blog/{p['slug']}/"
    og = post_og(p)
    hero_w, hero_h = img_size(p["hero"])
    schema = {"@context": "https://schema.org", "@type": "BlogPosting", "headline": p["title"], "description": p["description"],
              "image": og, "datePublished": p["date"][:10], "dateModified": p["date"][:10],
              "author": {"@type": "Organization", "name": SITE["name"]},
              "publisher": {"@type": "Organization", "name": SITE["name"], "logo": {"@type": "ImageObject", "url": SITE["url"] + "/images/butterfly-hero.png"}},
              "mainEntityOfPage": {"@type": "WebPage", "@id": abs_url(canonical)}}
    crumbs = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": abs_url("/")},
        {"@type": "ListItem", "position": 2, "name": "Blog", "item": abs_url("/blog/")},
        {"@type": "ListItem", "position": 3, "name": p["title"], "item": abs_url(canonical)}]}
    body = p["body"]
    if p["new"] and p["service"] in CAP:
        k, u, t, d, ic = CAP[p["service"]]
        body += (f'\n<div class="article-cta"><h3>Want help with this?</h3><p>Monarch handles {t.lower()} for restaurants as part of one '
                 f'white-glove team. {SITE["promise"]} <a href="{u}" style="color:var(--gold-light)">See how {t.lower()} works with us</a>.</p>'
                 f'<a class="btn btn-gold" href="/ai-assessment/">Get Your Free AI Assessment</a></div>')
    title = f"{p['title']} | Monarch Digital"
    preload = f'  <link rel="preload" as="image" href="{p["hero"]}" fetchpriority="high">\n'
    page = head(title, p["description"], canonical, og, ld(schema) + "\n  " + ld(crumbs), og_type="article", preload=preload)
    page += header("blog") + f"""  <main id="main">
  <section class="blog-post-hero">
    <div class="container">
      <img src="{p['hero']}" alt="{esc(p['title'])}" width="{hero_w}" height="{hero_h}" loading="eager" fetchpriority="high">
      <div class="blog-post-hero-content">
        <span class="blog-post-cat">{esc(p['category'])}</span>
        <h1>{esc(p['title'])}</h1>
        <div class="post-meta">
          <span>Monarch Digital</span>
          <span class="post-meta-dot"></span>
          <span>{fmt_date(p['date'], long=True)}</span>
          <span class="post-meta-dot"></span>
          <span>{p['read']} min read</span>
        </div>
      </div>
    </div>
  </section>
  <div class="blog-post-wrap">
    <article class="blog-article">
{body}
    </article>
    <aside class="blog-sidebar">
      <div class="sidebar-card">
        <div class="sidebar-head">Related Articles</div>
        <div class="sidebar-body">
{links}
        </div>
      </div>
      <div class="sidebar-cta">
        <div class="sidebar-cta-title">Free AI Assessment</div>
        <p>See where your restaurant is leaving money on the table, in operations and marketing.</p>
        <a href="/ai-assessment/">Get Your Free AI Assessment</a>
      </div>
    </aside>
  </div>
  </main>
""" + footer()
    write(f"blog/{p['slug']}/index.html", page, report)


def build_special(name, report):
    """Assessment, contact, and 404 pages are written from Python templates in pages_special.py."""
    import pages_special
    page_html, rel = getattr(pages_special, name)(globals())
    write(rel, page_html, report)
    if name == "assessment":
        # One source of truth for the answer choices: the form and api/assess.js both use these.
        opts = {k.lower(): getattr(pages_special, k) for k in ("CONCEPTS", "LOCATIONS", "SEATS", "STAFF", "POS", "RESERVATIONS",
                                                                 "SCHEDULING", "TRAINING", "HEADACHES", "PROJECTS", "CHANNELS", "OWNERS", "GOALS", "ROLES")}
        js = ("// Generated by _build/build.py from _build/pages_special.py. Do not edit by hand.\n"
              f"export const OPTIONS = {json.dumps(opts, indent=2)};\n"
              f"export const SERVICES = {json.dumps({k: {'title': re.sub('&amp;', '&', t), 'url': u} for k, u, t, d, ic in CAPS}, indent=2)};\n")
        write("api/_options.js", js, report)


def build_meta(posts, report):
    urls = [(URLS["home"], TODAY, "weekly", "1.0"), (URLS["services"], TODAY, "monthly", "0.9")]
    urls += [(c[1], TODAY, "monthly", "0.9") for c in CAPS]
    urls += [(URLS[k], TODAY, "monthly", "0.8") for k in ("assessment", "casestudy", "about", "contact")]
    urls += [(URLS["blog"], TODAY, "weekly", "0.8")]
    urls += [(f"/blog/{p['slug']}/", p["date"][:10], "monthly", "0.7") for p in posts]
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for loc, lm, cf, pr in urls:
        xml += f"  <url>\n    <loc>{abs_url(loc)}</loc>\n    <lastmod>{lm}</lastmod>\n    <changefreq>{cf}</changefreq>\n    <priority>{pr}</priority>\n  </url>\n"
    xml += "</urlset>\n"
    write("sitemap.xml", xml, report)
    write("robots.txt", f"User-agent: *\nAllow: /\nDisallow: /api/\n\nSitemap: {SITE['url']}/sitemap.xml\n", report)

    vpath = os.path.join(ROOT, "vercel.json")
    vercel = json.load(open(vpath))
    legacy_slugs = [p["slug"] for p in posts if not p["new"]]
    pairs = list(REDIRECTS) + [(f"/{slug}", f"/blog/{slug}/") for slug in legacy_slugs]
    # trailingSlash is on, so match both "/old" and "/old/" or the slash form 404s.
    redirects = [{"source": src, "destination": d, "permanent": True} for s, d in pairs for src in (s, s + "/")]
    vercel["redirects"] = redirects
    vercel.setdefault("functions", {})["api/assess.js"] = {"maxDuration": 120}
    write("vercel.json", json.dumps(vercel, indent=2) + "\n", report)

    cats = sorted({p["category"] for p in posts if p["new"]} | {"Marketing"})
    cfg_path = os.path.join(ROOT, "blog_config.json")
    cfg = json.load(open(cfg_path)) if os.path.exists(cfg_path) else {}
    cfg.update({"enabled": True, "site_slug": SITE["form_slug"], "framework": "static-html", "content_model": "html",
                "index_page": "blog/index.html", "post_folder": "blog", "post_extension": "html", "post_url_prefix": "/blog/",
                "image_folder": "images/blog", "image_url_prefix": "/images/blog/",
                "reference_post": "blog/restaurant-training-program-lms/index.html",
                "card_container_selector": "#postGrid", "card_class": "post-card", "filter_mechanism": "data-attribute",
                "filter_attribute": "data-cat", "filter_selector": None, "categories": cats})
    cfg.setdefault("meta", {}).update({"default_author": "Monarch Digital", "default_author_type": "Organization",
                                       "cta_text": "Get Your Free AI Assessment", "cta_href": "/ai-assessment/",
                                       "publisher_name": "Monarch Digital", "publisher_logo": SITE["url"] + "/images/butterfly-hero.png",
                                       "blog_url_prefix": "/blog/", "update_sitemap": True, "sitemap_path": "sitemap.xml"})
    write("blog_config.json", json.dumps(cfg, indent=2) + "\n", report)


def ensure_brand_assets():
    mark = os.path.join(ROOT, "images", "rebrand", "butterfly-mark.webp")
    if not os.path.exists(mark):
        with Image.open(os.path.join(ROOT, "images", "butterfly-hero.png")) as im:
            im = im.convert("RGBA")
            im = im.crop(im.getbbox())
            side = max(im.size)
            sq = Image.new("RGBA", (side, side), (0, 0, 0, 0))
            sq.paste(im, ((side - im.size[0]) // 2, (side - im.size[1]) // 2))
            sq.resize((128, 128), Image.LANCZOS).save(mark, "WEBP", quality=90, method=6)


def main():
    report = []
    ensure_brand_assets()
    posts = load_posts()
    pdir = os.path.join(CONTENT, "pages")
    pages = {f[:-5]: json.load(open(os.path.join(pdir, f), encoding="utf-8")) for f in sorted(os.listdir(pdir)) if f.endswith(".json")}
    missing = [k for k in ["home", "services", "about", "casestudy"] + [c[0] for c in CAPS] if k not in pages]
    if missing:
        report.append(f"NOTE  missing page content: {', '.join(missing)}")
    for key, data in pages.items():
        build_content_page(key, data, posts, report)
    build_blog_index(posts, report)
    for p in posts:
        build_post(p, posts, report)
    for name in ("assessment", "contact", "notfound"):
        build_special(name, report)
    build_meta(posts, report)
    for rel in RETIRED_FILES:
        path = os.path.join(ROOT, rel)
        if os.path.exists(path) and not client_edited(rel):
            os.remove(path)
            report.append(f"rm    {rel} (redirected)")
    # Every generated HTML page must carry the inline-edit loader.
    for dirpath, _, files in os.walk(ROOT):
        if any(seg in dirpath for seg in ("/_build", "/.git", "/node_modules", "/api")):
            continue
        for f in files:
            if f.endswith(".html"):
                fp = os.path.join(dirpath, f)
                if "mae-edit-loader.js" not in open(fp, encoding="utf-8").read():
                    report.append(f"WARN  {os.path.relpath(fp, ROOT)} has no mae-edit-loader")
    print("\n".join(report) or "nothing changed")
    print(f"\n{len(posts)} posts, {len(pages)} content pages")


if __name__ == "__main__":
    main()
