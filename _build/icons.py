"""Icons from the WES icon library (Desktop/Websites/icon-library/icons/icons.js).

Never hand-draw icons. Call icon("calendar") to get the library SVG, optionally
with a CSS class and pixel size.
"""
import os
import re

LIB = os.path.expanduser("~/Desktop/Websites/icon-library/icons/icons.js")
_PATTERN = re.compile(
    r"(?:'([a-z0-9-]+)'|([a-z0-9-]+))\s*:\s*\{\s*category:\s*'[^']*',\s*svg:\s*`(.*?)`",
    re.S,
)
_ICONS = {}


def _load():
    if _ICONS:
        return
    with open(LIB, encoding="utf-8") as fh:
        text = fh.read()
    for quoted, bare, svg in _PATTERN.findall(text):
        _ICONS[quoted or bare] = svg.strip()


def names():
    _load()
    return sorted(_ICONS)


def icon(name, cls="", size=None):
    _load()
    if name not in _ICONS:
        raise KeyError(f"icon '{name}' is not in the icon library")
    svg = _ICONS[name]
    attrs = ' aria-hidden="true" focusable="false"'
    if cls:
        attrs += f' class="{cls}"'
    if size:
        attrs += f' width="{size}" height="{size}"'
    return svg.replace("<svg ", f"<svg{attrs} ", 1)
