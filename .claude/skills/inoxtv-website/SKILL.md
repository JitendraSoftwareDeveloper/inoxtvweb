---
name: inoxtv-website
description: Work on the InoxTV help/marketing website at f:\Projects\Android\inoxtv\inoxtvweb (inoxtv.com). Use for ANY change to that site - adding or editing feature/guide/troubleshooting pages, SEO metadata, structured data, the static build system, SVG D-pad and flow diagrams, ad-programme policy compliance, sitemap, or asset pipeline. Also use when asked why the site was rejected for monetisation review, or how to add a page without breaking others.
---

# InoxTV Website Skill

Website repo: **`f:\Projects\Android\inoxtv\inoxtvweb`** -> published at **https://inoxtv.com** via
GitHub Pages (`CNAME` = `inoxtv.com`). The Android app it documents lives at
**`F:\Projects\Android\inoxtv\app\inoxtv`** and has its own `CLAUDE.md` plus the
`inoxtv-ui-guardrails` and `inoxtv-anti-modapk` skills.

Brand name, exactly as the site implements it: **InoxTV** (`og:site_name`, `manifest.json`). The
wordmark in the homepage `<h1>` splits it as `Inox` + `tv`. The app's own strings use `InoxTv`.

## Read first

1. `inoxtv_adsense_plan.md` - the plan of record. Page inventory, build system, SEO spec, diagram
   system, review strategy, execution phases. (Filename is legacy; do not repeat that word in new
   content - see the two owner rules below.)
2. `inoxtv_website_plan.md` - design system: colour tokens, typography, animation timings.
3. `index.html` `<head>` - the canonical SEO boilerplate every page inherits.

## Two owner rules that override style defaults

### 1. Never name the ad programme in site content

Do not write the programme's brand name, the publisher ID, or equivalent ad-network branding in page
copy, titles, headings, filenames, or anything else that reaches the site. Internally call it "the
review" or "the ad programme". The loader script and `ads.txt` obviously stay - they are machinery,
not content.

### 2. No AI footprint, anywhere

The site must read as first-party developer documentation written by the person who built the app.

- No "generated with", no model or tool attribution - not in copy, footers, HTML comments, commit
  messages, SVG metadata, or asset EXIF. Strip generator comments from anything you emit.
- No AI-tell prose. Avoid em-dash runs, "it's not just X, it's Y", "delve", "seamless", "robust",
  "in today's fast-paced world", three-item padding, and openers that restate the heading.
- No uniform page skeleton. Vary section and sentence length. Let some pages be genuinely short.
- Write in plain second-person English, and carry specifics only the developer would know: real
  label text, real defaults, real limits, real error strings.

Both are gate items. Check them on every page before it is committed.

## Why the site is being rebuilt

It is being converted from a one-page promo site into a help centre, because monetisation review
repeatedly returned "insufficient content". Two independent causes, both must stay fixed:

1. **Too few pages of real content.** Two indexable pages at the start (`index.html`,
   `privacy.html`). The fix is the P0 page set in the plan.
2. **IPTV is a high-risk vertical.** Piracy-adjacent signals trigger copyright-policy rejection even
   when content volume is fine. On this site the phrasing was not confined to the meta keywords tag -
   it was also in the `<title>`, `manifest.json` `name`, the JSON-LD descriptions, and the FAQ
   answers. Deleting the keywords tag alone leaves the signal in place.

### Hard content rules - never violate, on any page

- InoxTV is a **player** for playlists the user already owns. It ships **zero** content.
- Never host, link, embed, or name a playlist source, M3U URL, Xtream server, Stalker portal, IPTV provider, or channel list.
- Never publish channel names, channel counts, or broadcaster logos.
- Never write the piracy-adjacent phrasings: "free IPTV", "premium IPTV", "IPTV subscription", "free channels", "watch free TV".
- The disclaimer band appears in the footer of **every** page. Its source of truth is the app's own `main_screen_intro_text`.
- Never add `<meta name="keywords">`. No ranking value, and on this site it is pure negative signal.

## Architecture

### Current state vs target

Check for `build.py` / `_layouts/` before assuming.

- **Pre-build-system (original):** `index.html` + `privacy.html`, each with copy-pasted nav/footer/head.
- **Target:** `build.py` (stdlib Python only) renders `_content/**/*.html` fragments through
  `_layouts/` + `_partials/` into committed `<slug>/index.html` files.

### Non-negotiable constraints

| Constraint | Why |
|---|---|
| **Generated output is committed** | GitHub Pages has no build step. Same reason `.webp` and `og-image.jpg` must be committed - untracked generated assets 404 in production. |
| **No Node / npm / framework** | Existing tooling is Python stdlib (`convert-webp.py`, `check-assets.py`). Keep it that way. |
| **No runtime JS for nav, content, or footer** | Pages must be server-rendered HTML for the reviewer and for indexing. |
| **Apex domain only** | `www.inoxtv.com` does not resolve. Every absolute URL must be non-www. |
| **`privacy.html` never moves** | The shipped app hardcodes `https://inoxtv.com/privacy.html` (`settings_about_privacy_policy_url`). Old installs request it forever and Pages cannot 301. Do not create a duplicate at `/privacy/`. |
| **Never edit a generated `index.html`** | The next build overwrites it. Edit `_content/` or `_layouts/`. |
| **Never put a stray `.html` in the repo root** | Pages serves it. A scratch file becomes an indexable thin page. |

### Directory map

```
inoxtvweb/
  inoxtv_adsense_plan.md      <- plan of record
  inoxtv_website_plan.md      <- design system
  build.py                    <- builder (may not exist yet)
  _layouts/  _partials/  _data/site.json
  _content/<section>/<slug>.html  <- HTML fragment + JSON front matter
  index.html  privacy.html    <- homepage + privacy (privacy stays flat)
  images/
    diagrams/*.svg            <- hand-authored, see below
    screenshots/{mob,tv}/     <- owner-captured, .png + .webp pairs
    *.png + *.webp pairs
  check-assets.py  convert-webp.py
  sitemap.xml  robots.txt  manifest.json  CNAME
  ads.txt  app-ads.txt        <- seller files, owner-maintained
  style.css  script.js
```

## Adding a page

```
1. _content/<section>/<slug>.html  - front matter + body (structure below)
2. Add 2-3 "related" links to it from existing pages (no orphans)
3. python build.py
4. python check-assets.py
5. Commit the content file AND the generated output
```

Nav, hub listing, sitemap, breadcrumbs, JSON-LD, and TOC regenerate themselves.

### Front matter

First line is an HTML comment holding JSON:

```html
<!--{
  "title":       "60 chars max - <task or symptom> - <qualifier> | InoxTV",
  "h1":          "different wording from title",
  "description": "140-160 chars, a promise of what the reader will be able to do",
  "section":     "features | guides | troubleshooting | remote",
  "slug":        "features/multiview",
  "updated":     "YYYY-MM-DD",
  "related":     ["slug/one", "slug/two", "slug/three"],
  "howto":       { "name": "...", "steps": ["...", "..."] },
  "faq":         [{"q": "...", "a": "..."}]
}-->
```

`howto` emits `HowTo` JSON-LD; `faq` emits `FAQPage` **and** renders the visible accordion from the
same data - markup and schema must never disagree.

### Page body structure

Use it as a checklist of what a reader needs, not as a template to fill uniformly. Skip parts that
do not apply, and vary the order when the topic wants it.

1. Lede, 2-3 sentences: what this page lets you do, which platform.
2. Where it lives: settings-breadcrumb chip, `Settings > Playback > Buffer size`.
3. Diagram (D-pad map / flow / annotated screenshot).
4. Numbered steps, one action each, using the app's **exact** on-screen labels.
5. Options table: every value and when to pick it.
6. Platform differences (TV vs mobile) wherever behaviour differs.
7. Troubleshooting table: symptom, cause, fix - cross-linked.
8. Related pages (from front matter).
9. Visible "Last updated".

### Word floors

Features 700, Guides 900, Troubleshooting 500, Home 900. The builder warns below these. A floor is a
minimum, not a target - padding to hit a number is exactly the AI-tell to avoid.

## UI copy must match the app exactly

**Every on-screen label quoted on the site must be copied verbatim from**
`F:\Projects\Android\inoxtv\app\inoxtv\shared\src\main\res\values\strings.xml`.

If the site says "Buffer" and the app says "Buffer size", the page is wrong. Grep before writing:

```
grep -n 'name="settings_playback' <app>/shared/src/main/res/values/strings.xml
```

Useful groups: `settings_*`, `custom_tools_*` (player menu), `aspect_ratio_*`, `recording_*`,
`search_overlay_*`, `settings_rc_*` (remote key and action labels).

Several app strings are already good explanatory prose - reuse them rather than inventing copy.
`settings_playback_buffer_size_description`, `settings_playback_afr_description`, and
`recording_confirm_message` are the best examples.

## Diagrams

| Kind | Source |
|---|---|
| D-pad key maps, remote faces, gesture maps, flow diagrams, comparison diagrams, screen-anatomy wireframes, settings-path chips | **Author as hand-written SVG** |
| Real app UI screenshots | **Owner captures** into `images/screenshots/{mob,tv}/` |
| Annotated screenshots | Hybrid: owner's PNG plus an SVG callout overlay (numbered pins, arrows, highlight rings) |

Reference implementation: `images/diagrams/dpad-player.svg`. Preview harness:
`images/diagrams/preview.html` (noindex, and `robots.txt` should disallow it).

### Authoring standard

- Hand-written SVG, no editor cruft, no generator comment. `viewBox` plus explicit `width`/`height`.
- `role="img"` plus `<title>` plus a **prose `<desc>` stating every mapping in words**. That `<desc>`
  is both the accessible name and crawlable text - it is why these diagrams help rankings.
- Palette as CSS custom properties in a `<style>` block.
- **Dark is the default palette**; light goes in `@media (prefers-color-scheme: light)`.
  An SVG loaded via `<img src>` resolves `prefers-color-scheme` against the **viewer's OS**, not the
  page. The site is dark-only (`color-scheme: dark`, `theme-color #0B1020`), so a light-default SVG
  renders as a white panel on a dark page for anyone on a light-mode OS. `dpad-player.svg` shipped
  with this bug - check it is fixed.
- Inlining the `<svg>` into the page is the alternative fix, and is better on pages where the diagram
  is the primary content, because the site's own CSS variables then apply.
- Font stack `Outfit, Inter, system-ui, ...`; minimum 15 px at natural size.
- Press vs **Hold** distinguished by colour **and** label - never colour alone (WCAG).
- Numbered chips on the control matching a legend, so prose can reference "(1)".
- `convert-webp.py` must skip `images/diagrams/` - never rasterise an SVG.

### D-pad diagrams have a machine-readable source of truth

Default key maps are Kotlin enums with a `default` field, one per context. **Generate and verify
diagrams from these - never transcribe by hand:**

| Context | File (under `<app>/shared/src/main/java/in/inoxtv/shared/player/`) | Enum |
|---|---|---|
| Player | `SettingsRemoteControlPlayerController.kt` | `PlayerKey(storageId, labelRes, default)` |
| TV Guide | `SettingsRemoteControlTvGuideController.kt` | `TvGuideKey(storageId, labelRes, default)` |
| Movies/Shows | `SettingsRemoteControlVodController.kt` | `VodKey(storageId, labelRes, default)` |

Verified **player** defaults (2026-09-07): Up = next channel, Long Up = Multiview, Down = previous
channel, Long Down = Picture-in-picture, Left = channels overlay, Long Left = channels preview,
Right = most recent channel, Long Right = program description, OK = info panel plus recent,
Long OK = menu, Back = go back, Long Back = search, Menu = menu, Long Menu = TV guide overlay,
Info = info panel, Guide = TV guide overlay, Play/Pause = play/pause, RW and FF = info for previous
and next channel, Backspace = TV guide groups overlay, Pg+ and Pg- = info for next and previous channel.

Verified **TV guide** defaults (2026-09-07): OK = open channel, Long OK = channel options,
Left = show groups, Right = scroll to next programs, Back = go back, Long Back = return to player,
Menu = menu, Long Menu = show groups, Guide = show groups, Info = program description,
Play/Pause = program description, RW and FF = page scroll channels up and down, Pg+ and Pg- = page
scroll channels up and down, Backspace = return to player, Red = change favourite status,
Green = channel options, Yellow = group options, Blue = open settings. **Note:** the TV guide has no
Up/Down and no long-arrow bindings at all - Up and Down navigate the channel list natively.

When a default changes in the app, regenerate the diagram.

## SEO rules

| Element | Rule |
|---|---|
| `<title>` | 50-60 chars, unique sitewide, no ad-programme or "premium IPTV" phrasing |
| `<meta description>` | 140-160 chars, unique, action-promising |
| `<meta keywords>` | **Never** |
| `<h1>` | exactly one, different wording from `<title>` |
| `<h2>` | always carries an `id` (deep links plus TOC) |
| Canonical | absolute, apex, trailing slash, self-referencing |
| Images | `alt` plus explicit `width`/`height` plus `loading="lazy"` below the fold |
| Internal links | 3+ outbound, 2+ inbound per page. Descriptive anchors, never "click here" |

Structured data by page type: Guide = `HowTo` + `BreadcrumbList` + `TechArticle`; Feature =
`TechArticle` + `BreadcrumbList` (+ `FAQPage` if applicable); Troubleshooting = `FAQPage` +
`BreadcrumbList` + `TechArticle`; Hub = `CollectionPage` + `BreadcrumbList`; Policy = `WebPage`;
Home = `WebSite` + `Organization` + `SoftwareApplication` x2 (already present, keep).

Write titles in search language: symptom-first for troubleshooting ("iptv buffering android tv fix"),
task-first for guides ("how to add m3u playlist android tv").

## Monetisation review

The loader script is already in `<head>` for the site's publisher account and must stay on all pages
so the crawler can verify the site. Do not name the programme in content.

- **Zero ad units** on `/about/`, `/contact/`, `/privacy.html`, `/terms/`, `/dmca/`, `/disclaimer/` - policy forbids ads on pages without publisher content.
- **Zero ad units** near the APK download button or the Downloader code. Accidental clicks are invalid traffic and can get the account limited.
- Content pages: max 2 in-article units. Hubs: 1. Never two units visible in one mobile viewport.
- Do not re-apply until the gate in the plan is fully ticked and Search Console shows 25+ pages **indexed**, not merely discovered. Allow 2-4 weeks after publishing.
- `ads.txt` / `app-ads.txt` are owner-maintained seller files - do not rewrite them; only append lines the owner supplies.

## Tooling

| Script | Purpose | Known issue |
|---|---|---|
| `check-assets.py` | Verifies every local asset reference resolves; lists orphans | Hardcodes `("index.html", "privacy.html")` - must become a recursive glob of generated HTML plus `_content/**/*.html` |
| `convert-webp.py` | Writes `.webp` siblings for `images/**/*.png` | Must skip `images/diagrams/` |

Run both from the repo root. `check-assets.py` needs Pillow only for the dimension report.

## Verification before calling any website task done

1. `python check-assets.py` reports no missing assets.
2. `python build.py` (once it exists) reports no word-floor warnings, no orphan pages, no broken `related` slug.
3. Every quoted UI label grepped against the app's `strings.xml`.
4. New or changed diagrams eyeballed in `images/diagrams/preview.html` at real size, on both a dark and a light OS setting.
5. Absolute URLs are apex, non-www.
6. Hard content rules re-read against the new copy.
7. The two owner rules checked: no ad-programme name, no AI footprint or tool attribution anywhere.
8. Generated output staged for commit alongside the source.

## Git

**Never run `git add` / `git commit` / `git push` in this repo.** The owner controls all git
operations. List the files that need staging and stop. Do not add tool attribution or co-author
trailers to any commit message here.
