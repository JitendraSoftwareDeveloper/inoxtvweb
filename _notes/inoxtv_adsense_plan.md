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

> **Superseded in part — see §12.** The help centre shipped and the site was rejected again on
> 2026-09-12. The two causes above were real but not the whole set. §12 records what the
> post-launch audit actually found, which was a *deployment* fault rather than a content one:
> the unrendered source fragments were being served as 31 duplicate, navigation-less URLs.

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
├── _content/
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

For every file in `_content/`:

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
1. Create _content/<section>/<slug>.html with front matter + body.
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
| `check-assets.py` | Teach it that `.svg` diagrams are referenced from content fragments too, so scan `_content/**/*.html` as well |
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
| App feature added | Add `_content/features/<slug>.html`; link from 2–3 related pages; rebuild |
| Remote default changed in a `*Key` enum | Regenerate the affected `dpad-*.svg` from the enum (§6.3) |
| App string changed | Grep the site for the old label; update every page that quotes it |
| New app version | Add a `/changelog/` entry; bump `updated` on affected pages |
| Any page edit | Bump `updated` in front matter so `sitemap.xml` `lastmod` stays honest |
| Monthly | Search Console: coverage, Core Web Vitals, queries with impressions but no clicks → retitle those pages |

**Never:** edit a generated `index.html` directly — the next build overwrites it. Edit the file in
`_content/` or the layout in `_layouts/`.

---

## 11. Open decisions for the owner

1. **Contact email** — `/contact/` needs a real monitored address. Which one?
2. **Publisher identity** — `/about/` should name a person or company for reviewer trust. How much to disclose?
3. **Should `/features/backup-and-restore/` and `/guides/backup-and-restore/` both exist?** Recommendation: keep only the guide, and have the feature slug redirect to it — avoids thin near-duplicate content, which is itself an AdSense risk.
4. **Multi-language site** — the app has 19 languages. Translating the help centre would multiply content, but machine-translated pages are an AdSense risk. Recommendation: English only until approved.

---

## 12. Post-launch rejection — 2026-09-12

The help centre from §§2–9 shipped. 38 pages, 33,080 words, policy pages complete, disclaimer band
sitewide, loader in every `<head>`. The application was **rejected again**.

### 12.1 Read the rejection correctly

The notice names **no specific reason**. It says "there are a few things you'll need to adjust" and
links generic help articles. The "insufficient content" line in it is a **"Pro tip"** — boilerplate
present in every one of these mails, not a finding about this site.

**The actual reason is in the AdSense console under Sites → inoxtv.com.** Read that before acting on
anything here. Everything in §12 is what an independent audit found; it is not a transcript of
Google's finding, and the two may not be the same.

### 12.2 Domain age is not a documented blocker

Checked against Google's own eligibility page on 2026-09-12. It lists exactly three requirements:
unique content of your own, policy compliance, and 18+. **No minimum domain age, no waiting period.**

A recollection of a 6-month site-ownership rule for applicants in India and China does **not** appear
on that page and is not asserted here. The domain dates from 2026-05-22 (first commit), so roughly
3.7 months at rejection. New domains attract stricter review in practice, but age is not a stated
criterion and is not worth spending effort on.

### 12.3 What the audit actually found — duplicate source fragments served live

The root cause is a deployment fault, and it is verified, not theorised. Fetched in production:

```
https://inoxtv.com/content/features/live-tv.html  →  200, article body only
```

No header, no navigation, no footer, no canonical tag, no analytics. All **31 fragments** in
`content/` are reachable this way, so every article exists at two URLs:

| | Real page | Served fragment |
|---|---|---|
| URL | `/features/live-tv/` | `/content/features/live-tv.html` |
| Words | 2,043 | 1,466 — 72% of the same text |
| `<link rel=canonical>` | → `/features/live-tv/` | **none** |
| Nav / header / footer | present | **none** |
| In `sitemap.xml` | yes | no |
| Blocked in `robots.txt` | — | **no** |

**45,833 words of duplicated article text** on pages with no way to navigate anywhere, nothing
marking them as secondary, and the front-matter JSON sitting in an HTML comment at the top of each.

**Why it happens.** There is no `.nojekyll`, so GitHub Pages runs Jekyll, which excludes
`_`-prefixed directories — that is why `_data/`, `_layouts/`, `_partials/` and `_notes/` are safely
unserved (`/_notes/inoxtv_adsense_plan.md` → 404, confirmed). `content/` has no underscore, so Jekyll
copies it out verbatim. The fragments have no YAML front matter, so Jekyll passes them through
untouched rather than rendering them.

**Why it is a policy problem.** Google Publisher Policies, *Inventory value*: ads are not permitted
on screens "without publisher-content or with low-value content", nor on screens "used for alerts,
navigation or other behavioral purposes". A reviewer sampling the site can land on one of these. It
is a bare wall of text with no chrome and no exit — precisely that shape. It is also the
near-duplicate content risk already flagged in §11.3, at 31× the scale.

### 12.4 Secondary findings

| Finding | Severity | Detail |
|---|---|---|
| Build scripts downloadable | Low | `build.py`, `check-assets.py`, `convert-webp.py` served at the site root. Not a policy breach; generator source should not be public. |
| `ads.txt` declares app networks | Low–medium | 41 entries / 32 networks, mostly mobile-app SDKs (inmobi, mintegral, smaato, loopme, bidmachine). Those belong in `app-ads.txt` (313 lines, correct). A website's `ads.txt` should declare Google plus genuine *web* sellers. Reviewers do read this file. Owner's call — these lines may be deliberate. |
| `README.md` served | Cosmetic | Repository readme reachable at the site root. |

### 12.5 Fix plan

| # | Action | Rationale |
|---|---|---|
| 1 | Rename `content/` → `_content/`, update `CONTENT` in `build.py` | Jekyll then excludes it exactly as it already excludes `_data/`. Removes 31 duplicate URLs at the source. |
| 2 | Add `_config.yml` with an explicit `exclude:` list | Defence in depth for the `.py` files and `README.md`. Note: an `exclude:` key **replaces** Jekyll's defaults, so the list must restate what it needs. |
| 3 | Extend `audit()` with the checks in §12.6 | The build must fail loudly if this class of fault returns. |
| 4 | Rebuild, re-audit, verify 0 warnings | — |

Deliberately **not** done: trimming `ads.txt`. Those lines may be intentional mediation entries from
the app side, deleting 32 networks is the owner's decision, and an over-broad `ads.txt` is not a
rejection cause. Flagged only.

`robots.txt` `Disallow: /content/` was considered and rejected as the primary fix: it stops crawling
but not direct fetches, so a human reviewer can still open the URL. The rename removes the page.

### 12.6 New permanent build checks

Added to `audit()` so the fault cannot silently return:

- No servable directory outside the `_`-prefixed set contains unrendered fragments.
- Every generated page carries exactly one `<link rel="canonical">`, and it matches its own URL.
- No fragment-shaped file (front-matter comment, no `<html>`) sits anywhere Jekyll would serve it.
- `.nojekyll` does not exist — its presence would start serving every `_` directory.
- Loader in `<head>` on every page; no `data-ad-slot=""`.

### 12.7 Revised re-application gate

Supersedes §3.3, which stays valid but incomplete. Additionally, all of these must be true:

- [ ] `/content/...` returns **404** in production for all 31 paths (check after the deploy, not locally)
- [ ] `/build.py` returns 404
- [ ] `python build.py` reports **no warnings**
- [ ] The console reason under Sites → inoxtv.com has been read and addressed on its own terms
- [ ] Search Console shows no "Duplicate without user-selected canonical" entries for `/content/`
- [ ] Consent messages enabled account-side (GDPR + CCPA), since `privacy.html` §11 asserts they exist

Indexing lag applies to *removal* as well: Google must re-crawl to drop the 31 duplicates. Allow
**2–4 weeks** after the fix before re-applying.

---

## 13. Second full audit — 2026-09-12

Requested after `ads.txt` was finished: check the whole site again for any policy violation or
remaining reason to reject. Method: an independent script over all **38 served HTML files** (stripping
script, style and comments before matching, so it reads what a visitor reads), plus a cross-check of
every feature the homepage claims against the app source at `F:\Projects\Android\inoxtv\app\inoxtv`.

This section is again an **independent audit**, not a transcript of anything Google said. §12.1 still
applies: the notice names no reason, and the console is the only place the real one appears.

### 13.1 What it found

**F1 — The four navigation hubs are link lists (highest priority).** `/remote/` 155 words,
`/troubleshooting/` 176, `/features/` 265, `/guides/` 308. Each is a breadcrumb, one lede sentence,
a search box, and a set of cards. All four are marked `"ads": true` in `_data/site.json`, so they are
ad-bearing screens, and all four are indexable and in the sitemap. That lands on two clauses at once:
*Inventory value* refuses ads on screens "used for alerts, navigation or other behavioral purposes",
and separately on screens "without publisher-content or with low-value content". A hub is the second
clause's own example. It is also the same shape as the first rejection — "insufficient content".

These pages are worth keeping; a grouped index is genuinely useful. They are not worth keeping
**empty**. Fix: give each hub real orientation content — what the section covers, how to choose
between its pages, what to have ready — and hold them to a word floor in the build.

**F2 — The ad loader sits on the policy pages, contradicting the site's own privacy promise.**
`privacy.html` §11 tells visitors: *"Advertising is never placed on this Privacy Policy, on the Terms
of use, on the content disclaimer, or on the copyright and takedown page."* The loader is in the
`<head>` of all four, and of `/about/` and `/contact/` as well. The loader alone renders nothing, so
the sentence holds today only because `ad_slot` is empty — but the automatic units inject into any
page carrying the loader, so the promise depends on an account setting the site cannot see. A false
statement in a privacy policy is a worse problem than the ad it describes, and it is also the shape
reviewers call out. Fix: stop emitting the loader on the policy section and on `/search/`, which makes
the promise true by construction rather than by luck.

**F3 — The homepage advertises a feature the app does not implement.** The Android TV card lists
*"Auto-start on boot"*. `KEY_AUTO_START_ON_BOOT` is written and read **only inside
`SettingsGeneralController`** — no other file in the project touches it, and the only `BOOT_COMPLETED`
receiver in the whole repository is `RecordingBootReceiver`, which re-arms recording alarms rather
than launching the app. So the row exists in Settings and does nothing. This is the inert-feature
class already recorded for Multiview, PiP and catch-up: **check the reader, not the string.**

*Corrected while checking:* SMB **is** implemented — `SmbSetupController`, `SmbSetupBinder`,
`view_smb_setup_overlay.xml`, and the `file_explorer_setup_smb` string — as is the local-playlist file
explorer (`FileExplorerController`). An early grep in this audit missed both because it was run
against the wrong scope; the finding above is from the corrected search. Those two claims stay.

**F4 — "the direct download bypasses the filter"** (`/guides/install-android-tv/`). The sentence
describes Play's hardware filtering accurately, but "bypasses the filter" reads as circumvention to a
classifier that matches wording rather than intent. Cheap to reword; no meaning lost.

**F5 — `/search/` carries the loader** while being `noindex` and a thin results page with no content
of its own. Same fix as F2.

### 13.2 What passed

Recorded so this section is not read as "everything is broken":

| Check | Result |
|---|---|
| `ads.txt` | Single `google.com, pub-6161953663322185, DIRECT` line. Correct. |
| `app-ads.txt` | Holds the app networks. Correct split from `ads.txt`. |
| In-article ad units | **0** — correct before approval |
| Titles / descriptions | 38 unique of 38, both |
| Canonical / `<h1>` | Exactly one of each, per page, every page |
| Real playlist servers | **None.** Every Xtream example is `example.com:8080` or `server:port` |
| Provider or channel names | **None** |
| Privacy policy | 13 sections, 2,314 words, cookies and third-party vendors covered |
| Banned phrasing | 0 after F4. The two hits were "crackling" (audio) and "bypasses" — see §13.1 |
| `robots.txt` | Correct, including the `preview.html` disallow |
| SMB / file explorer / recording | **Implemented** — see the correction under F3 |
| Analytics + loader | In `<head>` on all 38 pages |

Not a violation, worth knowing: there is no `404.html`, so misses land on the host's bare default.
GitHub Pages does not need one, and it is not a rejection cause — but a custom one is cheap and
catches the old `/content/...` paths gracefully while they drain from the index.

### 13.3 Fix plan

| # | Action | Rationale |
|---|---|---|
| 1 | Real orientation content on the four hubs + a hub word floor in `audit()` | F1 — they are the navigation screens the policy names |
| 2 | Stop emitting the loader on `policy` pages and `/search/` | F2/F5 — makes §11 true by construction |
| 3 | Remove "Auto-start on boot" from the homepage card | F3 — unsupported claim |
| 4 | Reword the Play-filter sentence | F4 — reads as circumvention |
| 5 | Update `privacy.html` §11 to name exactly which pages carry no advertising | Keep the promise, the build and the markup in step |

Deliberate consequence of #2: the loader ships on **31 pages instead of 38**. Verification does not
depend on any particular page carrying it, and the exempt set is now the same set the privacy policy
names, so the two cannot drift apart.

This is a **reversal of the earlier "code in the head of every page" instruction**, and it is
deliberate: the site had written a promise that instruction made false. Flagged here rather than
applied quietly, and reversible in one line if the account-side exclusion is preferred instead.

### 13.4 New permanent build checks

- A hub whose orientation content is missing or under its word floor.
- The loader is **present** on every page that is not `policy` and not `/search/`, and **absent** on
  every page that is — checked from one flag so the expectation cannot drift from the emission.
- The banned-phrase list covers the circumvention wording from F4.

### 13.5 Added to the re-application gate

- [ ] Every hub carries real orientation content, not just cards
- [ ] No ad script on any of `/about/`, `/contact/`, `/terms/`, `/disclaimer/`, `/dmca/`,
      `privacy.html`, `/search/`
- [ ] `privacy.html` §11 wording matches the pages that actually carry no advertising
- [ ] The homepage claims no feature the app does not implement

## 14. Implementation of §13 — 2026-09-12

All five actions from §13.3 are in. What follows records what changed, what was verified after the
change, and the two places where checking the source contradicted what §13 had assumed.

### 14.1 The five fixes

**1 — Hub orientation content (F1).** New `_hubs/` directory, one HTML fragment per content section:
`guides.html` (383 words), `features.html` (359), `troubleshooting.html` (378), `remote.html` (416).
Read verbatim by `hub_intro()` and wrapped in `.doc-body.hub-intro`, so the prose takes the article
measure rather than the full page width. Whole-page counts now 695-833 words, against 155-308 before.

`_hubs/` is underscore-prefixed for the same reason `_content/` is: Jekyll never copies it, so the
fragments cannot be served as chrome-less duplicate pages. Verified by the same rule that made
`_notes/` unreachable in production.

The content is orientation, not padding: what to have ready before starting, which of the three
playlist types your credentials imply, why install-then-playlist-then-guide is the order that avoids
rework, how to triage a fault before opening a page, and why the three remote maps differ. Every
cross-link was checked against a page that exists.

**2 — Loader removed from the policy section and `/search/` (F2/F5).** One `carries_ads()` helper,
read by both the renderer and `audit()`, returns False for `section_key == "policy"` and for the
search slug. `PROTECTED_ADS = {"index.html": True, "privacy.html": False}` states the same thing for
the two hand-written pages, which carry no section key for the helper to read. Loader now ships on
**31 pages**, not 38 — the seven that carry no loader are `/about/`, `/contact/`, `/terms/`,
`/disclaimer/`, `/dmca/`, `/search/` and `privacy.html`. Verified absent from each, and present on
the other 31. (`images/diagrams/preview.html` is the one other HTML file in the repository; it is a
noindexed contact sheet for the diagram SVGs, disallowed in `robots.txt`, linked from nowhere, and
not a page — it never carried the loader and is not counted either way.)

**3 — Homepage feature claim (F3).** `<li>Auto-start on boot</li>` removed from the Android TV card
and replaced with `Favourites and My list`, which the app does implement (the favourites table backs
both the channel-list `Favorites` entry and the `My List` sidebar view). The list stays at five items
rather than four.

**4 — Circumvention wording (F4).** The install-android-tv FAQ answer now explains that Play's
hardware list is Play's own and that the published release build is not subject to it. Three entries
added to `BANNED`: `bypass the filter`, `bypasses the filter`, `circumvent the`. Bare `bypass` is
still deliberately absent — the terms page forbids users from circumventing restrictions, which is
the opposite problem, and a false positive would train whoever runs the build to ignore warnings.

**5 — `privacy.html` §11 (F2).** Ad script removed from `<head>` with a comment recording why. §11
now names the six exempt pages explicitly and states that no page loads an advertising script except
the pages that carry advertising. The one-line "Some pages carry advertising" bullet now points to
that list instead of leaving the reader to guess.

### 14.2 Two corrections found while implementing

Both were caught by checking the source rather than by reasoning, and both would have shipped a wrong
statement onto a page:

- **The TV guide's Up and Down keys.** §13.3's draft wording said they "scroll the channel list".
  The page itself says they *move the selection between channels*, and that is why they are not
  remappable. Reworded to match.
- **Backup and restore does carry playlists between devices.** The first draft of the corrected
  homepage FAQ said the two installs do not share playlists and each must be set up by hand. The
  backup guide's own table lists "Playlists, with their type, credentials and per-playlist settings"
  as included, and describes restoring onto a second device as the intended use. Reworded, and the
  JSON-LD answer changed with it so the structured data still matches the visible text.

Separately, the homepage FAQ answer `faq-4` contained "Absolutely!" and "the same powerful feature
set". Rewritten as plain description, and its twin in the `FAQPage` JSON-LD block rewritten to match.

### 14.3 Verification after the change

- `python build.py` — **no warnings**, 31 pages + 4 hubs, 33,080 words.
- `python check-assets.py` — 96 local references resolved, none missing; 8 unreferenced images, all
  pre-existing and all performance rather than policy.
- Loader placement checked per page in both directions by `audit()`; the same check on the two
  hand-written pages by `check_protected()`.
- New content scanned for the usual prose tells and for literal em-dashes; the only em-dashes left
  are pre-existing ones in the two hand-written pages, not introduced here.
- Banned-phrase scan across every served page: clean.

### 14.4 What this does not fix

Restating §13.5 because it is the part most likely to be mistaken for done:

- The **consent-management platform** is still account-side. §11 asserts that EEA, UK and Swiss
  visitors are asked for consent before personalised advertising, and there is still no CMP in the
  page code. That sentence is true only if Google's own consent message is switched on.
- **`ad_slot` is still empty**, so there is no in-article unit anywhere. That stays true until the
  account is approved and an id exists.
- The **rejection reason** in the console has still not been read. This audit is independent of it.

## 15. Consent Mode v2 — 2026-09-12

Closes the gap §14.4 named first: §11 of the privacy policy described a consent behaviour the site
did not implement. It is now implemented in the page code, and the half that cannot live in page
code is written down in §15.4 as an owner action rather than left implied.

### 15.1 Why there is no hand-written banner

The obvious reading of "add a consent message" is to write a cookie banner. That would have been
the wrong build, and worth recording so nobody adds one later.

To serve personalised ads to visitors in the EEA and the UK, Google requires a consent management
platform that is **certified by Google and integrated with the IAB Europe Transparency and Consent
Framework** — EEA since 16 January 2024, UK and Switzerland since 31 July 2024. Certification is a
property of the CMP, not of the banner's wording. A banner written by hand is not certified no
matter how correct its text, so it collects consent that cannot be transmitted in the format the ad
request needs. It looks compliant and changes nothing.

Google's own consent message, configured in the account under **Privacy & messaging**, *is* a
certified CMP (TCF vendor ID 300) and costs nothing. So the work splits in two:

- **In the page code** — Consent Mode v2 defaults, which decide what happens *before* any answer
  exists and what happens if no answer ever arrives. This is §15.2, and it is done.
- **In the account** — the certified message that asks the question. This is §15.4.

The split is clean because the message needs no tag of its own: the existing ad loader delivers it.
There is no third category of work sitting between the two, and no snippet waiting to be pasted in
once the message exists.

### 15.2 What was added to the code

`_partials/consent-mode.html`, included by `_layouts/base.html` and pasted into the two
hand-written pages, sets:

| Signal | EEA / UK / CH | Everywhere else |
|---|---|---|
| `ad_storage` | denied | granted |
| `ad_user_data` | denied | granted |
| `ad_personalization` | denied | granted |
| `analytics_storage` | denied | granted |

plus `wait_for_update: 500`, `url_passthrough`, and `ads_data_redaction`.

Three things about this were verified against Google's documentation rather than assumed:

1. **Order is load-bearing and silent.** `gtag.js` and `adsbygoogle.js` both read the defaults when
   they initialise. A consent block placed after either one parses fine, throws nothing, and has no
   effect. The block therefore sits above both in every `<head>`, and `check_consent()` compares
   offsets rather than checking presence, because presence is not the failure mode.
2. **`"EEA"` is not a region value.** `region` takes ISO 3166-2 codes, so the 27 member states are
   enumerated, plus IS, LI and NO, plus GB and CH. An earlier draft of this used `'EEA'`, which
   would have silently matched no one and left the whole EEA on the granted default.
3. **Specificity resolves the two defaults, not source order.** The regional command wins for the
   countries it names because it is more specific, and the command with no region covers everyone
   it does not name.

Denying by default outside those regions was considered and rejected: consent is not the legal
basis for measurement there, and it would suppress analytics for visitors who were never asked.

### 15.3 Keeping the three copies in step

`index.html` and `privacy.html` are `PROTECTED` — hand-written, never rendered through the layout,
so `{% include %}` cannot reach them and each holds a pasted copy. Pasted copies drift: the next
edit to the region list would leave the homepage on the old one, and nothing would report it.

`check_consent()` in `build.py` compares each pasted copy against `_partials/consent-mode.html`
ignoring indentation, and fails the build when they diverge. All three failure modes were tested by
deliberately breaking the input and confirming the warning fires:

| Break | Warning |
|---|---|
| Changed `wait_for_update` in the partial only | both hand-written pages reported as no longer matching |
| Moved `gtag.js` above the include in the layout | 36 pages reported as "read too late to apply" |
| Deleted the block from `index.html` | "loads Google script with no consent defaults in `<head>`" |

Restored after each, and the build returns to no warnings.

### 15.4 Owner action — publish the consent message

**No code is involved, and none is missing.** Google's Funding Choices reference is explicit that
publishers "don't need to re-tag at all" because "your existing Google Publisher Tag or AdSense tag
deploys user messages once the message is published". The loader is already on all 31 content
pages, so the delivery mechanism is in place and the message appears the moment it exists in the
account. Nothing can be added to this repository to bring that date forward — the message is
created behind a Google sign-in, and it is the account, not the site, that holds it.

**It is not an approval gate.** The published eligibility criteria are original content that meets
the programme policies, an owner aged 18 or over, and access to the site's HTML. No CMP, consent
message or cookie banner appears among them. The CMP requirement governs *serving personalised ads*
in the EEA, UK and Switzerland after approval — a revenue condition, not a review condition. The
site can be submitted for review before this is done.

What being un-published actually costs, while it is un-published:

- EEA/UK/CH visitors are never asked, so consent is never granted, so `ad_storage`,
  `ad_user_data`, `ad_personalization` and `analytics_storage` stay denied for them.
- Ads still serve there, non-personalised, at a lower rate. Revenue from those regions is reduced,
  not zero.
- Nothing on the site becomes untrue: §11 was reworded so the promise rests on the denied-by-default
  behaviour, which the code guarantees on its own.

In the account: **Privacy & messaging → European regulations → Manage → create the message → select
all sites → Publish.**

To confirm it afterwards, append Google's own debug parameters to any content page — no EEA IP or
VPN needed:

```
https://inoxtv.com/guides/add-m3u-playlist/?fc=alwaysshow&fctype=gdpr
```

The message must already be published to the site for that to render anything.

**The seven exempt pages will not show the message**, because they deliberately do not load the ad
script: `privacy.html`, `/terms/`, `/dmca/`, `/disclaimer/`, `/about/`, `/contact/`, `/search/`.
Adding the loader to them purely to carry the message would put an ad script back on the pages whose
own text promises there is none, and Auto ads could then place a unit there. The consent defaults
still apply on those pages — an EEA visitor who lands on one stores nothing — so the trade is a
visitor who is not *asked* on a policy page, against a policy page that contradicts itself. The
first is better, and it is why `check_protected()` enforces the absence.

### 15.5 Privacy policy changes that went with it

§11 asserted that visitors "are asked for consent before personalised advertising or non-essential
measurement cookies are used". That was a claim about a message that did not exist yet.

It now leads with what the code does — cookies are switched off before any Google script is allowed
to run, and stay off unless consented to — and describes the notice as the way consent is given.
The measurement bullet gained the same qualifier. Effective date moved to 12 September 2026, since
the substance changed and not just the wording.

### 15.6 Verification

- `python build.py` — no warnings, 31 pages + 4 hubs, 33,080 words.
- `python check-assets.py` — MISSING: none.
- Consent block confirmed ahead of both `gtag.js` and the ad loader by byte offset, not by eye, on
  every served page: 39 HTML files in the tree, 38 carrying the block and `gtag.js`, 31 of those
  also carrying the ad loader, 0 ordering violations. The 39th is
  `images/diagrams/preview.html`, the noindexed local contact sheet, which loads no Google script
  at all and correctly has no block.
- The two hand-written pages re-indented to two spaces to match their own heads, and the duplicated
  `window.dataLayer` / `function gtag()` pair removed — the consent block already defines both, and
  redefining them after it would have reset the queue.

### 15.7 What is still open after this

Nothing in the repository. Every item below is an account action or a post-approval step, and none
of them blocks submitting the site for review.

- **Publish the consent message** (§15.4). Affects EEA/UK/CH ad rates, not approval. No code.
- **`ad_slot` is still empty**, so there is no in-article unit. It cannot be filled until an
  approved account can create a unit and hand back an id. Unchanged from §14.4.
- **The console rejection reason has still not been read.** Unchanged from §14.4, and still the one
  input that could contradict this whole audit.

---

## 16. AI-footprint audit — 2026-09-13

The owner's question was direct: does this site read as machine-produced, and if so, remove every
trace. Worth stating the actual risk precisely, because it is not the one the question implies.

There is no rule that AI-assisted content is refused. The policy that bites is **scaled content
abuse**, and it is about content produced at volume with little value, whatever produced it. A human
writing thirty near-identical pages from a template trips it; a carefully written page does not
become ineligible because a tool helped. So the thing to remove is not "evidence of a tool" but
**anything that reads as unconsidered** — and the second is the one a reviewer actually sees.

That reframing decided what to change and what to leave. Every edit below made the prose better on
its own terms. Nothing was changed merely to defeat a detector.

### 16.1 What was checked, and what was clean

| Category | Method | Result |
|---|---|---|
| Vocabulary | 37 tell-words across all rendered pages | **0 hits** |
| Filler constructions | 13 patterns: "not just X, it's Y", "more than just", "that's where", "under the hood", "peace of mind" … | 2 hits, both ordinary English in context, kept |
| Generator traces | `generated`, model and vendor names, `meta name="generator"`, SVG editor metadata, EXIF | 4 hits of "generated", **all legitimate** — an M3U link *generated by an Xtream Codes panel*, an EPG *generated alongside your playlist*, key tables *generated from the app's own key definitions* |
| Structural uniformity | word count, h2 count, FAQ count, HowTo step count per page | Genuine spread: 648–2003 words (median 991), 5 distinct h2 counts, FAQ 3–6, steps 0–7 |
| Sentence rhythm | mean and sd of sentence length, per page | Page means 13.5–22.0 words; within-page sd 7.6–31.2; sentences from 3 to 230 words |
| FAQ schema vs visible copy | 125 pairs across 36 pages, plus 12 on the homepage | **0 mismatches** |
| `updated` dates | checked against git rather than assumed | Uniform date is honest; only one fragment had changed since the commit |

The sentence-rhythm figures are the ones worth keeping. Machine-written prose clusters near 15–20
words with low deviation because it defaults to one clause shape. A within-page spread of 7.6 to
31.2, with real three-word sentences and a 230-word table-derived one, is not that.

### 16.2 The em-dash sweep

The one real habit found. 212 in the tree:

- **51 kept.** Inside `<li>` and `<td>`, separating a term from its gloss — "Large — for a source
  that stalls". That is what the mark is for, and stripping it would have made those tables worse.
- **161 repaired**, taking running prose to zero.

Repairs were rotated rather than substituted, because replacing every dash with one other mark swaps
one uniform habit for another. Each was classified by the job it was doing: full stop or semicolon
for an independent clause, colon where what follows is a gloss or a list, comma for a subordinate
clause or an appositive, parentheses for a genuine aside. A one-off script did the bulk; every
result was diffed and 8 comma splices it introduced were fixed by hand.

Three passes were needed, and the reason is worth recording: **a source-only scan misses the front
matter.** The `card`, `lede` and `faq` fields are JSON, not markup, so they carry literal `—` rather
than `&mdash;` and never matched the first sweep — but they render into the page, the hub cards and
the JSON-LD. 20 were caught this way on 15 files, and only because the new guard flagged a rendered
page the source sweep had called clean.

### 16.3 What was deliberately kept

- **The 19 `.feature-icon` emoji.** A CSS-driven icon system, consistent sitewide. The one inline 💡
  in a homepage paragraph was removed — that one was decoration inside prose.
- **`<title>` separators** on `index.html` and `privacy.html`. A separator between a name and a
  descriptor in a 55-character title is typographic convention, not a sentence. `check_tells()` was
  taught to skip the title line rather than the titles being damaged to satisfy it.
- **"unlock"**, which on this site means the parental PIN.
- The **one `<td>` dash** in `troubleshooting/buffering-and-stuttering`, glossing a table term.

### 16.4 Permanent guards added to `build.py`

Both run on every build, for generated and hand-written pages alike:

- **`TELLS`** — 37 phrases, warned on if they appear in rendered text.
- **`check_tells()`** — the phrase scan plus an em-dash **rate**, `TELL_DASH_RATE = 3.0` per thousand
  words, ignoring list rows, table cells and `<title>`. A rate rather than a count, so a long page is
  not penalised for one dash and a short one cannot hide three.

Wired into **both** `audit()` and `check_protected()`. The second call is what makes it cover
`index.html` and `privacy.html`, and it is what caught the front-matter class of miss.

### 16.5 Verification

- `python build.py` — **no warnings**. 31 pages + 4 hubs, 32,948 words.
- `python check-assets.py` — MISSING: none.
- Prose em-dashes across all 38 served HTML files: **0**.
- 125 FAQ pairs verified present in the visible markup, plus the homepage's 12: **0 mismatches**.
- The two one-off scripts (`vary_dashes.py`, `check_faq_parity.py`) deleted. The permanent checks
  live in `build.py`.

### 16.6 The honest limit of this

No scan proves a negative. What can be said is specific: the measurable habits are gone, the
structural variation is real rather than simulated, and the site carries the kind of detail only
someone with the source open could write — the Downloader code, `00:1a:79:00:00:00` as a prefix and
not an account, four simultaneous recordings, one and a half seconds to first frame on every buffer
preset, `Assign EPG` present in the menu but not wired.

That last category is the actual defence, and it is the one a detector cannot fake in either
direction. It is also why §13's rule stands: **write from the app's source, not from what an IPTV
help page usually says.**
