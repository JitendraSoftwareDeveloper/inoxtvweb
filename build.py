#!/usr/bin/env python3
"""Static site builder for inoxtv.com.

Renders every fragment in content/ through _layouts/ and _partials/ into a
committed <slug>/index.html, and regenerates the navigation, section hubs,
breadcrumbs, table of contents, structured data and sitemap.xml from one
registry so none of them can drift as pages are added.

Adding a page is one new file in content/<section>/ plus a rebuild. Nothing
else needs touching.

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

ROOT = os.path.dirname(os.path.abspath(__file__))
CONTENT = os.path.join(ROOT, "content")
LAYOUTS = os.path.join(ROOT, "_layouts")
PARTIALS = os.path.join(ROOT, "_partials")
DATA = os.path.join(ROOT, "_data")
MANIFEST = os.path.join(ROOT, "_data", "build-manifest.json")

# Hand-written pages the builder must never touch or overwrite. privacy.html
# is load-bearing: the shipped app opens https://inoxtv.com/privacy.html from
# settings_about_privacy_policy_url, old installs will request that exact path
# forever, and GitHub Pages cannot issue a redirect.
PROTECTED = {"index.html", "privacy.html"}

TITLE_MAX = 65
DESC_MIN, DESC_MAX = 120, 165

MONTHS = ("January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December")

# Phrasing that reads as piracy-adjacent to a policy reviewer. Checked against
# the rendered page, not just the fragment, so a layout cannot smuggle it in.
BANNED = [
    "free iptv",
    "premium iptv",
    "iptv subscription",
    "free channels",
    "watch free tv",
    "free live tv",
]


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
            raise SystemExit("content/ not found")
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
            )
            blocks.append(
                '      <div class="site-foot-col">\n'
                "        <h2>%s</h2>\n        <ul>\n%s\n        </ul>\n      </div>"
                % (html.escape(col["heading"]), links)
            )
        return "\n".join(blocks)

    def ads_html(self, meta: dict, section: dict) -> str:
        """In-article slots, or nothing at all on a page without publisher content."""
        if not section.get("ads") or meta.get("ads") is False:
            return ""
        return self.tpl.render(
            "partial",
            "ad-in-article",
            {"ads_client": self.site["ads_client"], "ad_slot": meta.get("ad_slot", "")},
        )

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
              content, jsonld, current_section, ads) -> str:
        # A page with no slot makes no ad request at all: loading the script
        # where nothing can render it is pointless, and on a policy page it
        # invites exactly the wrong reading.
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
                "body_class": body_class,
                "analytics_id": self.site["analytics_id"],
                "ads_loader": ads_loader,
                "jsonld": jsonld,
                "nav_links": self.nav_links(current_section),
                "footer_columns": self.footer_columns(),
                "disclaimer": html.escape(self.site["disclaimer"]),
                "content": content,
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
            ads=bool(ads),
        )
        self.emit(os.path.join(page["slug"], "index.html"), out)
        self.audit(page, out)

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
        rendered = self.tpl.render(
            "layout",
            "hub",
            {
                "breadcrumbs": breadcrumbs_html(trail),
                "h1": html.escape(section["h1"]),
                "lede": section.get("lede", ""),
                "content": "",
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
            ads=False,  # a hub is an index; the prose lives on the pages it links to
        )
        self.emit(os.path.join(key, "index.html"), out)
        self.hubs += 1
        if not pages:
            self.warn("hub /%s/ has no pages yet" % key)

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
        if 'class="adsbygoogle"' in rendered and page["section"] == "policy":
            self.warn("%s: policy page must carry no ad slot" % page["slug"])

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

    def run(self) -> int:
        self.discover()
        for page in self.pages:
            self.render_page(page)
        for key, section in self.site["sections"].items():
            if section.get("hub") is False:
                continue
            self.render_hub(key, section)
        self.sitemap()
        self.check_links()
        self.check_reachability()
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
