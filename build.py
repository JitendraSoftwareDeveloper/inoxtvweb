#!/usr/bin/env python3
"""Static site builder for inoxtv.com.

Renders every fragment in _content/ through _layouts/ and _partials/ into a
committed <slug>/index.html, and regenerates the navigation, section hubs,
breadcrumbs, table of contents, structured data and sitemap.xml from one
registry so none of them can drift as pages are added.

Adding a page is one new file in _content/<section>/ plus a rebuild. Nothing
else needs touching.

Site search is off until "cse_id" in _data/site.json holds a hosted search
engine id. With it set, the next build adds /search/, a field in the masthead
and on every hub, and a footer link; with it empty none of those are written,
so a search box that cannot answer anything never reaches the site.

    python build.py            build, then print a report
    python build.py --clean    delete previously generated output first
    python build.py --strict   exit 1 if anything was reported

Standard library only: GitHub Pages has no build step, so the output is
committed and the build runs locally.
"""

from __future__ import annotations

import argparse
import html
import json
import os
import re
import shutil
import sys
from datetime import date, datetime
from urllib.parse import quote

ROOT = os.path.dirname(os.path.abspath(__file__))
# Underscore-prefixed on purpose. GitHub Pages runs Jekyll (there is no
# .nojekyll), and Jekyll never copies a "_" directory into the served output.
# Without the underscore every fragment in here is published as a second,
# chrome-less copy of an article it already renders - 31 duplicate URLs with no
# nav and no canonical, which is the "low-value content" shape the programme
# policies refuse. Renaming this back would republish all of them.
CONTENT = os.path.join(ROOT, "_content")
# Orientation text for each section hub, one file per section, named after the
# section key. Kept out of _content because discover() treats every .html there
# as an article: these carry no front matter and are not pages of their own.
# A hub that is only a breadcrumb, a lede and a grid of link cards is the
# "screen used for navigation" the inventory rules name, so each one needs
# something worth reading on it. See HUB_WORD_FLOOR.
HUBS = os.path.join(ROOT, "_hubs")
LAYOUTS = os.path.join(ROOT, "_layouts")
PARTIALS = os.path.join(ROOT, "_partials")
DATA = os.path.join(ROOT, "_data")
MANIFEST = os.path.join(ROOT, "_data", "build-manifest.json")

# Hand-written pages the builder must never touch or overwrite. privacy.html
# is load-bearing: the shipped app opens https://inoxtv.com/privacy.html from
# settings_about_privacy_policy_url, old installs will request that exact path
# forever, and GitHub Pages cannot issue a redirect.
PROTECTED = {"index.html", "privacy.html"}

# Whether each hand-written page may load the ad script. They carry no section
# key, so carries_ads() cannot answer for them and the expectation is stated
# here instead; check_protected() reads this, so the two stay in step.
# privacy.html is False because its own §11 tells visitors advertising is never
# placed on it, and the automatic units fill any page that loads the loader.
PROTECTED_ADS = {"index.html": True, "privacy.html": False}

TITLE_MAX = 65
DESC_MIN, DESC_MAX = 120, 165

# Words a section hub has to carry in its own orientation text, measured with
# the link cards, breadcrumb and lede stripped out. About 330-530 in practice.
#
# The number is not the point. A hub whose only prose is one lede sentence is a
# list of links, and the inventory rules do not allow ads on "screens used for
# alerts, navigation or other behavioral purposes". This is a minimum that
# fails the build when a hub loses its content, not a target to pad towards -
# padding to hit a count is its own problem.
HUB_WORD_FLOOR = 250

MONTHS = ("January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December")

# Phrasing that reads as piracy-adjacent to a policy reviewer. Checked against
# the rendered page, not just the fragment, so a layout cannot smuggle it in.
#
# Every entry has to be unambiguous, because a false positive here trains
# whoever runs the build to ignore the warnings. Protocol names (M3U, Xtream
# Codes, Stalker Portal) are deliberately absent: those are formats the app
# reads, and naming a format is not naming a source. "crack" is absent for the
# same reason - audio crackles. So is "working playlist", which in these pages
# means a playlist that already works, not one being handed out.
BANNED = [
    "free iptv",
    "premium iptv",
    "iptv subscription",
    "free channels",
    "watch free tv",
    "free live tv",
    "unlimited channels",
    "thousands of channels",
    "no subscription needed",
    "no subscription required",
    "free playlist",
    "playlist link below",
    "playlist we provide",
    "bypass geo",
    # "bypass" on its own is deliberately not listed: the terms page forbids
    # users from circumventing restrictions, which is the opposite of the
    # problem. What has to stay out is the phrasing that presents a route
    # around a store's device list as the point of the page rather than a
    # consequence of it.
    "bypass the filter",
    "bypasses the filter",
    "circumvent the",
    "unblock channels",
    "cracked apk",
    "cracked version",
    "torrent",
    "pirated",
]

# Phrasing that reads as machine-written. Separate from BANNED because the
# consequence is different: BANNED is a policy problem that can get the site
# refused outright, this is a quality signal that makes a reviewer read the
# pages as low-value filler rather than documentation someone wrote.
#
# The test for an entry is whether a developer writing about their own app
# would ever reach for it. "Comprehensive" and "robust" describe a product
# being sold; "seamless" and "effortless" are claims a user makes, not a
# manual. Domain words that merely look similar stay out: "unlock" is the
# parental PIN, "boost" is not used, and "leverage" would be wrong in any
# sentence on this site anyway.
TELLS = [
    "delve",
    "seamless",
    "effortless",
    "robust",
    "comprehensive",
    "leverage",
    "elevate your",
    "empower",
    "streamline",
    "cutting-edge",
    "game-changer",
    "game changer",
    "state-of-the-art",
    "revolutionize",
    "revolutionise",
    "dive into",
    "deep dive",
    "embark on",
    "a testament to",
    "the realm of",
    "unleash",
    "myriad",
    "plethora",
    "in today's",
    "look no further",
    "rest assured",
    "it's worth noting",
    "it is worth noting",
    "at the end of the day",
    "when it comes to",
    "in conclusion",
    "to sum up",
    "let's explore",
    "we'll explore",
    "by following these steps",
    "whether you're a",
    "not just a",
    "not only that",
]

# Em-dashes per thousand words, above which a page is flagged. The mark itself
# is fine - it does real work in a "label - definition" list row, and those are
# excluded from the count. What reads as machine-written is the habit of
# appending an explanatory clause to sentence after sentence with one, which is
# what this catches. The floor was set after the 2026-09-13 sweep took the
# prose count to zero; anything above it means the habit is returning.
TELL_DASH_RATE = 3.0


# --------------------------------------------------------------------------
# small helpers
# --------------------------------------------------------------------------

def read(path: str) -> str:
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def write(path: str, text: str) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


def load_json(path: str, default=None):
    if not os.path.exists(path):
        return default
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def human_date(iso: str) -> str:
    """2026-09-07 -> 7 September 2026. Assembled by hand because the strftime
    code for an unpadded day differs between platforms."""
    try:
        dt = datetime.strptime(iso, "%Y-%m-%d")
    except ValueError:
        return iso
    return "%d %s %d" % (dt.day, MONTHS[dt.month - 1], dt.year)


def strip_tags(markup: str) -> str:
    text = re.sub(r"<script\b.*?</script>", " ", markup, flags=re.S | re.I)
    text = re.sub(r"<style\b.*?</style>", " ", text, flags=re.S | re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    return html.unescape(re.sub(r"\s+", " ", text)).strip()


def word_count(markup: str) -> int:
    return len(strip_tags(markup).split())


def jsonld_block(*objects) -> str:
    """Serialise structured data, escaping < so it cannot close the script."""
    out = []
    for obj in objects:
        if not obj:
            continue
        payload = json.dumps(obj, ensure_ascii=False, indent=2)
        payload = payload.replace("<", "\\u003c").replace("&", "\\u0026")
        out.append('<script type="application/ld+json">\n%s\n</script>' % payload)
    return "\n".join(out)


# --------------------------------------------------------------------------
# templating: {{ key }} substitution plus {% include partial %}
# --------------------------------------------------------------------------

INCLUDE_RE = re.compile(r"[ \t]*\{%\s*include\s+([\w-]+)\s*%\}")
TOKEN_RE = re.compile(r"\{\{\s*([\w_]+)\s*\}\}")


class Templates:
    def __init__(self) -> None:
        self._cache: dict[str, str] = {}

    def _load(self, kind: str, name: str) -> str:
        key = "%s/%s" % (kind, name)
        if key not in self._cache:
            base = LAYOUTS if kind == "layout" else PARTIALS
            self._cache[key] = read(os.path.join(base, name + ".html"))
        return self._cache[key]

    def render(self, kind: str, name: str, ctx: dict) -> str:
        text = self._load(kind, name)
        # Includes first, so a partial's own tokens resolve in the same pass.
        for _ in range(4):
            new = INCLUDE_RE.sub(lambda m: self._load("partial", m.group(1)), text)
            if new == text:
                break
            text = new
        return TOKEN_RE.sub(lambda m: str(ctx.get(m.group(1), "")), text)


# --------------------------------------------------------------------------
# front matter
# --------------------------------------------------------------------------

FRONT_RE = re.compile(r"^\s*<!--\s*(\{.*?\})\s*-->", re.S)


def parse_fragment(path: str) -> tuple[dict, str]:
    raw = read(path)
    match = FRONT_RE.match(raw)
    if not match:
        raise ValueError("%s: no JSON front matter in a leading HTML comment" % path)
    try:
        meta = json.loads(match.group(1))
    except json.JSONDecodeError as exc:
        raise ValueError("%s: front matter is not valid JSON (%s)" % (path, exc)) from exc
    return meta, raw[match.end():].strip()


# --------------------------------------------------------------------------
# page assembly
# --------------------------------------------------------------------------

H2_RE = re.compile(r'<h2\s+id="([^"]+)"[^>]*>(.*?)</h2>', re.S | re.I)


def headings(body: str) -> list[tuple[str, str]]:
    return [(hid, strip_tags(text)) for hid, text in H2_RE.findall(body)]


def build_toc(items: list[tuple[str, str]]) -> str:
    if len(items) < 3:
        return ""
        # Fewer than three sections is a page you read straight through.
    rows = "\n".join(
        '          <li><a href="#%s">%s</a></li>' % (hid, html.escape(text))
        for hid, text in items
    )
    return (
        '      <nav class="toc" aria-labelledby="toc-h">\n'
        '        <p class="toc-h" id="toc-h">On this page</p>\n'
        "        <ol>\n%s\n        </ol>\n"
        "      </nav>" % rows
    )


def insert_ads(body: str, ads_html: str) -> str:
    """Place at most two in-article slots, both well clear of any CTA.

    Slots go immediately before an <h2>, never inside a list, table or figure,
    so a slot can never land between a step and its screenshot. Two visible at
    once on a phone would breach the placement rules, so the second slot needs
    at least three sections of separation.
    """
    if not ads_html:
        return body
    starts = [m.start() for m in re.finditer(r"<h2\s", body, re.I)]
    if len(starts) < 3:
        return body
    picks = [starts[1]]
    if len(starts) >= 6:
        picks.append(starts[len(starts) // 2 + 1])
    out = []
    prev = 0
    for pos in picks:
        out.append(body[prev:pos])
        out.append(ads_html)
        prev = pos
    out.append(body[prev:])
    return "".join(out)


def breadcrumbs_html(trail: list[tuple[str, str]]) -> str:
    parts = []
    for idx, (label, url) in enumerate(trail):
        last = idx == len(trail) - 1
        if last:
            parts.append('<li aria-current="page">%s</li>' % html.escape(label))
        else:
            parts.append('<li><a href="%s">%s</a></li>' % (url, html.escape(label)))
    return (
        '    <nav class="crumbs" aria-label="Breadcrumb">\n      <ol>%s</ol>\n    </nav>'
        % "".join(parts)
    )


def related_html(meta: dict, registry: dict, warn) -> str:
    slugs = meta.get("related") or []
    cards = []
    for slug in slugs:
        target = registry.get(slug.strip("/"))
        if not target:
            warn("%s: related slug '%s' does not exist" % (meta["slug"], slug))
            continue
        cards.append(
            '        <li><a href="%s"><span class="rel-sec">%s</span>'
            '<span class="rel-title">%s</span></a></li>'
            % (target["url"], html.escape(target["section_title"]), html.escape(target["h1"]))
        )
    if not cards:
        return ""
    return (
        '        <section class="related" aria-labelledby="related-h">\n'
        '          <h2 id="related-h">Related pages</h2>\n'
        "          <ul>\n%s\n          </ul>\n        </section>" % "\n".join(cards)
    )


class Builder:
    def __init__(self, site: dict, strict: bool) -> None:
        self.site = site
        self.strict = strict
        self.tpl = Templates()
        self.pages: list[dict] = []
        self.registry: dict[str, dict] = {}
        self.written: list[str] = []
        self.warnings: list[str] = []
        self.hubs = 0
        self.base = site["base_url"].rstrip("/")

    def warn(self, message: str) -> None:
        self.warnings.append(message)

    # -- discovery ---------------------------------------------------------

    def discover(self) -> None:
        if not os.path.isdir(CONTENT):
            raise SystemExit("_content/ not found")
        for dirpath, _dirs, files in os.walk(CONTENT):
            for name in sorted(files):
                if not name.endswith(".html"):
                    continue
                path = os.path.join(dirpath, name)
                meta, body = parse_fragment(path)
                for field in ("title", "h1", "description", "section", "slug", "updated"):
                    if not meta.get(field):
                        raise ValueError("%s: front matter is missing '%s'" % (path, field))
                if meta["section"] not in self.site["sections"]:
                    raise ValueError(
                        "%s: unknown section '%s'" % (path, meta["section"])
                    )
                section = self.site["sections"][meta["section"]]
                slug = meta["slug"].strip("/")
                page = {
                    "meta": meta,
                    "body": body,
                    "source": os.path.relpath(path, ROOT).replace("\\", "/"),
                    "slug": slug,
                    "url": "/" + slug + "/",
                    "h1": meta["h1"],
                    "section": meta["section"],
                    "section_title": section["title"],
                    "words": word_count(body),
                }
                if slug in self.registry:
                    raise ValueError("duplicate slug '%s'" % slug)
                self.registry[slug] = page
                self.pages.append(page)
        self.pages.sort(key=lambda p: (p["section"], p["meta"].get("order", 99), p["slug"]))

    # -- chrome ------------------------------------------------------------

    def nav_links(self, current: str) -> str:
        rows = []
        for item in self.site["nav"]:
            classes = []
            if item.get("cta"):
                classes.append("nav-cta")
            if current and item["url"].strip("/") == current:
                classes.append("is-current")
            attr = ' class="%s"' % " ".join(classes) if classes else ""
            aria = ' aria-current="page"' if "is-current" in classes else ""
            rows.append(
                '        <li><a href="%s"%s%s>%s</a></li>'
                % (item["url"], attr, aria, html.escape(item["label"]))
            )
        return "\n".join(rows)

    def footer_columns(self) -> str:
        blocks = []
        for col in self.site["footer_columns"]:
            links = "\n".join(
                '          <li><a href="%s">%s</a></li>' % (l["url"], html.escape(l["label"]))
                for l in col["links"]
                if l["url"] != "/search/" or self.search_on()
            )
            blocks.append(
                '      <div class="site-foot-col">\n'
                "        <h2>%s</h2>\n        <ul>\n%s\n        </ul>\n      </div>"
                % (html.escape(col["heading"]), links)
            )
        return "\n".join(blocks)

    def carries_ads(self, section_key: str, slug: str = "") -> bool:
        """Whether a page's <head> may load the ad script.

        One rule, read by both the renderer and audit(), so what the build emits
        and what it expects cannot drift apart.

        Policy pages and /search/ are excluded, and that exclusion is what makes
        privacy.html §11 true rather than aspirational: it promises visitors that
        no advertising is placed on the policy pages, and the automatic units
        fill any page that loads the loader. The policy section also has no
        publisher content of its own to sell - legal text, an about page and a
        contact page are not what the inventory rules call content.

        /search/ is excluded twice over: it is noindex, and a results page has
        nothing to offer an advertiser.
        """
        if section_key == "policy":
            return False
        if slug.startswith("search/") or slug.rstrip("/") == "search":
            return False
        return True

    def ad_slot_id(self, meta: dict) -> str:
        """The in-article unit's id, or empty while there is no real one.

        An <ins> with an empty data-ad-slot is broken ad code: the unit has no
        identity, so it can never fill, and a reviewer sees containers that
        render nothing. The id can only be created once the account is approved,
        so until then the head loader ships alone and placement is left to the
        automatic units, which need no id. Paste one into "ad_slot" and the next
        build puts the two in-article units back.
        """
        return str(meta.get("ad_slot") or self.site.get("ad_slot") or "").strip()

    def ads_html(self, meta: dict, section: dict) -> str:
        """In-article slots, or nothing at all on a page without publisher content."""
        if not section.get("ads") or meta.get("ads") is False:
            return ""
        slot = self.ad_slot_id(meta)
        if not slot:
            return ""
        return self.tpl.render(
            "partial",
            "ad-in-article",
            {"ads_client": self.site["ads_client"], "ad_slot": html.escape(slot, quote=True)},
        )

    # -- share -------------------------------------------------------------

    def share_links(self, canonical: str, h1: str, summary: str) -> dict:
        """Pre-built share targets for one page.

        Assembled here rather than in the browser for two reasons: every button
        stays a real link with scripting off, and each page shares its own
        address instead of whatever the script was told the site root is.
        """
        url = quote(canonical, safe="")
        headline = quote("InoxTV: " + h1, safe="")
        blurb = quote(summary, safe="")
        long_form = quote("%s\n\n%s" % (summary, canonical), safe="")
        targets = {
            "share_whatsapp": "https://wa.me/?text=" + long_form,
            "share_telegram": "https://t.me/share/url?url=%s&text=%s" % (url, blurb),
            "share_reddit": "https://www.reddit.com/submit?url=%s&title=%s" % (url, headline),
            "share_twitter": "https://twitter.com/intent/tweet?text=%s&url=%s" % (blurb, url),
            "share_facebook": "https://www.facebook.com/sharer/sharer.php?u=" + url,
            "share_linkedin": "https://www.linkedin.com/sharing/share-offsite/?url=" + url,
            "share_email": "mailto:?subject=%s&body=%s" % (headline, long_form),
        }
        return {key: html.escape(value, quote=True) for key, value in targets.items()}

    # -- report an error ---------------------------------------------------

    def report_mail(self, canonical: str, h1: str) -> str:
        """The mailto behind the report-an-error control on one page.

        Prefilled with the page it was pressed on. Without that, a good share
        of the corrections that arrive cannot be acted on, because nothing in
        the message says which of thirty-odd pages it describes.
        """
        subject = quote("Error on: " + h1, safe="")
        body = quote(
            "Page: %s\n\n"
            "What is wrong on this page:\n\n\n"
            "Device and app version, if it matters:\n\n" % canonical,
            safe="",
        )
        target = "mailto:%s?subject=%s&body=%s" % (
            self.site["support_email"],
            subject,
            body,
        )
        return html.escape(target, quote=True)

    def report_band(self, canonical: str, h1: str, variant: str = "default") -> str:
        copy = self.site["report_copy"][variant]
        return self.tpl.render(
            "partial",
            "page-report",
            {
                "report_h": html.escape(copy["heading"]),
                "report_sub": copy["sub"],
                "report_mail": self.report_mail(canonical, h1),
                "support_email": self.site["support_email"],
            },
        )

    # -- search ------------------------------------------------------------

    SEARCH_ICON = (
        '<svg viewBox="0 0 24 24" width="17" height="17" aria-hidden="true" fill="none"'
        ' stroke="currentColor" stroke-width="2" stroke-linecap="round">'
        '<circle cx="11" cy="11" r="7"></circle><path d="M20 20l-4.3-4.3"></path></svg>'
    )

    SEARCH_PLACEHOLDER = {
        "nav": "Search help",
        "hub": "Search every page: buffering, playlist, TV guide",
    }

    def search_on(self) -> bool:
        """Search ships only once a search engine id sits in _data/site.json.

        A box that returns nothing is worse than no box, so the field, the
        results page and the footer link are all built from this one flag.
        """
        return bool(str(self.site.get("cse_id") or "").strip())

    def search_form(self, variant: str) -> str:
        """A plain GET form aimed at /search/.

        Deliberately not the hosted search-box widget: that needs the search
        provider's script on all thirty-seven pages for a control most visitors
        never touch. A form needs no script at all, so search keeps working
        with JavaScript switched off and the third-party request happens on the
        results page only.
        """
        if not self.search_on():
            return ""
        field = "q-" + variant
        # One search landmark per page, and it is always the masthead one, so
        # landmark navigation lands in the same place everywhere. The hero form
        # on a hub submits to the same address and needs no second landmark.
        role = ' role="search"' if variant == "nav" else ""
        label = (
            '<span class="sr-only">Search</span>'
            if variant == "nav"
            else '<span class="site-search-go-label">Search</span>'
        )
        return (
            '<form class="site-search site-search--%s"%s'
            ' action="/search/" method="get">\n'
            '        <label class="sr-only" for="%s">Search the InoxTV help centre</label>\n'
            '        <input class="site-search-field" type="search" id="%s" name="q"'
            ' placeholder="%s" autocomplete="off" enterkeyhint="search">\n'
            '        <button class="site-search-go" type="submit">%s%s</button>\n'
            "      </form>"
            % (
                variant,
                role,
                field,
                field,
                html.escape(self.SEARCH_PLACEHOLDER[variant], quote=True),
                self.SEARCH_ICON,
                label,
            )
        )

    def cse_loader(self) -> str:
        if not self.search_on():
            return ""
        cx = html.escape(quote(str(self.site["cse_id"]).strip(), safe=":"), quote=True)
        return '<script async src="https://cse.google.com/cse.js?cx=%s"></script>' % cx

    # -- structured data ---------------------------------------------------

    def breadcrumb_ld(self, trail: list[tuple[str, str]]) -> dict:
        return {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": i + 1,
                    "name": label,
                    "item": self.base + url,
                }
                for i, (label, url) in enumerate(trail)
            ],
        }

    def article_ld(self, page: dict, canonical: str) -> dict:
        meta = page["meta"]
        return {
            "@context": "https://schema.org",
            "@type": "TechArticle",
            "headline": meta["h1"],
            "description": meta["description"],
            "url": canonical,
            "dateModified": meta["updated"],
            "inLanguage": "en",
            "isPartOf": {"@type": "WebSite", "name": "InoxTV", "url": self.base},
            "about": {
                "@type": "SoftwareApplication",
                "name": "InoxTV",
                "operatingSystem": "Android, Android TV",
                "applicationCategory": "MultimediaApplication",
            },
            "publisher": {"@type": "Organization", "name": "InoxTV", "url": self.base},
        }

    @staticmethod
    def howto_ld(meta: dict) -> dict | None:
        howto = meta.get("howto")
        if not howto:
            return None
        return {
            "@context": "https://schema.org",
            "@type": "HowTo",
            "name": howto["name"],
            "step": [
                {"@type": "HowToStep", "position": i + 1, "text": text}
                for i, text in enumerate(howto["steps"])
            ],
        }

    @staticmethod
    def faq_ld(meta: dict) -> dict | None:
        faq = meta.get("faq")
        if not faq:
            return None
        return {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": [
                {
                    "@type": "Question",
                    "name": item["q"],
                    "acceptedAnswer": {"@type": "Answer", "text": item["a"]},
                }
                for item in faq
            ],
        }

    def faq_markup(self, meta: dict) -> str:
        """Render the visible FAQ from the same data the schema uses.

        Markup and structured data disagreeing is a manual-action risk, so
        there is deliberately no way to write one without the other.
        """
        faq = meta.get("faq")
        if not faq:
            return ""
        items = "\n".join(
            "            <details>\n"
            "              <summary>%s</summary>\n"
            "              <div>%s</div>\n"
            "            </details>" % (html.escape(i["q"]), html.escape(i["a"]))
            for i in faq
        )
        return (
            '        <section class="faq" aria-labelledby="faq-h">\n'
            '          <h2 id="faq-h">Questions people ask</h2>\n'
            '          <div class="faq-list">\n%s\n          </div>\n        </section>'
            % items
        )

    # -- rendering ---------------------------------------------------------

    def shell(self, *, title, description, canonical, og_type, body_class,
              content, jsonld, current_section, share, report,
              robots="index, follow, max-image-preview:large, max-snippet:-1",
              cse=False, ads=True) -> str:
        # The loader goes in the head of every page that can show an ad, which is
        # how the site is verified and how automatic placements reach pages that
        # carry no hand-placed slot. Whether a page shows an ad is a separate
        # decision, made by ads_html().
        #
        # "ads=False" is not a soft preference, it is what keeps privacy.html
        # §11 honest: that section promises visitors no advertising on the policy
        # pages, and the automatic units fill any page that loads this script, so
        # leaving it there would make the promise depend on an account setting the
        # site cannot see. Absent from the head, the promise is true by
        # construction. Verified per page in audit().
        ads_loader = ""
        if ads:
            ads_loader = (
                '<script async src="https://pagead2.googlesyndication.com/pagead/js/'
                'adsbygoogle.js?client=%s" crossorigin="anonymous"></script>'
                % self.site["ads_client"]
            )
        return self.tpl.render(
            "layout",
            "base",
            {
                "title": html.escape(title, quote=True),
                "og_title": html.escape(title.split(" | ")[0], quote=True),
                "description": html.escape(description, quote=True),
                "canonical": canonical,
                "base_url": self.base,
                "og_type": og_type,
                "robots": robots,
                "body_class": body_class,
                "analytics_id": self.site["analytics_id"],
                "ads_loader": ads_loader,
                "cse_loader": self.cse_loader() if cse else "",
                "jsonld": jsonld,
                "nav_links": self.nav_links(current_section),
                "search_nav": self.search_form("nav"),
                "footer_columns": self.footer_columns(),
                "disclaimer": html.escape(self.site["disclaimer"]),
                "content": content,
                "page_report": report,
                **share,
            },
        )

    def render_page(self, page: dict) -> None:
        meta, body = page["meta"], page["body"]
        section = self.site["sections"][page["section"]]
        canonical = self.base + page["url"]
        is_policy = page["section"] == "policy"

        trail = [("Home", "/")]
        if not is_policy:
            trail.append((section["title"], "/%s/" % page["section"]))
        trail.append((meta["h1"], page["url"]))

        toc_items = headings(body)
        body_out = body
        faq = self.faq_markup(meta)
        if faq:
            body_out += "\n" + faq
            toc_items.append(("faq-h", "Questions people ask"))
        ads = self.ads_html(meta, section)
        body_out = insert_ads(body_out, ads)
        share = self.share_links(canonical, meta["h1"], meta["description"])

        rendered = self.tpl.render(
            "layout",
            "policy" if is_policy else "doc",
            {
                "breadcrumbs": breadcrumbs_html(trail),
                "section_title": html.escape(section["title"]),
                "h1": html.escape(meta["h1"]),
                "lede": meta.get("lede", meta["description"]),
                "updated": meta["updated"],
                "updated_human": human_date(meta["updated"]),
                "content": body_out,
                "related": related_html(meta, self.registry, self.warn),
                "toc": build_toc(toc_items),
                "disclaimer": html.escape(self.site["disclaimer"]),
            },
        )

        ld = jsonld_block(
            self.breadcrumb_ld(trail),
            {
                "@context": "https://schema.org",
                "@type": "WebPage",
                "name": meta["h1"],
                "description": meta["description"],
                "url": canonical,
                "dateModified": meta["updated"],
            }
            if is_policy
            else self.article_ld(page, canonical),
            self.howto_ld(meta),
            self.faq_ld(meta),
        )

        out = self.shell(
            title=meta["title"],
            description=meta["description"],
            canonical=canonical,
            og_type="article",
            body_class="page-doc" + (" page-policy" if is_policy else ""),
            content=rendered,
            jsonld=ld,
            current_section="" if is_policy else page["section"],
            share=share,
            report=self.report_band(canonical, meta["h1"]),
            ads=self.carries_ads(page["section"], page["slug"]),
        )
        self.emit(os.path.join(page["slug"], "index.html"), out)
        self.audit(page, out)

    def hub_intro(self, key: str, section: dict) -> str:
        """The orientation prose that sits above a hub's link cards.

        Read verbatim from _hubs/<section>.html and wrapped so it takes the
        article measure rather than the full page width. One file per section,
        so editing one hub cannot collide with another, and adding a page to a
        section never touches this.

        Returns empty for a section with no file, and warns rather than raising:
        a missing fragment should be visible in the build output, not fatal.
        """
        path = os.path.join(HUBS, "%s.html" % key)
        if not os.path.isfile(path):
            self.warn(
                "hub /%s/ has no orientation text (_hubs/%s.html): a page that "
                "is only links is a navigation screen" % (key, key)
            )
            return ""
        with open(path, encoding="utf-8") as fh:
            body = fh.read().strip()
        words = word_count(body)
        if words < HUB_WORD_FLOOR:
            self.warn(
                "hub /%s/: %d words of orientation text, floor is %d"
                % (key, words, HUB_WORD_FLOOR)
            )
        return '<div class="doc-body hub-intro">\n%s\n</div>' % body

    def render_hub(self, key: str, section: dict) -> None:
        url = "/%s/" % key
        canonical = self.base + url
        pages = [p for p in self.pages if p["section"] == key]
        groups = []
        seen = set()
        for group in section.get("groups", []):
            members = [p for p in pages if p["meta"].get("group") == group["id"]]
            if not members:
                continue
            seen.update(p["slug"] for p in members)
            groups.append(self.hub_group(group["heading"], group["id"], members))
        rest = [p for p in pages if p["slug"] not in seen]
        if rest:
            groups.append(self.hub_group("More", "more", rest))

        trail = [("Home", "/"), (section["title"], url)]
        intro = self.hub_intro(key, section)
        rendered = self.tpl.render(
            "layout",
            "hub",
            {
                "breadcrumbs": breadcrumbs_html(trail),
                "h1": html.escape(section["h1"]),
                "lede": section.get("lede", ""),
                "search_hero": self.search_form("hub"),
                "content": intro,
                "groups": "\n".join(groups),
                "disclaimer": html.escape(self.site["disclaimer"]),
            },
        )
        ld = jsonld_block(
            self.breadcrumb_ld(trail),
            {
                "@context": "https://schema.org",
                "@type": "CollectionPage",
                "name": section["h1"],
                "description": section["description"],
                "url": canonical,
                "isPartOf": {"@type": "WebSite", "name": "InoxTV", "url": self.base},
                "hasPart": [
                    {
                        "@type": "TechArticle",
                        "headline": p["h1"],
                        "url": self.base + p["url"],
                    }
                    for p in pages
                ],
            },
        )
        out = self.shell(
            title="%s | InoxTV" % section["title"],
            description=section["description"],
            canonical=canonical,
            og_type="website",
            body_class="page-hub",
            content=rendered,
            jsonld=ld,
            current_section=key,
            share=self.share_links(canonical, section["h1"], section["description"]),
            report=self.report_band(canonical, section["h1"]),
            ads=self.carries_ads(key, "%s/" % key),
        )
        self.emit(os.path.join(key, "index.html"), out)
        self.hubs += 1
        if not pages:
            self.warn("hub /%s/ has no pages yet" % key)

    def render_search(self) -> None:
        """The one page that loads the hosted search script.

        Results are read from ?q= in the address, so the boxes elsewhere on the
        site stay plain forms and this page still works when it is reached from
        a bookmark or a pasted link. It carries no ad slot and asks not to be
        indexed: a results page has no content of its own to offer either one.
        """
        if not self.search_on():
            return
        url = "/search/"
        canonical = self.base + url
        h1 = "Search the help centre"
        description = (
            "Search every InoxTV setup guide, feature page and troubleshooting fix "
            "for Android TV, Fire TV and Android phones in one place."
        )
        trail = [("Home", "/"), ("Search", url)]

        cards = []
        for key, section in self.site["sections"].items():
            if section.get("hub") is False:
                continue
            if not any(p["section"] == key for p in self.pages):
                continue
            cards.append(
                '        <li><a href="/%s/">\n          <h3>%s</h3>\n'
                "          <p>%s</p>\n        </a></li>"
                % (key, html.escape(section["title"]), html.escape(section["description"]))
            )
        browse = (
            '    <section class="hub-group" aria-labelledby="g-browse">\n'
            '      <h2 id="g-browse">Or work through a section</h2>\n'
            '      <ul class="hub-cards">\n%s\n      </ul>\n    </section>' % "\n".join(cards)
        )

        rendered = self.tpl.render(
            "layout",
            "search",
            {
                "breadcrumbs": breadcrumbs_html(trail),
                "h1": html.escape(h1),
                "lede": "Everything in the help centre is indexed here: the setup "
                        "guides, the feature pages, the key reference and every fix. "
                        "Search for the message on screen or the setting you are "
                        "looking at.",
                "search_hero": self.search_form("hub"),
                "groups": browse,
                "disclaimer": html.escape(self.site["disclaimer"]),
            },
        )
        out = self.shell(
            title="Search InoxTV help and guides | InoxTV",
            description=description,
            canonical=canonical,
            og_type="website",
            body_class="page-hub page-search",
            content=rendered,
            jsonld=jsonld_block(self.breadcrumb_ld(trail)),
            current_section="search",
            share=self.share_links(canonical, h1, description),
            report=self.report_band(canonical, h1, "search"),
            robots="noindex, follow",
            cse=True,
            ads=self.carries_ads("search", "search/"),
        )
        self.emit(os.path.join("search", "index.html"), out)

    @staticmethod
    def hub_group(heading: str, gid: str, members: list[dict]) -> str:
        cards = "\n".join(
            '        <li><a href="%s">\n'
            "          <h3>%s</h3>\n"
            "          <p>%s</p>\n"
            "        </a></li>"
            % (
                p["url"],
                html.escape(p["h1"]),
                html.escape(p["meta"].get("card", p["meta"]["description"])),
            )
            for p in members
        )
        return (
            '    <section class="hub-group" aria-labelledby="g-%s">\n'
            '      <h2 id="g-%s">%s</h2>\n'
            '      <ul class="hub-cards">\n%s\n      </ul>\n    </section>'
            % (gid, gid, html.escape(heading), cards)
        )

    # -- output ------------------------------------------------------------

    def emit(self, rel: str, text: str) -> None:
        rel = rel.replace("\\", "/")
        if rel in PROTECTED:
            raise SystemExit("refusing to overwrite hand-written %s" % rel)
        write(os.path.join(ROOT, rel), text)
        self.written.append(rel)

    def audit(self, page: dict, rendered: str) -> None:
        meta = page["meta"]
        # The plan sets a target per page; the section floor is the fallback for
        # a page that does not state one.
        floor = meta.get("min_words") or self.site["sections"][page["section"]].get(
            "word_floor", 0
        )
        if page["words"] < floor:
            self.warn(
                "%s: %d words, floor is %d" % (page["slug"], page["words"], floor)
            )
        if len(meta["title"]) > TITLE_MAX:
            self.warn("%s: title is %d chars (max %d)" % (page["slug"], len(meta["title"]), TITLE_MAX))
        if not DESC_MIN <= len(meta["description"]) <= DESC_MAX:
            self.warn(
                "%s: description is %d chars (want %d-%d)"
                % (page["slug"], len(meta["description"]), DESC_MIN, DESC_MAX)
            )
        if meta["title"].split(" | ")[0].strip().lower() == meta["h1"].strip().lower():
            self.warn("%s: title and h1 are identical" % page["slug"])
        if len(meta.get("related") or []) < 2 and page["section"] != "policy":
            self.warn("%s: fewer than 2 related links" % page["slug"])
        if 'name="keywords"' in rendered:
            self.warn("%s: has a keywords meta tag" % page["slug"])
        lowered = strip_tags(rendered).lower()
        for phrase in BANNED:
            if phrase in lowered:
                self.warn("%s: contains banned phrasing '%s'" % (page["slug"], phrase))
        self.check_tells(page["slug"], rendered)
        if 'class="adsbygoogle"' in rendered and page["section"] == "policy":
            self.warn("%s: policy page must carry no ad slot" % page["slug"])
        # Checked in both directions off carries_ads(), so the page that may not
        # load the script cannot quietly start loading it, and one that may
        # cannot quietly lose it.
        head = rendered[: rendered.lower().find("</head>")]
        has_loader = "googlesyndication.com/pagead/js/adsbygoogle.js" in head
        if self.carries_ads(page["section"], page["slug"]):
            if not has_loader:
                self.warn("%s: no ad loader in <head>" % page["slug"])
        elif has_loader:
            self.warn(
                "%s: loads the ad script but is exempt - the automatic units "
                "would fill it, which the privacy policy says does not happen"
                % page["slug"]
            )
        if 'data-ad-slot=""' in rendered:
            self.warn("%s: ad unit with an empty slot id" % page["slug"])
        # A page that does not name itself as the canonical version is what lets
        # a duplicate compete with it. Both halves matter: exactly one tag, and
        # the address it names has to be this page's own.
        canonicals = re.findall(r'<link\s+rel="canonical"\s+href="([^"]+)"', rendered)
        want = self.base + page["url"]
        if len(canonicals) != 1:
            self.warn(
                "%s: %d canonical tags, want exactly 1" % (page["slug"], len(canonicals))
            )
        elif canonicals[0] != want:
            self.warn(
                "%s: canonical points at %s, want %s"
                % (page["slug"], canonicals[0], want)
            )

    def check_links(self) -> None:
        """Warn on any root-relative href or img src that will 404.

        Everything the help centre links to is either a generated page, a hub,
        or a file sitting in the repository, so this is decidable at build time
        and there is no excuse for shipping a dead link.
        """
        pages = {"/"} | {p["url"] for p in self.pages}
        pages |= {
            "/%s/" % key
            for key, section in self.site["sections"].items()
            if section.get("hub") is not False
        }
        if self.search_on():
            pages.add("/search/")

        for page in self.pages:
            targets = set(re.findall(r'(?:href|src)="(/[^"#]*)', page["body"]))
            for target in sorted(targets):
                if target in pages:
                    continue
                local = os.path.join(ROOT, target.lstrip("/").replace("/", os.sep))
                if os.path.exists(local):
                    continue
                self.warn("%s: links to %s, which does not exist" % (page["slug"], target))

    def sitemap(self) -> None:
        today = date.today().isoformat()
        rows = [("/", today, "1.0")]
        for key, section in self.site["sections"].items():
            if section.get("hub") is False:
                continue
            if any(p["section"] == key for p in self.pages):
                rows.append(("/%s/" % key, today, "0.8"))
        for page in self.pages:
            pri = "0.5" if page["section"] == "policy" else "0.7"
            rows.append((page["url"], page["meta"]["updated"], pri))
        rows.append(("/privacy.html", "2026-05-23", "0.5"))

        body = "\n".join(
            "  <url>\n    <loc>%s%s</loc>\n    <lastmod>%s</lastmod>\n"
            "    <priority>%s</priority>\n  </url>" % (self.base, url, mod, pri)
            for url, mod, pri in rows
        )
        write(
            os.path.join(ROOT, "sitemap.xml"),
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            "%s\n</urlset>\n" % body,
        )
        self.written.append("sitemap.xml")

    def check_reachability(self) -> None:
        """Every page must be reachable from / by real links, in <= 3 clicks.

        Hubs are linked from the nav, so a page in a hub group is two clicks
        from home. A page with no group never appears in a hub listing.
        A related card and an in-body link both count as an inbound link; a
        page linking to itself does not.
        """
        for page in self.pages:
            if page["section"] == "policy":
                continue
            section = self.site["sections"][page["section"]]
            group_ids = {g["id"] for g in section.get("groups", [])}
            gid = page["meta"].get("group")
            if gid and gid not in group_ids:
                self.warn("%s: group '%s' is not defined for section %s"
                          % (page["slug"], gid, page["section"]))

        linked: set[str] = set()
        for page in self.pages:
            own = page["slug"]
            for slug in page["meta"].get("related") or []:
                if slug.strip("/") != own:
                    linked.add(slug.strip("/"))
            for href in re.findall(r'href="/([^"#]*)"', page["body"]):
                if href.strip("/") != own:
                    linked.add(href.strip("/"))
        for page in self.pages:
            if page["section"] == "policy":
                continue
            if page["slug"] not in linked:
                self.warn("%s: nothing links to it; add it to another page's related list"
                          % page["slug"])

    def prune(self) -> None:
        """Delete output from an earlier build that this one no longer produces."""
        old = set(load_json(MANIFEST, {}).get("written", []))
        for rel in sorted(old - set(self.written)):
            if rel in PROTECTED:
                continue
            path = os.path.join(ROOT, rel)
            if os.path.isfile(path):
                os.remove(path)
                parent = os.path.dirname(path)
                while parent != ROOT and os.path.isdir(parent) and not os.listdir(parent):
                    os.rmdir(parent)
                    parent = os.path.dirname(parent)
                print("  removed stale %s" % rel)

    def save_manifest(self) -> None:
        write(
            MANIFEST,
            json.dumps({"written": sorted(self.written)}, indent=2) + "\n",
        )

    def check_tells(self, label: str, rendered: str) -> None:
        """Flag phrasing and punctuation habits that read as machine-written.

        Called for generated pages from audit() and for the two hand-written
        ones from check_protected(), because a tell on the homepage is the one
        a reviewer meets first.

        The dash count deliberately ignores list and table rows. A row that
        reads "Large - for a source that stalls" is using the mark as
        typography between a term and its gloss, which is what it is for. The
        habit worth catching is in running prose, where a dash appended to
        sentence after sentence is doing the job a full stop, a colon or a pair
        of brackets should be sharing.

        <title> is skipped for the same reason: a separator between a name and
        a descriptor in a 55-character title is a typographic convention, not a
        sentence, and shortening a good title to satisfy this check would cost
        more than it gains.
        """
        lowered = strip_tags(rendered).lower()
        for phrase in TELLS:
            if phrase in lowered:
                self.warn("%s: phrasing reads as machine-written, '%s'" % (label, phrase))

        prose_dashes = 0
        for line in rendered.split("\n"):
            stripped = line.strip()
            if stripped.startswith("<li>") or "<td>" in stripped or "<th>" in stripped:
                continue
            if stripped.startswith("<title>"):
                continue
            prose_dashes += stripped.count("&mdash;") + stripped.count("—")

        words = word_count(rendered)
        if words >= 200 and prose_dashes:
            rate = prose_dashes / words * 1000
            if rate > TELL_DASH_RATE:
                self.warn(
                    "%s: %d em-dashes in running prose, %.1f per 1000 words "
                    "(over %.1f) - vary the punctuation"
                    % (label, prose_dashes, rate, TELL_DASH_RATE)
                )

    def check_protected(self) -> None:
        """Check the two hand-written pages the builder never renders.

        index.html and privacy.html are excluded from emit(), so audit() never
        sees them and every check it performs stops at the edge of the generated
        set. That makes this the only place the policy and search-gate checks can
        reach them, and it has to be kept in step with audit() by hand.

        The search half is checked in both directions: blanking "cse_id" strips
        the field from every generated page, which would leave these two aiming
        at a /search/ that no longer exists.
        """
        for rel in sorted(PROTECTED):
            path = os.path.join(ROOT, rel)
            if not os.path.exists(path):
                continue
            has_form = 'action="/search/"' in read(path)
            if has_form and not self.search_on():
                self.warn(
                    '%s: has a search form but search is off, so it points at a '
                    'missing /search/ - remove the form or set "cse_id"' % rel
                )
            elif not has_form and self.search_on():
                self.warn(
                    "%s: search is on but this page has no search field "
                    "(it is hand-written, so the builder cannot add it)" % rel
                )

            # audit() only ever sees pages this script renders, so until now the
            # two hand-written pages were the one place banned phrasing could sit
            # unchecked - and the homepage was carrying "thousands of channels"
            # in both its FAQ copy and the matching schema. The phrase was
            # describing playlist capacity rather than offering anything, but a
            # classifier matches wording, not intent.
            rendered = read(path)
            lowered = strip_tags(rendered).lower()
            for phrase in BANNED:
                if phrase in lowered:
                    self.warn("%s: contains banned phrasing '%s'" % (rel, phrase))
            self.check_tells(rel, rendered)
            if 'name="keywords"' in rendered:
                self.warn("%s: has a keywords meta tag" % rel)
            head = rendered[: rendered.lower().find("</head>")]
            # Same rule as carries_ads(), stated per page because these two are
            # hand-written and carry no section key for it to read. The homepage
            # shows ads; privacy.html is the page the promise in its own §11 is
            # about, so it must not load the script.
            if PROTECTED_ADS[rel]:
                if "googlesyndication.com/pagead/js/adsbygoogle.js" not in head:
                    self.warn("%s: no ad loader in <head>" % rel)
            elif "googlesyndication.com/pagead/js/adsbygoogle.js" in head:
                self.warn(
                    "%s: loads the ad script, but this page promises visitors no "
                    "advertising - remove it from the <head>" % rel
                )
            if "googletagmanager.com/gtag/js" not in head:
                self.warn("%s: no analytics in <head>" % rel)

    def check_consent(self) -> None:
        """Check the consent defaults on every page that loads Google script.

        Consent Mode is order-sensitive in a way nothing else here is: gtag.js
        and adsbygoogle.js both read the defaults when they initialise, so a
        block that runs after either of them has no effect at all and fails
        silently - the page looks right, the tags fire, and the EEA visitor is
        measured anyway. A diff of the file will not show it. Only the offsets
        will, which is why this compares positions rather than presence.

        The generated pages all inherit one copy through the layout's
        {% include consent-mode %}. index.html and privacy.html are hand-written
        and cannot, so they hold pasted copies, and a pasted copy is a copy that
        drifts: the next change to the partial would leave the homepage on the
        old region list. So the two are compared against the partial itself,
        ignoring indentation, because the hand-written pages indent their head
        two spaces and the partial does not.
        """
        partial = os.path.join(PARTIALS, "consent-mode.html")
        if not os.path.isfile(partial):
            self.warn(
                "_partials/consent-mode.html is missing: every page would load "
                "gtag.js with no consent defaults ahead of it"
            )
            return

        def squash(text: str) -> str:
            """Compare on content, not on how deeply a file happens to indent."""
            return "\n".join(
                line.strip() for line in text.split("\n") if line.strip()
            )

        want = squash(read(partial))

        # self.written carries sitemap.xml too; only pages have a head to check.
        pages = sorted(PROTECTED) + sorted(
            r for r in self.written if r.endswith(".html")
        )
        for rel in pages:
            path = os.path.join(ROOT, rel)
            if not os.path.isfile(path):
                continue
            text = read(path)
            head = text[: text.lower().find("</head>")]

            consent = head.find("gtag('consent', 'default'")
            tagjs = head.find("googletagmanager.com/gtag/js")
            adjs = head.find("googlesyndication.com/pagead/js/adsbygoogle.js")

            if consent < 0:
                if tagjs >= 0 or adjs >= 0:
                    self.warn(
                        "%s: loads Google script with no consent defaults in "
                        "<head>" % rel
                    )
                continue
            if tagjs >= 0 and tagjs < consent:
                self.warn(
                    "%s: gtag.js is loaded before the consent defaults, so the "
                    "defaults are read too late to apply" % rel
                )
            if adjs >= 0 and adjs < consent:
                self.warn(
                    "%s: the ad script is loaded before the consent defaults, so "
                    "the defaults are read too late to apply" % rel
                )

            # Both hand-written pages hold a pasted copy. Anything generated got
            # its copy from the partial by construction, so there is nothing to
            # compare - only the paste can drift.
            if rel in PROTECTED:
                start = head.rfind("<script>", 0, consent)
                end = head.find("</script>", consent)
                if start < 0 or end < 0:
                    self.warn("%s: consent block is not in a <script> tag" % rel)
                    continue
                got = squash(head[start : end + len("</script>")])
                if got != want:
                    self.warn(
                        "%s: its consent block no longer matches "
                        "_partials/consent-mode.html - this page is hand-written, "
                        "so the partial does not reach it and the copy has to be "
                        "updated by hand" % rel
                    )

    def check_exposure(self) -> None:
        """Find source files the host would publish as pages.

        This is the check that was missing when the site was rejected on
        2026-09-12. The fragments lived in content/, which has no underscore, so
        Jekyll copied all 31 of them into the served output: every article also
        answered at /content/<section>/<slug>.html as a chrome-less, canonical-less
        wall of text. Two near-identical URLs per article, and the duplicate is
        exactly the "low-value content" shape the policies refuse.

        Nothing here inspects the build's own output - it inspects the repository
        the way the host will see it, because that is where this class of fault
        lives. Rendered pages are checked by audit() instead.
        """
        nojekyll = os.path.join(ROOT, ".nojekyll")
        if os.path.exists(nojekyll):
            self.warn(
                ".nojekyll exists, which switches Jekyll off and starts serving "
                "every _ directory - _content, _layouts, _partials and _data "
                "would all become public. Delete it."
            )

        # Jekyll drops "_" and "." directories. Everything else ships.
        served_dirs = [
            name
            for name in sorted(os.listdir(ROOT))
            if os.path.isdir(os.path.join(ROOT, name))
            and not name.startswith(("_", "."))
        ]
        for name in served_dirs:
            for dirpath, dirs, files in os.walk(os.path.join(ROOT, name)):
                dirs[:] = [d for d in dirs if not d.startswith((".", "_"))]
                for filename in sorted(files):
                    if not filename.endswith(".html"):
                        continue
                    path = os.path.join(dirpath, filename)
                    text = read(path)
                    # A fragment carries JSON front matter and no document shell.
                    # A rendered page has both a doctype and an <html> element.
                    if FRONT_RE.match(text) or "<html" not in text.lower():
                        self.warn(
                            "%s would be served as a page but is an unrendered "
                            "fragment - move it under a _ directory"
                            % os.path.relpath(path, ROOT).replace(os.sep, "/")
                        )

        # A stray .html at the repository root becomes an indexable thin page,
        # and the two that belong there are hand-written and already accounted for.
        for filename in sorted(os.listdir(ROOT)):
            if not filename.endswith(".html") or filename in PROTECTED:
                continue
            if not os.path.isfile(os.path.join(ROOT, filename)):
                continue
            self.warn(
                "%s sits in the repository root, so it is served as a page - "
                "move it into a section or delete it" % filename
            )

    def run(self) -> int:
        self.discover()
        for page in self.pages:
            self.render_page(page)
        for key, section in self.site["sections"].items():
            if section.get("hub") is False:
                continue
            self.render_hub(key, section)
        self.render_search()
        self.sitemap()
        self.check_links()
        self.check_reachability()
        self.check_protected()
        self.check_consent()
        self.check_exposure()
        self.prune()
        self.save_manifest()
        return self.report()

    def report(self) -> int:
        by_section: dict[str, list[dict]] = {}
        for page in self.pages:
            by_section.setdefault(page["section"], []).append(page)
        print("built %d pages + %d hubs" % (len(self.pages), self.hubs))
        for key in sorted(by_section):
            pages = by_section[key]
            total = sum(p["words"] for p in pages)
            print("  %-16s %2d pages  %6d words" % (key, len(pages), total))
        print("  %-16s %6d words total" % ("", sum(p["words"] for p in self.pages)))
        slot = self.ad_slot_id({})
        if slot:
            print("  ads              loader on every page + in-article unit %s" % slot)
        else:
            print("  ads              loader on every page, no in-article unit:")
            print('                   set "ad_slot" in _data/site.json once approved')
        if self.search_on():
            print('  search           on, /search/ built')
        else:
            print('  search           off: set "cse_id" in _data/site.json to switch it on')
        if self.warnings:
            print("\n%d thing(s) to look at:" % len(self.warnings))
            for message in self.warnings:
                print("  - %s" % message)
        else:
            print("\nno warnings")
        return 1 if (self.warnings and self.strict) else 0


def clean() -> None:
    old = load_json(MANIFEST, {}).get("written", [])
    dirs = set()
    for rel in old:
        if rel in PROTECTED:
            continue
        path = os.path.join(ROOT, rel)
        if os.path.isfile(path):
            os.remove(path)
        top = rel.split("/")[0]
        if "/" in rel:
            dirs.add(top)
    for name in dirs:
        path = os.path.join(ROOT, name)
        if os.path.isdir(path) and not os.listdir(path):
            shutil.rmtree(path)
    print("cleaned %d generated file(s)" % len(old))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--clean", action="store_true", help="delete generated output first")
    parser.add_argument("--strict", action="store_true", help="exit 1 on any warning")
    args = parser.parse_args()
    if args.clean:
        clean()
    site = load_json(os.path.join(DATA, "site.json"))
    if not site:
        raise SystemExit("_data/site.json not found")
    try:
        return Builder(site, args.strict).run()
    except (ValueError, KeyError) as exc:
        print("build failed: %s" % exc, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
