"""One-off: generate .webp alongside the .png images in images/.

Run from the repo root:  python convert-webp.py
Requires: pip install pillow

Preserves alpha (RGBA) so transparent logos/icons don't get black boxes.
Skips images that must stay PNG (see SKIP).
Does not modify the PNGs or the HTML -- it only writes .webp siblings.
"""
from pathlib import Path

from PIL import Image

# These are fetched directly by URL, never through a <picture> element, so a
# .webp sibling would just be dead weight:
#   og-image.png  - superseded by og-image.jpg; social scrapers don't reliably
#                   render WebP link previews.
#   icon-*.png    - manifest.json declares them as "type": "image/png".
# NOTE mobile-icon.png / tv-icon.png are deliberately NOT skipped: they serve
# double duty as manifest icons AND inside <picture> in index.html, so their
# .webp siblings are load-bearing.
SKIP = {
    "og-image.png",
    "icon-512.png",
    "icon-maskable-512.png",
}

total_png = total_webp = 0

for png in sorted(Path("images").rglob("*.png")):
    if png.name in SKIP:
        print(f"skip  {png}")
        continue

    im = Image.open(png)
    # Keep the alpha channel when there is one; RGB would flatten it to black.
    im = im.convert("RGBA" if im.mode in ("RGBA", "LA", "P") else "RGB")

    webp = png.with_suffix(".webp")
    im.save(webp, "WEBP", quality=82, method=6)

    png_kb = png.stat().st_size // 1024
    webp_kb = webp.stat().st_size // 1024
    saved = 100 - round(webp_kb / png_kb * 100) if png_kb else 0
    total_png += png_kb
    total_webp += webp_kb
    print(f"{png}  {png_kb} KB -> {webp_kb} KB  (-{saved}%)  mode={im.mode}")

if total_png:
    pct = 100 - round(total_webp / total_png * 100)
    print(f"\ntotal  {total_png} KB -> {total_webp} KB  (-{pct}%)")
print("\nPNGs untouched. Update markup to <picture> before this changes anything.")
