"""Dev check: verify every local asset reference resolves, and list orphans.

Run from the repo root:  python check-assets.py
Requires: pip install pillow  (only for the dimension report)
"""
import io
import json
import os
import re

SEP = chr(92)  # backslash, written this way so shell heredocs can't mangle it

ORIGINS = ("https://inoxtv.com/", "http://inoxtv.com/")

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
    refs.setdefault(p.lstrip("/"), set()).add(where)


for f in ("index.html", "privacy.html"):
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

s = io.open("style.css", encoding="utf-8").read()
for m in re.findall(r'url\(\s*[\'"]?([^\'")]+)', s):
    add(m, "style.css")

for ic in json.load(open("manifest.json"))["icons"]:
    add(ic["src"], "manifest.json")

missing = []
ok = 0
for p, where in sorted(refs.items()):
    if os.path.exists(p):
        ok += 1
    else:
        missing.append((p, sorted(where)))

print("local asset references resolved: %d" % ok)
if missing:
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
