#!/usr/bin/env python3
"""Generate site photography with Gemini image models.

Usage:
  python3 _build/gen_images.py pages        # page heroes and detail shots
  python3 _build/gen_images.py blog         # one hero per blog post (reads image_prompt)
  python3 _build/gen_images.py pages --force services-hero

Originals land in _build/img-src/ (not deployed). Optimized WebP goes to
images/rebrand/<key>.webp (1600 wide) and a 1200x630 JPG for social cards to
images/rebrand/og/<key>.jpg. Existing outputs are skipped unless --force names them.
"""
import base64
import concurrent.futures as cf
import io
import json
import os
import re
import sys
import time
import urllib.request

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "_build", "img-src")
OUT = os.path.join(ROOT, "images", "rebrand")
OG = os.path.join(OUT, "og")
for d in (SRC, OUT, OG):
    os.makedirs(d, exist_ok=True)

# Newest first. Models Google reports as gone are skipped for the rest of the run.
MODELS = [m for m in os.environ.get("GEMINI_IMAGE_MODELS", "").split(",") if m] or [
    "gemini-3-pro-image",
    "nano-banana-pro-preview",
    "gemini-nano-banana-2.1",
    "gemini-3.1-flash-image",
    "gemini-2.5-flash-image",
]
DEAD = set()

STYLE = (
    "Photorealistic editorial photograph for a hospitality company website. Natural, warm light, "
    "shallow depth of field, rich but realistic color. Palette leans deep charcoal, warm brass and gold, "
    "cream, with a subtle teal accent somewhere in the frame. Absolutely no text, no letters, no logos, "
    "no readable signage, no brand names, no watermarks. Any people are ordinary, natural, and not "
    "looking at the camera. Wide 16:9 composition with room for the subject to breathe."
)

PAGES = {
    "home-detail": "A restaurant owner and her team sharing a family meal at a long table in a warm dining room before service, candid laughter, aprons on, late afternoon light.",
    "services-hero": "A restaurant owner and a consultant walking through a modern upscale dining room before service, reviewing plans on a tablet, charcoal walls, brass pendant lights.",
    "services-detail": "Flat lay on a dark walnut table: fabric and wood finish swatches, a folded chef coat, a hand-drawn restaurant floor plan, a tablet showing a calendar, and an espresso cup, warm light from above.",
    "software-hero": "A host at a modern restaurant host stand using a tablet, the evening dining room softly blurred behind her, warm pendant light, guests arriving.",
    "software-detail": "Close-up of a server's hands holding a tablet beside a set table in an upscale restaurant, candlelight and dining room bokeh behind.",
    "ai-hero": "A restaurant manager in a small office behind the dining room looking at a laptop with charts, warm desk lamp, evening, the kitchen pass glowing through an interior window.",
    "ai-detail": "A smartphone lying on a polished wooden bar top with a chat conversation glowing on screen (no legible words), blurred bottles and warm bar lighting behind.",
    "training-hero": "A friendly trainer coaching two new restaurant servers at a dining table with a tablet before service, bright natural window light, black aprons, encouraging mood.",
    "training-detail": "A chef demonstrating plating technique to a young line cook in a clean professional kitchen, stainless steel and warm light, both focused on the plate.",
    "marketing-hero": "Overhead view of beautifully plated dishes on a dark table while a hand photographs them with a phone, warm natural light, linen napkins, a glass of wine.",
    "marketing-detail": "A lively restaurant patio at golden hour full of guests dining under warm string lights, plants and brick, inviting atmosphere.",
    "scheduling-hero": "A restaurant general manager sitting at the bar after close reviewing a weekly schedule on a laptop, chairs up on tables, dim warm lighting.",
    "scheduling-detail": "A restaurant pre-shift meeting: servers and cooks in black aprons gathered in the dining room listening to a manager, morning light through tall windows.",
    "furniture-hero": "A newly finished upscale restaurant dining room with custom walnut tables, leather banquettes, brass pendant lights and a long bar, no people, warm evening light.",
    "furniture-detail": "Furniture samples on a restaurant table: wood finish blocks, leather and fabric swatches, a chair leg sample and a rolled floor plan, warm side light.",
    "uniforms-hero": "A restaurant team standing together in coordinated uniforms in a modern dining room: servers in charcoal shirts and leather aprons, a chef in a white coat, a bartender in a vest, natural light.",
    "uniforms-detail": "Neatly folded chef coats, black bistro aprons and charcoal server shirts on wooden shelves in a tidy staff room, warm light, fabric texture visible.",
    "operations-hero": "A busy restaurant kitchen pass during dinner service, a chef calling tickets while plates wait under heat lamps, motion blur, warm light.",
    "operations-detail": "A restaurant owner at a quiet corner table reviewing printed reports and a menu with a calculator and coffee, morning light.",
    "multilocation-hero": "A city street at dusk lined with several glowing restaurant storefronts with warm interiors, people on the sidewalk, no readable signs.",
    "multilocation-detail": "A regional manager with a tablet walking through a newly opened restaurant while staff in matching uniforms set tables, bright and organized.",
    "about-hero": "A monarch butterfly resting on a patio screen at dawn, soft golden sunrise light, gentle bokeh of palm fronds and water in the background.",
    "casestudy-hero": "A snowy mountain village at dusk with warm glowing windows and evergreen trees, upscale alpine evening, no readable signs.",
    "casestudy-detail": "An elegant private dining room with a long wood table set for dinner, a stone fireplace, candlelight, mountain lodge style, no people.",
    "assessment-hero": "A restaurant owner at the bar counter reading a report on a tablet with a coffee, morning before opening, warm light through the windows.",
    "contact-hero": "A restaurant entrance at dusk with warm light spilling out of large front windows onto the sidewalk, inviting, no readable signage.",
    "blog-hero": "Overhead view of a restaurant owner's desk with an open notebook, coffee, menu drafts, a pen and a tablet, warm morning light.",
}


def gemini_image(prompt, key):
    api_key = os.environ["GEMINI_API_KEY"]
    last_err = None
    for model in MODELS:
        if model in DEAD:
            continue
        image_config = {"aspectRatio": "16:9"}
        if model.startswith(("gemini-3-pro", "nano-banana-pro")):
            image_config["imageSize"] = "2K"  # pro models only; the flash models reject it
        body = {
            "contents": [{"parts": [{"text": f"{STYLE}\n\nScene: {prompt}"}]}],
            "generationConfig": {
                "responseModalities": ["IMAGE"],
                "imageConfig": image_config,
            },
        }
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        req = urllib.request.Request(url, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                data = json.loads(r.read())
        except urllib.error.HTTPError as e:
            msg = e.read()[:300].decode(errors="replace")
            if e.code == 404 or "deprecat" in msg.lower() or "not found" in msg.lower():
                DEAD.add(model)
            last_err = f"{model}: HTTP {e.code} {msg}"
            continue
        except Exception as e:  # network hiccup, try the next model
            last_err = f"{model}: {e}"
            continue
        for cand in data.get("candidates", []):
            for part in cand.get("content", {}).get("parts", []):
                inline = part.get("inlineData") or part.get("inline_data")
                if inline:
                    return base64.b64decode(inline["data"]), model
        last_err = f"{model}: no image in response {json.dumps(data)[:200]}"
    raise RuntimeError(last_err or "no models available")


def save(key, raw):
    with open(os.path.join(SRC, f"{key}.png"), "wb") as fh:
        fh.write(raw)
    img = Image.open(io.BytesIO(raw)).convert("RGB")
    w, h = img.size
    # Normalize to 16:9 by center crop, then size for the web.
    target = 16 / 9
    if abs(w / h - target) > 0.01:
        if w / h > target:
            nw = int(h * target)
            img = img.crop(((w - nw) // 2, 0, (w - nw) // 2 + nw, h))
        else:
            nh = int(w / target)
            img = img.crop((0, (h - nh) // 2, w, (h - nh) // 2 + nh))
    web = img.resize((1600, 900), Image.LANCZOS) if img.size[0] > 1600 else img
    web.save(os.path.join(OUT, f"{key}.webp"), "WEBP", quality=78, method=6)
    og = img.resize((1200, 675), Image.LANCZOS).crop((0, 22, 1200, 652))
    og.save(os.path.join(OG, f"{key}.jpg"), "JPEG", quality=82, optimize=True, progressive=True)
    return img.size


def blog_manifest():
    manifest = {}
    bdir = os.path.join(ROOT, "_build", "content", "blog")
    for f in sorted(os.listdir(bdir)):
        if not f.endswith(".md"):
            continue
        text = open(os.path.join(bdir, f), encoding="utf-8").read()
        m = re.search(r'^image_prompt:\s*"?(.*?)"?\s*$', text, re.M)
        if m:
            manifest[f"blog-{f[:-3]}"] = m.group(1)
    return manifest


def main(argv):
    which = argv[0] if argv else "pages"
    force = set(argv[argv.index("--force") + 1:]) if "--force" in argv else set()
    manifest = PAGES if which == "pages" else blog_manifest()
    todo = {k: v for k, v in manifest.items()
            if k in force or not os.path.exists(os.path.join(OUT, f"{k}.webp"))}
    print(f"{len(todo)} image(s) to generate ({len(manifest)} in manifest)", flush=True)

    def work(item):
        key, prompt = item
        for attempt in range(3):
            try:
                raw, model = gemini_image(prompt, key)
                size = save(key, raw)
                return f"OK   {key} ({model}, {size[0]}x{size[1]})"
            except Exception as e:
                err = str(e)
                time.sleep(4 * (attempt + 1))
        return f"FAIL {key}: {err[:200]}"

    with cf.ThreadPoolExecutor(max_workers=4) as pool:
        for line in pool.map(work, todo.items()):
            print(line, flush=True)


if __name__ == "__main__":
    main(sys.argv[1:])
