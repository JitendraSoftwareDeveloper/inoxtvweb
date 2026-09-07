# InoxTV Website — AdSense Approval & Content Architecture Plan

> **Goal:** turn `inoxtv.com` from a one-page promo site into a genuine help centre for the
> InoxTV Android app, so that (a) Google AdSense approves it, (b) every page ranks for the
> problems real users search for, and (c) new feature pages can be added by dropping in one
> file — no hand-editing of nav, sitemap, or hub pages.

Created: 2026-09-07 · Owner: project owner · Companion doc: [`inoxtv_website_plan.md`](inoxtv_website_plan.md) (design system, colours, animations — still valid)

---

## 1. Diagnosis — why AdSense keeps saying "insufficient content"

### 1.1 The measurable problem

| Signal | Current state | What AdSense expects |
|---|---|---|
| Indexable pages | **2** (`index.html`, `privacy.html`) | A *site*, not a landing page — realistically 25+ substantial pages |
| Pages in `sitemap.xml` | 2 | All content pages |
| Site ownership pages | none | About + Contact are effectively mandatory |
| Content type | Promotional (feature bullets, download CTAs) | Informational — content with value independent of the ad |
| Nav depth | Anchor links inside one page (`#features`, `#faq`) | Real page-to-page navigation with crawlable internal links |
| User problem solved | none directly | Reviewer must be able to read a page and learn something |

The homepage is long, but length is not the metric. A reviewer sees **one page of marketing plus one
legal page**. "Feature X exists" is a claim; "here is how to do X, where the button is, and what to
do when it fails" is content. Only the second kind clears the bar.

### 1.2 The second, unstated problem — IPTV is a high-risk vertical

This matters as much as the page count and is easy to miss, because Google reports it under the same
generic rejection label.

AdSense will not monetise sites that appear to help people reach unauthorised streams. Publisher
policies on copyright and "enabling dishonest behaviour" are applied conservatively to anything in the
IPTV space. Several things on the site today read as piracy-adjacent to a reviewer or classifier:

| Current signal | Risk | Fix |
|---|---|---|
| `<meta name="keywords">` contains `free IPTV player`, `premium IPTV`, `Firestick IPTV`, `sideload IPTV`, `Downloader code` | Keyword set matches pirate-IPTV SEO patterns | Remove the meta keywords tag entirely — Google ignores it for ranking and it only supplies negative signal |
| FAQ: "you just need an **IPTV subscription** … from your service provider" | Implies the site is part of a subscription funnel | Reword to playlist-centric language: "a playlist you already own from a provider you have chosen" |
| Direct APK + Downloader code `2910810` prominent on the homepage | Software distribution outside official stores | Keep it — sideloading is a legitimate, supported path for Fire TV. But move it to a dedicated `/guides/install-fire-tv-stick/` page, explain *why* (no Play Store on Fire OS), and never place an ad unit next to the download button |
| No content disclaimer anywhere | The single biggest miss | See below |

**The app itself already says the right thing.** `shared/src/main/res/values/strings.xml` →
`main_screen_intro_text`:

> "InoxTv doesn't provide any sources of TV channels. To watch TV channels, please add a playlist
> provided by your IPTV service"

That sentence is the site's legal and policy backbone and it currently appears **nowhere on the
website**. It must appear on the homepage above the fold, in a persistent footer band on every page,
and expanded into `/disclaimer/`.

**Hard rules, permanently:**

- Never host, link, embed, or name a playlist source, channel list, M3U URL, Xtream server, or IPTV provider.
- Never publish channel names, channel counts, or logos of broadcasters.
- Never use the phrases "free IPTV", "IPTV subscription", "free channels", "watch free TV".
- Always describe InoxTV as a **player** for playlists the user already owns.

### 1.3 Verdict

Two independent gaps. Fixing only the page count and re-applying will fail again. The plan below
fixes both at once: the help-centre content solves "insufficient content", and the policy pages plus
positioning rewrite solve the copyright risk.

---

## 2. Strategy — the site becomes the app's help centre

The user's own framing is exactly right: **the website should solve the user's problems about each
and every feature.** That is also, conveniently, the single best answer to an AdSense content
rejection, because it produces content that is original, useful, and impossible to mistake for
promotional filler.

Three content families, each with a hub page:

| Family | Question it answers | Volume |
|---|---|---|
| **Guides** (`/guides/`) | "How do I set this up?" — task-first, start to finish | 15 pages |
| **Features** (`/features/`) | "What does this do, where is it, how do I use it?" | 24 pages |
| **Troubleshooting** (`/troubleshooting/`) | "It's broken — why, and how do I fix it?" | 16 pages |

Plus a **Remote control reference** (`/remote/`) — the highest-value section of the whole site,
because no competitor documents D-pad key maps well and InoxTV has three fully remappable contexts.

Why this shape wins on SEO as well: users search in problem language. "inoxtv buffering fix",
"xtream codes login failed", "android tv iptv no epg", "how to record live tv android tv". A
promotional page can never match those queries. A troubleshooting page matches them exactly.

---

## 3. Information architecture

### 3.1 URL conventions

- Directory-style URLs with `index.html`: `/features/multiview/` — clean, extension-free, stable forever, works on GitHub Pages with no redirect rules.
- Lowercase, hyphenated, no dates, no stop words.
- **Exception — `privacy.html` stays exactly where it is.** The shipped app hardcodes
  `https://inoxtv.com/privacy.html` (`settings_about_privacy_policy_url`), and older installs will
  request that path forever. GitHub Pages cannot issue a 301. Do not move it, do not create a
  duplicate at `/privacy/`.

### 3.2 Full page inventory

Legend — **P0** = required before re-applying to AdSense · **P1** = strongly recommended before re-applying · **P2** = post-approval growth

#### Tier 0 — Trust & policy (AdSense prerequisites)

| # | URL | Title focus | Words | Pri |
|---|---|---|---|---|
| 1 | `/` | InoxTV — IPTV player for Android TV, Fire TV & mobile | 900 | P0 |
| 2 | `/about/` | Who builds InoxTV, what it is and is not | 500 | P0 |
| 3 | `/contact/` | Support email, response time, what to include in a report | 350 | P0 |
| 4 | `/privacy.html` | Privacy policy *(exists — keep path)* | — | P0 |
| 5 | `/terms/` | Terms of use & acceptable use | 800 | P0 |
| 6 | `/disclaimer/` | Content disclaimer — InoxTV supplies no channels | 600 | P0 |
| 7 | `/dmca/` | Copyright & takedown policy | 600 | P0 |

#### Tier 1 — Hubs (generated from the page registry, never hand-written)

| # | URL | Purpose | Pri |
|---|---|---|---|
| 8 | `/guides/` | All setup guides, grouped by stage | P0 |
| 9 | `/features/` | Every feature, grouped by area | P0 |
| 10 | `/troubleshooting/` | Symptom-first problem index | P0 |
| 11 | `/remote/` | D-pad & remote key reference hub | P1 |
| 12 | `/changelog/` | Release notes per version | P2 |

#### Tier 2 — Guides

| # | URL slug under `/guides/` | Words | Pri |
|---|---|---|---|
| 13 | `first-hour-with-inoxtv` | 1,400 | P0 |
| 14 | `install-android-tv` | 900 | P0 |
| 15 | `install-fire-tv-stick` | 1,200 | P0 |
| 16 | `install-android-mobile` | 700 | P1 |
| 17 | `choose-playlist-type` (M3U vs Xtream vs Stalker) | 1,100 | P0 |
| 18 | `add-m3u-playlist` | 1,000 | P0 |
| 19 | `add-xtream-codes-playlist` | 1,000 | P0 |
| 20 | `add-stalker-portal-playlist` | 900 | P0 |
| 21 | `set-up-tv-guide-epg` | 1,200 | P0 |
| 22 | `customise-remote-buttons` | 1,500 | P1 |
| 23 | `set-up-parental-controls` | 1,000 | P1 |
| 24 | `set-up-recordings` | 1,100 | P1 |
| 25 | `organise-groups-and-sorting` | 900 | P1 |
| 26 | `backup-and-restore` | 900 | P1 |
| 27 | `change-language` | 600 | P2 |

#### Tier 3 — Features

| # | URL slug under `/features/` | Words | Pri |
|---|---|---|---|
| 28 | `live-tv` | 900 | P0 |
| 29 | `tv-guide-epg` | 1,000 | P0 |
| 30 | `movies-and-shows` | 900 | P0 |
| 31 | `multiview` | 800 | P0 |
| 32 | `picture-in-picture` | 700 | P0 |
| 33 | `search` (voice + text) | 800 | P1 |
| 34 | `recordings` | 900 | P1 |
| 35 | `favourites-and-my-list` | 700 | P1 |
| 36 | `reminders` | 600 | P1 |
| 37 | `catch-up-tv` | 800 | P1 |
| 38 | `player-controls` | 1,000 | P1 |
| 39 | `audio-and-subtitle-tracks` | 800 | P1 |
| 40 | `display-modes-and-aspect-ratio` | 700 | P1 |
| 41 | `playback-settings` (buffer, decoders, AFR, passthrough) | 1,200 | P1 |
| 42 | `parental-controls` | 900 | P1 |
| 43 | `appearance-and-themes` (7 dark themes, font size) | 700 | P2 |
| 44 | `languages` (19) | 700 | P2 |
| 45 | `playlist-management` | 900 | P2 |
| 46 | `groups-management` | 800 | P2 |
| 47 | `auto-start-and-resume` | 600 | P2 |
| 48 | `backup-and-restore` | 700 | P2 |
| 49 | `sleep-timer` | 500 | P2 |
| 50 | `external-player` | 600 | P2 |
| 51 | `file-explorer` (TV local M3U picker) | 600 | P2 |
| 52 | `account-info` (Xtream account & server panel) | 600 | P2 |

#### Tier 4 — Troubleshooting (symptom-titled — this is where search traffic lands)

| # | URL slug under `/troubleshooting/` | Words | Pri |
|---|---|---|---|
| 53 | `buffering-and-stuttering` | 1,100 | P0 |
| 54 | `playlist-wont-load` | 1,000 | P0 |
| 55 | `no-tv-guide-data` | 900 | P0 |
| 56 | `channel-wont-play` | 900 | P0 |
| 57 | `no-sound` | 800 | P1 |
| 58 | `subtitles-not-showing` | 700 | P1 |
| 59 | `xtream-login-failed` | 800 | P1 |
| 60 | `stalker-portal-mac-error` | 700 | P1 |
| 61 | `epg-update-failed` | 800 | P1 |
| 62 | `recording-failed` | 900 | P1 |
| 63 | `app-slow-on-tv-box` | 1,000 | P1 |
| 64 | `forgot-parental-pin` | 500 | P2 |
| 65 | `restore-failed` | 700 | P2 |
| 66 | `multiview-not-working` | 600 | P2 |
| 67 | `picture-in-picture-not-working` | 600 | P2 |
| 68 | `app-wont-start-on-boot` | 700 | P2 |

#### Tier 5 — Remote reference

| # | URL | Content | Pri |
|---|---|---|---|
| 69 | `/remote/player-keys/` | All 24 player-context keys, defaults, every available action | P1 |
| 70 | `/remote/tv-guide-keys/` | TV-guide-context key map | P1 |
| 71 | `/remote/vod-keys/` | Movies/shows-context key map | P1 |
| 72 | `/remote/mobile-gestures/` | Touch equivalents of every remote action | P2 |

**Totals:** P0 = 28 pages · P0+P1 = 52 pages · everything = 72 pages.

### 3.3 The re-application gate

Do **not** re-apply to AdSense until all of these are true. Re-applying against an unchanged site
just re-triggers the same rejection and burns review cycles.

- [ ] All 28 **P0** pages live, each meeting its word target
- [ ] All 7 Tier-0 trust/policy pages live and linked from the footer of every page
- [ ] `meta name="keywords"` removed sitewide
- [ ] "free IPTV" / "IPTV subscription" language purged sitewide
- [ ] Content disclaimer band present in the footer of every page
- [ ] `sitemap.xml` regenerated and submitted; Search Console shows ≥ 25 pages **indexed** (not merely discovered)
- [ ] Every page reachable from `/` in ≤ 3 clicks via real `<a href>` links
- [ ] No ad units on `/contact/`, `/privacy.html`, `/terms/`, `/dmca/`, `/disclaimer/`
- [ ] No ad unit within 300 px of the APK download button
- [ ] Lighthouse SEO ≥ 95 on a sample of 5 pages

Indexing is the slow step — allow **2–4 weeks** between publishing and re-applying.

---

## 4. Build system — how to add a page with zero conflict

### 4.1 The problem being solved

Today `nav`, `footer`, and ~80 lines of `<head>` boilerplate are **copy-pasted** between
`index.html` and `privacy.html`. At 72 pages that guarantees drift: a nav link added to one page and
missing from seventy others. `check-assets.py` also hardcodes `for f in ("index.html", "privacy.html")`,
so it silently stops checking new pages.

### 4.2 Chosen approach — a ~200-line Python builder, output committed

No Node, no npm, no framework. The repo already ships Python tooling (`convert-webp.py`,
`check-assets.py`), GitHub Pages serves committed static files, and the generated HTML must be real
server-rendered markup for SEO — no runtime JS injection of nav or content.

The build runs **locally**; its output is **committed**. This is consistent with the existing
constraint that generated assets (`.webp`, `og-image.jpg`) must be committed because the host has no
build step.

```
inoxtvweb/
├── build.py                    # the builder — stdlib only
├── _layouts/
│   ├── base.html               # <html>, <head>, nav, footer, ad slots
│   ├── doc.html                # article: breadcrumb, TOC, body, related, updated-date
│   └── hub.html                # listing page: grouped cards from the registry
├── _partials/
│   ├── nav.html
│   ├── footer.html
│   ├── disclaimer-band.html    # "InoxTV provides no channels" — every page
│   └── ad-in-article.html
├── _data/
│   └── site.json               # nav tree, section metadata, ad on/off per section
├── content/
│   ├── features/multiview.html
│   ├── guides/add-m3u-playlist.html
│   └── troubleshooting/buffering-and-stuttering.html
├── images/diagrams/*.svg
└── ← generated & committed →
    ├── features/multiview/index.html
    ├── features/index.html      (hub, generated)
    └── sitemap.xml              (generated)
```

### 4.3 Content file format

Each content file is a plain **HTML fragment** whose first line is an HTML comment holding JSON front
matter. HTML fragments rather than Markdown because there is no stdlib Markdown parser, and because
the pages embed hand-authored SVG diagrams, comparison tables, and custom CSS components that
Markdown would only get in the way of.

```html
<!--{
  "title":       "Multiview on Android TV — watch up to 4 channels at once | InoxTV",
  "h1":          "Multiview: watch several channels at the same time",
  "description": "How to open Multiview in InoxTV on Android TV, add and swap channels, choose which audio plays, and what to do when a channel will not load in a tile.",
  "section":     "features",
  "slug":        "features/multiview",
  "updated":     "2026-09-07",
  "diagram":     "dpad-multiview.svg",
  "related":     ["features/picture-in-picture", "guides/customise-remote-buttons", "troubleshooting/multiview-not-working"],
  "howto": {
    "name": "Open Multiview in InoxTV",
    "steps": [
      "While a channel is playing, hold the Up button on the remote.",
      "Pick a second channel from the list that appears.",
      "Press OK on any tile to make it the active, audible tile."
    ]
  },
  "faq": [
    {"q": "How many channels can Multiview show?", "a": "…"},
    {"q": "Which tile plays the sound?", "a": "…"}
  ]
}-->

<p class="lede">…</p>
<h2 id="how-to-open">How to open Multiview</h2>
…
```

### 4.4 What the builder does

For every file in `content/`:

1. Parse front matter; fail loudly on a missing `title`, `description`, `section`, or `slug`.
2. Render `doc.html` inside `base.html`, substituting `{{title}}`, `{{body}}`, etc.
3. Auto-generate, so no page ever hand-writes them:
   - `<link rel="canonical">` from `slug`
   - Open Graph + Twitter tags from `title` / `description`
   - `BreadcrumbList` JSON-LD from `slug`
   - `TechArticle` JSON-LD with `dateModified` from `updated`
   - `HowTo` JSON-LD if `howto` is present
   - `FAQPage` JSON-LD if `faq` is present (and render the visible accordion from the same data — never let the markup and the schema disagree)
   - A table-of-contents from the `<h2 id="…">` elements
   - The "Related pages" block from `related`, **validated bidirectionally** — a broken slug fails the build
4. Write `<slug>/index.html`.

Then, once:

5. Regenerate each hub page from the registry of everything it just built.
6. Regenerate `sitemap.xml` with real `lastmod` values from `updated`.
7. Regenerate the nav from `_data/site.json`.
8. Print a report: page count, per-page word count, any page under its section's minimum, any orphan (no inbound internal link).

### 4.5 Adding a page later — the whole procedure

```
1. Create content/<section>/<slug>.html with front matter + body.
2. Add 2–3 "related" slugs pointing at it from existing pages.
3. python build.py
4. python check-assets.py        # after the fix in §4.6
5. Commit the content file AND the generated output.
```

Nav, hub listing, sitemap, breadcrumbs, JSON-LD, and TOC all update themselves. Nothing else is
touched, so two people adding two different pages cannot conflict beyond `sitemap.xml`, which is
regenerated rather than merged.

### 4.6 Required fixes to existing tooling

| File | Change |
|---|---|
| `check-assets.py` | Replace the hardcoded `("index.html", "privacy.html")` tuple with a recursive glob of all generated `*.html`, excluding `_layouts/`, `_partials/`, and `images/diagrams/preview.html` |
| `check-assets.py` | Teach it that `.svg` diagrams are referenced from content fragments too, so scan `content/**/*.html` as well |
| `convert-webp.py` | Skip `images/diagrams/` entirely — SVG must not be rasterised |
| `.gitignore` | Ensure generated `*/index.html` are **not** ignored; they must be committed |
| `robots.txt` | Add `Disallow: /images/diagrams/preview.html` |

---

## 5. SEO specification

### 5.1 Per-page rules (enforced by the builder)

| Element | Rule |
|---|---|
| `<title>` | 50–60 chars. Pattern: `<Specific task or symptom> — <qualifier> \| InoxTV`. Never repeat the same title twice sitewide. |
| `<meta description>` | 140–160 chars, written as a promise of what the reader will be able to do. Unique per page. |
| `<meta keywords>` | **Removed sitewide.** No ranking value, and on an IPTV site it is pure negative signal. |
| `<h1>` | Exactly one, matching search intent, different wording from `<title>` |
| `<h2>` | Every one carries an `id` so it can be deep-linked and feed the TOC |
| Canonical | Absolute, apex domain, trailing slash, self-referencing |
| Breadcrumbs | Visible trail + `BreadcrumbList` JSON-LD |
| Internal links | ≥ 3 outbound to sibling pages, ≥ 2 inbound from others. Descriptive anchor text — never "click here" |
| Images | Every `<img>` has `alt`, explicit `width`/`height` (CLS), `loading="lazy"` below the fold |
| Diagrams | Inline `<svg>` with `<title>` + `<desc>` — the `<desc>` is crawlable text that describes the key map in words |
| Word floor | Features 700 · Guides 900 · Troubleshooting 500 · builder warns below |

### 5.2 Structured data per page type

| Page type | Schema |
|---|---|
| Home | `WebSite` + `Organization` + `SoftwareApplication` ×2 *(exists today — keep)* |
| Guide | `HowTo` + `BreadcrumbList` + `TechArticle` |
| Feature | `TechArticle` + `BreadcrumbList` + `FAQPage` where applicable |
| Troubleshooting | `FAQPage` + `BreadcrumbList` + `TechArticle` |
| Hub | `CollectionPage` + `BreadcrumbList` |
| Policy pages | `WebPage` only |

Validate with the Rich Results Test after the first build of each new type. `FAQPage` rich results are
no longer shown for most sites, but the markup still helps Google understand the page — keep it.

### 5.3 Target queries by section

Write titles against how people actually search. Symptom language beats feature language.

| Section | Query shape | Example |
|---|---|---|
| Troubleshooting | symptom + platform | "iptv buffering android tv fix", "xtream codes login failed" |
| Guides | how-to + object | "how to add m3u playlist android tv", "install iptv player fire tv stick" |
| Features | feature + "how to use" | "android tv multiview how to", "iptv picture in picture" |
| Remote | key + action | "android tv remote long press channel list", "iptv remote button mapping" |

### 5.4 What to leave alone

The current homepage `<head>` is already strong: canonical, OG with typed JPEG and dimensions,
Twitter card, hreflang set, preconnect, WebP preload with `fetchpriority`, GA4, AdSense loader. Keep
all of it; move it into `_layouts/base.html` so all 72 pages inherit it. The only deletion is
`meta name="keywords"`.

---

## 6. Diagram system

The user's instinct is right — for a remote-control app, a picture of the D-pad is worth far more
than a paragraph. Here is exactly what I can and cannot produce.

### 6.1 What I can create, and what needs a screenshot

| Kind | Who makes it | Notes |
|---|---|---|
| **D-pad key maps** | **I create** — hand-authored SVG | Proven: [`images/diagrams/dpad-player.svg`](images/diagrams/dpad-player.svg) already exists and is accurate |
| **Full remote face** | **I create** | Colour buttons, Info, Guide, Menu, RW/FF/Play — for the `/remote/` pages |
| **Mobile gesture maps** | **I create** | Phone outline + tap / long-press / swipe / pinch glyphs |
| **Flow diagrams** | **I create** | e.g. playlist import: Add → Parse → Store → EPG fetch → Play |
| **Comparison diagrams** | **I create** | M3U vs Xtream vs Stalker — what each one needs from you |
| **Settings-path breadcrumbs** | **I create** | Small inline SVG chips: `Settings › Playback › Buffer size` |
| **Screen-anatomy wireframes** | **I create** | Abstract wireframe of a screen region with numbered callouts — no real pixels needed |
| **Real UI screenshots** | **You capture** | I cannot render the actual app UI |
| **Annotated screenshots** | **Hybrid — best option** | You capture the PNG; I overlay an SVG callout layer (numbered pins, arrows, highlight rings) positioned over it |

The hybrid is worth the extra step on the highest-traffic pages: a real screenshot proves the feature
exists, and my callout layer stays editable, translatable, and crawlable as text.

### 6.2 Fix required in the existing diagram

`dpad-player.svg` has a real bug for this site. Its palette defaults to **light**
(`--surface: #FFFFFF`) and only switches to dark inside `@media (prefers-color-scheme: dark)`. When
an SVG is referenced through `<img src>`, that media query resolves against the **viewer's OS
setting**, not the page. InoxTV's site is dark-only (`color-scheme: dark`, `theme-color #0B1020`), so
a visitor on a light-mode OS gets a **white diagram panel on a dark page**.

Two valid fixes — pick one and apply it to every diagram:

1. **Make dark the default** and treat light as the override (`@media (prefers-color-scheme: light)`).
   Keeps `<img>` usage, one file, works everywhere. **Recommended.**
2. **Inline the `<svg>` into the page** so the site's own CSS variables apply. Better for
   theming and for text crawlability, costs page weight and makes reuse across pages manual.

Recommendation: **dark-default palette (fix 1) for the file, and inline it (fix 2) on the one or two
pages where the diagram is the primary content.** The builder can inline on request via a
`"diagram_inline": true` front-matter flag.

### 6.3 The D-pad diagrams have a machine-readable source of truth

This is the key maintainability finding. The default key maps are declared as Kotlin enums with a
`default` field, one per context:

| Context | File | Enum |
|---|---|---|
| Player | `shared/…/player/SettingsRemoteControlPlayerController.kt` | `PlayerKey(storageId, labelRes, default)` |
| TV Guide | `shared/…/player/SettingsRemoteControlTvGuideController.kt` | `TvGuideKey(storageId, labelRes, default)` |
| Movies/Shows | `shared/…/player/SettingsRemoteControlVodController.kt` | `VodKey(storageId, labelRes, default)` |

So every D-pad diagram and every remote-reference table can be **generated and re-verified from the
app source** rather than transcribed by hand. Verified today — the existing `dpad-player.svg` matches
`PlayerKey` exactly (Up = next channel, Long Up = Multiview, Left = channel list overlay, Long Left =
preview mode, Right = most recent channel, Long Right = program description, Down = previous channel,
Long Down = PiP, OK = info + recent, Long OK = menu).

**Maintenance rule:** when a default changes in the app, regenerate the diagram from the enum. Never
edit the SVG labels by hand without checking the enum.

### 6.4 Diagram inventory

| File | Used by | Priority |
|---|---|---|
| `dpad-player.svg` | `/remote/player-keys/`, `/features/live-tv/` | ✅ exists (needs §6.2 fix) |
| `dpad-tv-guide.svg` | `/remote/tv-guide-keys/`, `/features/tv-guide-epg/` | P1 |
| `dpad-vod.svg` | `/remote/vod-keys/`, `/features/movies-and-shows/` | P1 |
| `remote-full-face.svg` | `/remote/` hub | P1 |
| `dpad-multiview.svg` | `/features/multiview/` | P1 |
| `dpad-pip.svg` | `/features/picture-in-picture/` | P1 |
| `flow-playlist-import.svg` | `/guides/choose-playlist-type/` | P0 |
| `compare-playlist-types.svg` | `/guides/choose-playlist-type/` | P0 |
| `flow-epg-update.svg` | `/guides/set-up-tv-guide-epg/`, `/troubleshooting/no-tv-guide-data/` | P0 |
| `flow-firetv-sideload.svg` | `/guides/install-fire-tv-stick/` | P0 |
| `anatomy-player-controls.svg` | `/features/player-controls/` | P1 |
| `anatomy-tv-guide-grid.svg` | `/features/tv-guide-epg/` | P1 |
| `anatomy-sidebar.svg` | `/guides/first-hour-with-inoxtv/` | P1 |
| `gestures-mobile-player.svg` | `/remote/mobile-gestures/` | P2 |
| `decision-buffering.svg` | `/troubleshooting/buffering-and-stuttering/` | P1 |
| `settings-path-*.svg` | inline chips across many pages | P2 |

### 6.5 Diagram authoring standard

Codified so every diagram matches. Full recipe lives in the `inoxtv-website` skill.

- Hand-authored SVG, no editor cruft. `viewBox` + explicit `width`/`height`.
- `role="img"` with `<title>` and a **prose `<desc>` that states every mapping in words** — this is
  the accessible name *and* crawlable SEO text. It is why diagrams help rather than hurt rankings.
- Palette as CSS custom properties in a `<style>` block, dark as the default (§6.2).
- Type: `Outfit, Inter, system-ui, …` to match the site. Minimum 15 px at natural size.
- Press vs **Hold** distinguished by colour *and* label — never colour alone (WCAG).
- Numbered chips on the control, matching a legend, so the prose can reference "①".
- Preview at real size in `images/diagrams/preview.html` before wiring into a page.

---

## 7. AdSense compliance

### 7.1 Required before applying

- **Ownership & contact** — `/about/` names who publishes the site; `/contact/` gives a working email that is monitored. Reviewers check this.
- **Complete policy set** — Privacy (exists), Terms, Disclaimer, DMCA. All four linked from the footer of every page.
- **The AdSense loader stays in `<head>`** on all pages so the crawler can verify the site — it is already there for `ca-pub-6161953663322185`.
- **No ad units on thin or policy pages.** Policy: ads must not appear on pages without publisher content.
- **No ads near the APK button.** Accidental clicks are invalid traffic and can get an account limited.

### 7.2 Ad placement after approval

| Page type | Units | Placement |
|---|---|---|
| Guides / Features / Troubleshooting | max 2 in-article | after the first `<h2>`, and before "Related pages" |
| Hubs | 1 | below the first card group |
| Home | 1 | mid-page, below the features grid |
| About / Contact / Privacy / Terms / DMCA / Disclaimer | **0** | — |
| Fire TV install guide | **0** above the fold | keep all units far from the download button |

Content-to-ad ratio: content must dominate every viewport. Never two units visible at once on mobile.

### 7.3 Ongoing policy hygiene

- Every new page gets read once against §1.2's hard rules before it is committed.
- Never accept guest posts, never add a comments section without moderation, never add a page that lists providers.
- If Google ever sends a policy notice, fix and use the in-console appeal — do not re-apply from scratch.

---

## 8. Content writing standard

A page clears the AdSense bar when a reader with that exact problem leaves able to act. Structure
every content page like this:

1. **Lede (2–3 sentences)** — what this page lets you do, and which platform it applies to.
2. **Where it lives** — the exact path, as a settings-breadcrumb chip: `Settings › Playback › Buffer size`.
3. **Diagram** — D-pad map, flow, or annotated screenshot.
4. **Numbered steps** — one action per step, naming the real on-screen label from `strings.xml`. Never invent UI text.
5. **What each option means** — a table of every value and when to pick it. Reuse the app's own explanatory strings; e.g. buffer size already ships a good explanation in `settings_playback_buffer_size_description`.
6. **Platform differences** — a TV-vs-mobile note wherever behaviour differs.
7. **Troubleshooting table** — symptom → likely cause → fix. Cross-link the dedicated troubleshooting page.
8. **Related pages** — 3 links, from front matter.
9. **Last updated** date, visible.

Rules:

- Use the app's exact wording for every label, copied from `shared/src/main/res/values/strings.xml`. If the site says "Buffer" and the app says "Buffer size", the page is wrong.
- Write in second person, present tense, plain English — the audience includes non-native speakers across 19 app languages.
- No superlatives, no "revolutionary", no filler. Reviewers and readers both discount it.
- Every numeric claim traceable to source (19 languages, 7 dark themes, 3 playlist formats, Downloader code 2910810).

---

## 9. Execution phases

| Phase | Work | Output | Gate |
|---|---|---|---|
| **0 — Policy fix** | Remove meta keywords; purge "free IPTV" / "subscription" wording; add disclaimer band | Homepage safe to show a reviewer | §1.2 rules pass |
| **1 — Build system** | `build.py`, `_layouts/`, `_partials/`, `_data/site.json`; port `index.html` + `privacy.html` onto the layout; fix `check-assets.py` | Existing 2 pages rebuilt byte-comparable | Both pages render identically |
| **2 — Trust pages** | About, Contact, Terms, Disclaimer, DMCA | 7 Tier-0 pages | Linked in every footer |
| **3 — P0 content** | 3 hubs + 9 guides + 5 features + 4 troubleshooting | 28 pages live | Word floors met |
| **4 — Diagrams** | Fix `dpad-player.svg` palette; author the 4 P0 flow/compare diagrams | Diagrams wired into P0 pages | Preview check passes |
| **5 — Index & submit** | Regenerate sitemap, submit, request indexing | ≥ 25 pages indexed | Wait 2–4 weeks |
| **6 — Apply** | Re-apply to AdSense | — | §3.3 checklist fully ticked |
| **7 — Growth** | P1 then P2 pages, `/remote/` section, changelog | 72 pages | ongoing |

Phases 0–2 are small and unblock everything. Phase 3 is the bulk of the effort and is the phase that
actually fixes the rejection.

---

## 10. Maintenance

| Trigger | Action |
|---|---|
| App feature added | Add `content/features/<slug>.html`; link from 2–3 related pages; rebuild |
| Remote default changed in a `*Key` enum | Regenerate the affected `dpad-*.svg` from the enum (§6.3) |
| App string changed | Grep the site for the old label; update every page that quotes it |
| New app version | Add a `/changelog/` entry; bump `updated` on affected pages |
| Any page edit | Bump `updated` in front matter so `sitemap.xml` `lastmod` stays honest |
| Monthly | Search Console: coverage, Core Web Vitals, queries with impressions but no clicks → retitle those pages |

**Never:** edit a generated `index.html` directly — the next build overwrites it. Edit the file in
`content/` or the layout in `_layouts/`.

---

## 11. Open decisions for the owner

1. **Contact email** — `/contact/` needs a real monitored address. Which one?
2. **Publisher identity** — `/about/` should name a person or company for reviewer trust. How much to disclose?
3. **Should `/features/backup-and-restore/` and `/guides/backup-and-restore/` both exist?** Recommendation: keep only the guide, and have the feature slug redirect to it — avoids thin near-duplicate content, which is itself an AdSense risk.
4. **Multi-language site** — the app has 19 languages. Translating the help centre would multiply content, but machine-translated pages are an AdSense risk. Recommendation: English only until approved.
