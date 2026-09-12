"""Dev check: verify every local asset reference resolves, and list orphans.

Run from the repo root:  python check-assets.py

Scans the rendered pages -- the hand-written ones at the root and every
<slug>/index.html build.py generates -- so a diagram or screenshot referenced
only by a generated page is checked too. There is no build step on the host, so
an unresolved reference here is a 404 in production.
"""
import io
import json
import os
import re
from pathlib import Path

SEP = chr(92)  # backslash, written this way so shell heredocs can't mangle it

ORIGINS = ("https://inoxtv.com/", "http://inoxtv.com/")

# Not rendered pages: _content/ holds fragments, _layouts/ and _partials/ hold
# templates whose placeholders are not real paths, and the diagram preview is a
# local contact sheet that is never linked from the site.
SKIP_PARTS = {"content", "_layouts", "_partials", ".git", ".claude", "node_modules"}
SKIP_FILES = {"images/diagrams/preview.html"}

refs = {}


def add(p, where):
    p = p.split("?")[0].split("#")[0].strip()
    # og:image / twitter:image / JSON-LD reference assets by absolute URL.
    # Rewrite same-origin URLs to local paths so they are checked too.
    for o in ORIGINS:
        if p.startswith(o):
            p = p[len(o):]
            break
    if not p or p.startswith(("http:", "https:", "data:", "mailto:", "//", "#")):
        return
    p = p.lstrip("/")
    # "/" is the home link on every page. Stripping the slash leaves an empty
    # string, which then reads as a missing file; it is served by index.html.
    refs.setdefault(p or "index.html", set()).add(where)


def pages():
    for path in sorted(Path(".").rglob("*.html")):
        rel = path.as_posix()
        if SKIP_PARTS & set(path.parts) or rel in SKIP_FILES:
            continue
        yield rel


page_count = 0
for f in pages():
    page_count += 1
    s = io.open(f, encoding="utf-8").read()
    for pat in (
        r'src="([^"]+)"',
        r'srcset="([^"]+)"',
        r'href="([^"]+)"',
        r'content="(https?://[^"]+\.(?:png|jpg|jpeg|webp|ico|svg))"',  # og/twitter images
        r'"logo":\s*"([^"]+)"',                                        # JSON-LD
    ):
        for m in re.findall(pat, s):
            for part in m.split(","):
                add(part.strip().split(" ")[0], f)

for css in sorted(Path(".").glob("*.css")):
    s = io.open(css, encoding="utf-8").read()
    for m in re.findall(r'url\(\s*[\'"]?([^\'")]+)', s):
        add(m, css.name)

for ic in json.load(open("manifest.json"))["icons"]:
    add(ic["src"], "manifest.json")

print("pages scanned: %d" % page_count)

missing = []
ok = 0
for p, where in sorted(refs.items()):
    if os.path.exists(p):
        ok += 1
    else:
        missing.append((p, sorted(where)))

print("local references resolved: %d" % ok)
if missing:
    # Directory references (a trailing slash) only resolve once build.py has
    # written that page, so a run before the build reports those as missing.
    print("\nMISSING (%d):" % len(missing))
    for p, w in missing:
        print("  %-50s referenced by %s" % (p, ", ".join(w)))
else:
    print("MISSING: none")

on_disk = set()
for root, _, files in os.walk("images"):
    for fn in files:
        on_disk.add(os.path.join(root, fn).replace(SEP, "/"))

orphans = sorted(on_disk - set(refs))
print(
    "\nimage files on disk: %d   referenced: %d   unreferenced: %d"
    % (len(on_disk), len(on_disk & set(refs)), len(orphans))
)
tot = 0
for p in orphans:
    kb = os.path.getsize(p) // 1024
    tot += kb
    print("  %-46s %6d KB" % (p, kb))
if orphans:
    print("  %-46s %6d KB total" % ("", tot))
