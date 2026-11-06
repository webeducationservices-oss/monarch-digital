#!/usr/bin/env python3
"""Copy linter for Monarch Digital content.

Usage:
  python3 _build/lint_copy.py <file> [<file> ...]
  python3 _build/lint_copy.py --all

Exits 1 when any ERROR is found. WARN lines need a human look but do not fail.
Checks house style: no em or en dashes, no banned AI phrasing, American spelling,
no emojis, no names that must stay private, and the brand name.
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ERROR_PATTERNS = [
    (r"[—–]", "em or en dash (restructure the sentence; no dashes)"),
    (r"&mdash;|&ndash;|&#8212;|&#8211;", "dash entity"),
    (r"\s--\s", "double hyphen used as a dash"),
    (r"\bhonest(ly)?\b", "banned word: honest/honestly"),
    (r"\belevat(e|es|ed|ing)\b", "banned word: elevate"),
    (r"\bseamless(ly)?\b", "banned word: seamless"),
    (r"\bjourney\b", "banned word: journey"),
    (r"\btruly\b", "banned word: truly"),
    (r"here'?s the (thing|secret)", "banned phrase"),
    (r"\bthe truth is\b", "banned phrase"),
    (r"\breason enough\b", "banned phrase"),
    (r"\bno surprises\b", "banned phrase"),
    (r"that'?s a wrap", "banned phrase"),
    (r"\bstart here\b", "banned phrase"),
    (r"\bready to [a-z]+[^.!?\n]*\?", "banned 'ready to...?' question"),
    (r"\bthe best part of\b", "banned phrase"),
    (r"\bworth naming\b|deserves its own mention", "banned phrase"),
    (r"\bmore than just\b", "banned 'more than just' framing"),
    (r"\bnot just\b", "banned 'not just' framing"),
    (r"\bit isn'?t [^.]{1,40}, it'?s\b", "banned 'it isn't X, it's Y' framing"),
    (r"\bless about\b[^.]{1,60}\bmore about\b", "banned 'less about / more about' framing"),
    (r"\bdelve\b|\btapestry\b|\btestament to\b", "AI tell word"),
    (r"\bgame[- ]chang", "AI tell word: game changer"),
    (r"\bunleash\b|\bsupercharg", "AI tell word"),
    (r"in today'?s (fast[- ]paced|digital|competitive)", "AI tell phrase"),
    (r"\bnavigat(e|ing) the (complex|ever)", "AI tell phrase"),
    (r"\bever[- ]evolving\b|\bever[- ]changing landscape\b", "AI tell phrase"),
    (r"\b(colour|favour|behaviour|honour|labour|centre|metre|theatre|catalogue|analyse|licence)\b", "British spelling"),
    (r"\b(organis|optimis|prioritis|customis|recognis|realis|specialis|standardis|minimis|maximis|utilis|emphasis(?!ed\b)|summaris|apologis|personalis|finalis|categoris|digitalis)(e|es|ed|ing|ation)\b", "British -ise spelling"),
    (r"Monarch Digital Marketing", "old brand name; use Monarch Digital"),
    (r"Web Education Services|\bWES\b|myaieditor|My AI Editor|\bLaunchpad\b", "partner or product name must not appear"),
    (r"[\U0001F300-\U0001FAFF☀-➿\U0001F000-\U0001F2FF]", "emoji"),
]

WARN_PATTERNS = [
    (r", not [a-z]", "possible 'X, not Y' framing; rephrase as a positive statement"),
    (r"\bnot [^.,;]{1,40} but\b", "possible 'not X but Y' framing"),
    (r"\b62\b", "the number 62 appears; make sure it is not a reference to the client"),
    (r"!", "exclamation mark; keep them rare"),
    (r":\s*[A-Z][a-z]+\.\s*$", "possible colon reveal"),
    (r"\bunlock\b|\blandscape\b|\brobust\b|\bcutting[- ]edge\b|\brevolution", "stock marketing word; consider plainer wording"),
    (r"\bToast\b[^.]{0,60}\b(integrat|sync|connect)", "Toast plus integration claim; the work runs alongside the POS, do not claim a data integration"),
]


# Names that must never appear in public copy live in a local, untracked file
# (_build/private_terms.txt, one regex per line) so this public repo never lists them.
PRIVATE_TERMS = os.path.join(ROOT, "_build", "private_terms.txt")
if os.path.exists(PRIVATE_TERMS):
    for _term in open(PRIVATE_TERMS, encoding="utf-8").read().splitlines():
        if _term.strip() and not _term.startswith("#"):
            ERROR_PATTERNS.append((_term.strip(), "private name"))


def strip_markup(text):
    # Ignore URLs, HTML attributes and front-matter keys that legitimately hold symbols.
    text = re.sub(r"https?://\S+", " ", text)
    text = re.sub(r'href="[^"]*"', " ", text)
    text = re.sub(r'"(icon|media|mockup|href|key|slug|image_prompt)"\s*:\s*"[^"]*"', " ", text)
    return text


def lint_file(path):
    errors = warns = 0
    with open(path, encoding="utf-8") as fh:
        lines = fh.read().splitlines()
    for i, raw in enumerate(lines, 1):
        line = strip_markup(raw)
        for pat, msg in ERROR_PATTERNS:
            flags = 0 if pat.startswith("Monarch") or msg == "private name" else re.IGNORECASE
            if re.search(pat, line, flags):
                print(f"ERROR {os.path.relpath(path, ROOT)}:{i}: {msg}: {raw.strip()[:140]}")
                errors += 1
        for pat, msg in WARN_PATTERNS:
            if re.search(pat, line):
                print(f"WARN  {os.path.relpath(path, ROOT)}:{i}: {msg}: {raw.strip()[:140]}")
                warns += 1
    return errors, warns


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    files = []
    if argv == ["--all"]:
        for sub in ("_build/content/pages", "_build/content/blog"):
            d = os.path.join(ROOT, sub)
            if os.path.isdir(d):
                files += [os.path.join(d, f) for f in sorted(os.listdir(d)) if f.endswith((".json", ".md"))]
    else:
        files = [os.path.abspath(a) for a in argv]
    total_e = total_w = 0
    for f in files:
        e, w = lint_file(f)
        total_e += e
        total_w += w
    print(f"\n{len(files)} file(s): {total_e} error(s), {total_w} warning(s)")
    return 1 if total_e else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
