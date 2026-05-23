# InoxTV Website — Production-Ready Implementation Plan

## 1. Project Overview

### 1.1 Purpose
Build a premium, animated, single-page landing website for **InoxTV** — a premium IPTV player application for Android Mobile and Android TV. The website serves as the official online presence, showcasing features point-by-point, and directing users to download the app from Google Play Store.

### 1.2 Technology Stack
| Layer | Technology |
|-------|-----------|
| Structure | HTML5 (semantic) |
| Styling | Vanilla CSS3 (custom properties, keyframes, grid, flexbox) |
| Logic | Vanilla JavaScript (ES6+, Intersection Observer, smooth scroll) |
| Analytics | Google Analytics 4 (GA4) via `gtag.js` |
| SEO | Structured Data (JSON-LD), Open Graph, Twitter Cards, Sitemap XML, robots.txt |
| Hosting | Static hosting (Netlify, Vercel, GitHub Pages, Firebase Hosting, or any CDN) |

### 1.3 Domain & URLs
| Item | Value |
|------|-------|
| Production Domain | `https://www.inoxtv.com` |
| Privacy Policy | `https://sites.google.com/view/inoxtvpolicy` |
| Mobile Play Store | `https://play.google.com/store/apps/details?id=in.inoxtv.mobile` |
| TV Play Store | `https://play.google.com/store/apps/details?id=in.inoxtv.tv` |

---

## 2. Website Architecture

### 2.1 File Structure
```
website/
├── index.html              # Main HTML page (single-page application)
├── style.css               # Complete CSS stylesheet
├── script.js               # JavaScript for animations, interactions, analytics
├── sitemap.xml             # XML sitemap for Google Search Console
├── robots.txt              # Crawler directives
├── manifest.json           # Web app manifest for PWA-lite
├── inoxtv_website_plan.md  # This plan document
└── images/
    ├── logo.png              # App icon (transparent background, square)
    ├── banner.png            # Hero banner with TV mockup
    ├── logo-wide.png         # Wide logo with tagline (transparent bg)
    ├── logo-text.png         # Full logo with text (white bg, for structured data)
    ├── tv-icon.png           # TV launcher icon
    ├── mobile-icon.png       # Mobile launcher icon
    ├── favicon.ico           # Favicon (generated from logo)
    ├── og-image.png          # Open Graph image (1200x630)
    └── apple-touch-icon.png  # Apple touch icon (180x180)
```

### 2.2 Page Sections (Single-Page Layout)
```
┌─────────────────────────────────────────┐
│  ① NAVIGATION BAR (sticky, glassmorphism)│
├─────────────────────────────────────────┤
│  ② HERO SECTION                         │
│  - Animated logo entrance               │
│  - Tagline with typewriter effect       │
│  - CTA buttons (Download Mobile / TV)   │
│  - Animated particle/glow background    │
├─────────────────────────────────────────┤
│  ③ FEATURES SECTION                     │
│  - Animated feature cards (staggered)   │
│  - Icon + title + description per card  │
│  - Scroll-triggered reveal animations   │
│  - 14 key features displayed            │
├─────────────────────────────────────────┤
│  ④ PLATFORM SECTION                     │
│  - Android Mobile showcase              │
│  - Android TV showcase                  │
│  - Side-by-side comparison              │
├─────────────────────────────────────────┤
│  ⑤ PLAYLIST SUPPORT SECTION             │
│  - M3U, Xtream Codes, Stalker Portal   │
│  - Animated cards with hover effects    │
├─────────────────────────────────────────┤
│  ⑥ LANGUAGES SECTION                    │
│  - 18 supported languages grid          │
│  - Animated globe/flag display          │
├─────────────────────────────────────────┤
│  ⑦ DOWNLOAD SECTION (CTA)              │
│  - Google Play badges for both apps     │
│  - Gradient background with animation   │
│  - Direct Play Store links              │
├─────────────────────────────────────────┤
│  ⑧ FOOTER                               │
│  - Privacy Policy link                  │
│  - Copyright notice                     │
│  - Social links (optional)              │
└─────────────────────────────────────────┘
```

---

## 3. Design System

### 3.1 Color Palette
Derived from the InoxTV Android app branding and logo assets:

| Token | Hex | Usage |
|-------|-----|-------|
| `--color-bg-primary` | `#0B1020` | Page background (deep dark blue) |
| `--color-bg-secondary` | `#0A2463` | Section backgrounds |
| `--color-bg-tertiary` | `#1E3A8A` | Card backgrounds, surfaces |
| `--color-accent-blue` | `#3B82F6` | Links, highlights, buttons |
| `--color-accent-pink` | `#E91E90` | Brand pink ("tv" in logo) |
| `--color-accent-purple` | `#8B5CF6` | Gradient midpoint, decorative |
| `--color-accent-magenta` | `#D946EF` | Gradient accents (logo play button) |
| `--color-text-primary` | `#FFFFFF` | Headings, primary text |
| `--color-text-secondary` | `#B0C4DE` | Body text, descriptions |
| `--color-text-muted` | `#64748B` | Footer, captions |
| `--color-surface-glass` | `rgba(255,255,255,0.05)` | Glassmorphism cards |
| `--color-border-glass` | `rgba(255,255,255,0.1)` | Glassmorphism borders |

### 3.2 Typography
```css
/* Primary: Inter (Google Fonts) — clean, modern, excellent readability */
/* Display: Outfit (Google Fonts) — bold headings with character */
font-family: 'Inter', system-ui, -apple-system, sans-serif;
font-family: 'Outfit', 'Inter', sans-serif; /* headings */
```

| Element | Font | Weight | Size (desktop) | Size (mobile) |
|---------|------|--------|---------------|--------------|
| H1 (Hero) | Outfit | 800 | 4rem | 2.5rem |
| H2 (Section) | Outfit | 700 | 2.5rem | 1.8rem |
| H3 (Card) | Inter | 600 | 1.25rem | 1.1rem |
| Body | Inter | 400 | 1rem | 0.95rem |
| Caption | Inter | 400 | 0.875rem | 0.8rem |

### 3.3 Spacing Scale
```
4px → 8px → 12px → 16px → 24px → 32px → 48px → 64px → 96px → 128px
```

### 3.4 Border Radius
| Element | Radius |
|---------|--------|
| Cards | 16px |
| Buttons | 12px |
| Badges | 8px |
| Pill buttons | 999px |

### 3.5 Animations
| Animation | Type | Duration | Trigger |
|-----------|------|----------|---------|
| Logo entrance | Scale + Fade | 1s ease-out | Page load |
| Tagline typewriter | Character reveal | 3s | After logo |
| Feature cards | Slide-up + Fade | 0.6s staggered | Scroll into view |
| Platform cards | Slide-in left/right | 0.8s | Scroll into view |
| Download buttons | Pulse glow | 2s infinite | Always |
| Background particles | Float | 15s infinite | Always |
| Navbar glass | Blur increase | 0.3s | On scroll |
| Feature icons | Bounce | 0.5s | On hover |
| Counter numbers | Count-up | 2s | Scroll into view |

---

## 4. Features Showcase (Point by Point)

Each feature is displayed as an animated card with an SVG icon, title, and description:

| # | Feature | Icon | Description |
|---|---------|------|-------------|
| 1 | **Live TV Channels** | 📺 | Stream thousands of live TV channels in real-time with crystal-clear quality. Supports HD, FHD, and 4K streams. |
| 2 | **Movies & TV Shows** | 🎬 | Browse and watch an extensive library of movies and TV shows with detailed information, ratings, and trailers. |
| 3 | **TV Guide (EPG)** | 📋 | Full electronic program guide showing current, past, and upcoming programs. Never miss your favorite show again. |
| 4 | **Multiview** | 🖥️ | Watch multiple channels simultaneously on a single screen. Perfect for sports fans and news watchers. |
| 5 | **Picture-in-Picture** | 🪟 | Continue watching in a floating window while using other apps. Seamless multitasking experience. |
| 6 | **Voice & Text Search** | 🔍 | Find channels, movies, and shows instantly with powerful voice and text search across all your playlists. |
| 7 | **Multiple Playlist Support** | 📂 | Add and manage multiple IPTV playlists. Supports M3U, Xtream Codes, and Stalker Portal formats. |
| 8 | **Favorites & My List** | ⭐ | Save your favorite channels, movies, and shows for quick access. Create personalized watchlists. |
| 9 | **Recordings** | ⏺️ | Record live TV programs and watch them later at your convenience. Never miss a moment. |
| 10 | **Backup & Restore** | 💾 | Safely backup all your playlists, settings, and preferences. Restore them on any device instantly. |
| 11 | **18 Languages** | 🌍 | Full interface support for 18 languages including English, Hindi, Arabic, French, German, Spanish, and more. |
| 12 | **Parental Controls** | 🔒 | Protect your children with built-in parental controls. Restrict content access with a secure PIN. |
| 13 | **Custom Appearance** | 🎨 | Personalize your experience with theme customization, font size options, and flexible layout settings. |
| 14 | **Auto-Start & Resume** | 🔄 | Auto-start on device boot, resume last channel, and auto-update playlists for a seamless experience. |

---

## 5. SEO Strategy

### 5.1 On-Page SEO

#### Title Tag
```html
<title>InoxTV — Premium IPTV Player for Android Mobile & TV | Live TV, Movies, Shows</title>
```

#### Meta Description
```html
<meta name="description" content="InoxTV is a premium IPTV player for Android Mobile and Android TV. Watch live TV channels, movies, and TV shows with EPG, multiview, PiP, voice search, and 18 language support. Download free from Google Play Store.">
```

#### Meta Keywords
```html
<meta name="keywords" content="InoxTV, IPTV player, Android TV, live TV, IPTV app, M3U player, Xtream Codes, Stalker Portal, EPG, TV guide, multiview, picture in picture, Android IPTV, free IPTV player, premium IPTV">
```

#### Canonical URL
```html
<link rel="canonical" href="https://www.inoxtv.com/">
```

### 5.2 Open Graph Tags (Facebook, LinkedIn, WhatsApp)
```html
<meta property="og:type" content="website">
<meta property="og:url" content="https://www.inoxtv.com/">
<meta property="og:title" content="InoxTV — Premium IPTV Player for Android Mobile & TV">
<meta property="og:description" content="Watch live TV, movies, and shows with the most feature-rich IPTV player. Available for Android Mobile and Android TV.">
<meta property="og:image" content="https://www.inoxtv.com/images/og-image.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:site_name" content="InoxTV">
<meta property="og:locale" content="en_US">
```

### 5.3 Twitter Card Tags
```html
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="InoxTV — Premium IPTV Player for Android Mobile & TV">
<meta name="twitter:description" content="Watch live TV, movies, and shows. Download InoxTV free from Google Play Store.">
<meta name="twitter:image" content="https://www.inoxtv.com/images/og-image.png">
```

### 5.4 Structured Data (JSON-LD)

#### Organization Schema
```json
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "InoxTV",
  "url": "https://www.inoxtv.com",
  "logo": "https://www.inoxtv.com/images/logo.png",
  "description": "Premium IPTV Player for Android"
}
```

#### SoftwareApplication Schema (Mobile)
```json
{
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "name": "InoxTV Mobile",
  "operatingSystem": "Android",
  "applicationCategory": "MultimediaApplication",
  "offers": { "@type": "Offer", "price": "0", "priceCurrency": "USD" },
  "installUrl": "https://play.google.com/store/apps/details?id=in.inoxtv.mobile",
  "description": "Premium IPTV player for Android phones and tablets"
}
```

#### SoftwareApplication Schema (TV)
```json
{
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "name": "InoxTV TV",
  "operatingSystem": "Android TV",
  "applicationCategory": "MultimediaApplication",
  "offers": { "@type": "Offer", "price": "0", "priceCurrency": "USD" },
  "installUrl": "https://play.google.com/store/apps/details?id=in.inoxtv.tv",
  "description": "Premium IPTV player for Android TV"
}
```

#### WebSite Schema (for sitelinks search)
```json
{
  "@context": "https://schema.org",
  "@type": "WebSite",
  "name": "InoxTV",
  "url": "https://www.inoxtv.com"
}
```

### 5.5 Technical SEO Files

#### sitemap.xml
- Lists `https://www.inoxtv.com/` as the primary URL
- `<lastmod>` set to current date
- `<changefreq>monthly</changefreq>`
- `<priority>1.0</priority>`

#### robots.txt
```
User-agent: *
Allow: /
Sitemap: https://www.inoxtv.com/sitemap.xml
```

### 5.6 Performance SEO
- **Preload** critical fonts (Inter, Outfit) via `<link rel="preload">`
- **Lazy load** images below the fold with `loading="lazy"`
- **Preconnect** to Google Fonts and Google Analytics domains
- **Minified** CSS and JS for production
- **Compressed** images (WebP where supported, PNG fallback)
- **Critical CSS** inlined in `<head>` for above-the-fold content

### 5.7 Accessibility (a11y)
- All images have meaningful `alt` text
- ARIA labels on interactive elements
- Keyboard navigable (focus styles)
- Color contrast meets WCAG AA (4.5:1 for text)
- Skip-to-content link
- Semantic HTML5 landmarks (`<header>`, `<main>`, `<nav>`, `<section>`, `<footer>`)

---

## 6. Google Analytics 4 Integration

### 6.1 Setup
```html
<!-- Google Analytics 4 -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-XXXXXXXXXX');
</script>
```

> [!WARNING]
> Replace `G-XXXXXXXXXX` with your actual GA4 Measurement ID from [Google Analytics](https://analytics.google.com/).

### 6.2 Custom Events Tracked
| Event Name | Trigger | Parameters |
|------------|---------|------------|
| `download_click` | Click on any download button | `platform`: "mobile" or "tv" |
| `feature_view` | Feature card scrolls into view | `feature_name`: feature title |
| `section_view` | Any section scrolls into view | `section_name`: section id |
| `privacy_click` | Click on privacy policy link | — |
| `scroll_depth` | User scrolls 25%, 50%, 75%, 100% | `percent`: scroll percentage |
| `cta_click` | Click on any CTA button | `cta_location`: section name |

### 6.3 Google Search Console Setup
1. Add property `https://www.inoxtv.com` in [Google Search Console](https://search.google.com/search-console)
2. Verify ownership via DNS TXT record, HTML file upload, or meta tag
3. Submit `sitemap.xml` URL: `https://www.inoxtv.com/sitemap.xml`
4. Request indexing of the homepage
5. Monitor Core Web Vitals, coverage, and enhancement reports

---

## 7. Google Search Indexing Optimization

### 7.1 Ensuring Proper Display on Google Search

#### Rich Results
- JSON-LD structured data ensures the website appears with rich snippets
- Software Application schema shows app info, download links, and ratings
- Organization schema shows logo in Knowledge Panel

#### Appearance on Google Search
```
InoxTV — Premium IPTV Player for Android Mobile & TV
https://www.inoxtv.com
InoxTV is a premium IPTV player for Android Mobile and Android TV.
Watch live TV channels, movies, and TV shows with EPG, multiview, PiP...
```

### 7.2 Indexing Checklist
- [x] `robots.txt` allows all crawlers
- [x] `sitemap.xml` submitted to Search Console
- [x] Canonical URL set
- [x] No `noindex` tags on pages
- [x] Mobile-friendly responsive design
- [x] Fast page load (< 2s)
- [x] HTTPS enabled (hosting provider)
- [x] Structured data validated with [Rich Results Test](https://search.google.com/test/rich-results)
- [x] Open Graph tags for social sharing
- [x] Unique, descriptive title and meta description

---

## 8. Image Assets Plan

### 8.1 Source Images (from `E:\tivimate apps images\Inoxtv\Chat gpt\`)
| Source File | Usage | Target |
|-------------|-------|--------|
| `ChatGPT_Image_May_19__2026__04_28_58_PM-removebg-preview.png` | App icon/logo | `images/logo.png` |
| `ChatGPT Image May 20, 2026, 03_29_04 AM.png` | Hero banner | `images/banner.png` |
| `expanded_sidebar_image-removebg-preview.png` | Wide logo | `images/logo-wide.png` |
| `ChatGPT Image May 20, 2026, 03_36_05 AM.png` | Text logo | `images/logo-text.png` |
| `192x192_tv_launcher.png` | TV icon | `images/tv-icon.png` |
| `64x64_mobile launcher.png` | Mobile icon | `images/mobile-icon.png` |
| `expanded sidebar image.png` | OG image base | `images/og-image.png` |

### 8.2 Generated Assets Needed
| Asset | Size | Format | Purpose |
|-------|------|--------|---------|
| `favicon.ico` | 32x32 | ICO | Browser tab icon |
| `apple-touch-icon.png` | 180x180 | PNG | iOS home screen |
| `og-image.png` | 1200x630 | PNG | Social sharing preview |

---

## 9. Animations Detail

### 9.1 Page Load Sequence
```
0.0s  → Background gradient animation starts
0.2s  → Navbar fades in
0.5s  → Hero logo scales in with glow
1.0s  → Tagline typewriter starts
1.5s  → Subtitle fades up
2.0s  → CTA buttons slide up with stagger
2.5s  → Scroll indicator bounces
```

### 9.2 Scroll Animations (Intersection Observer)
```javascript
// Each section element gets observed
// When 15% visible → add 'visible' class
// CSS handles the transition:
//   opacity: 0 → 1
//   transform: translateY(40px) → translateY(0)
//   transition: 0.6s ease-out with stagger delay per child
```

### 9.3 Background Effects
- **Floating particles**: 20 semi-transparent circles with random positions and float animations
- **Gradient orbs**: 3 large gradient blobs with slow movement (CSS `@keyframes`)
- **Glow effects**: Radial gradient behind hero content
- **Grid lines**: Subtle perspective grid on hero section

### 9.4 Micro-Interactions
- Button hover: slight scale (1.05), glow shadow increase
- Card hover: translateY(-8px), border glow, icon color shift
- Feature icon: gentle bounce on hover
- Download badge: pulse glow effect
- Navbar: backdrop-filter blur increases on scroll

---

## 10. Responsive Design Breakpoints

| Breakpoint | Range | Layout |
|------------|-------|--------|
| Mobile S | 320px - 480px | Single column, stacked |
| Mobile L | 481px - 768px | Single column, wider padding |
| Tablet | 769px - 1024px | 2-column grid for features |
| Desktop | 1025px - 1440px | 3-column grid, side-by-side sections |
| Desktop XL | 1441px+ | Max-width container, centered |

---

## 11. Deployment Checklist

### 11.1 Pre-Deployment
- [ ] Replace `G-XXXXXXXXXX` with real GA4 Measurement ID
- [ ] Verify all Play Store links work
- [ ] Validate structured data with Google's Rich Results Test
- [ ] Test on mobile devices (responsive)
- [ ] Test on desktop browsers (Chrome, Firefox, Safari, Edge)
- [ ] Run Lighthouse audit (target: 90+ all categories)
- [ ] Compress all images (TinyPNG or equivalent)
- [ ] Test all animations performance (60fps)
- [ ] Verify privacy policy link works

### 11.2 Hosting Setup
1. Choose hosting provider (recommended: **Netlify** or **Firebase Hosting**)
2. Connect custom domain `inoxtv.com`
3. Enable HTTPS (auto-SSL)
4. Configure caching headers:
   ```
   /images/*: Cache-Control: public, max-age=31536000
   /*.css: Cache-Control: public, max-age=604800
   /*.js: Cache-Control: public, max-age=604800
   /index.html: Cache-Control: public, max-age=3600
   ```
5. Enable Brotli/Gzip compression

### 11.3 Post-Deployment
- [ ] Submit sitemap to Google Search Console
- [ ] Verify GA4 is receiving data (Real-time reports)
- [ ] Request indexing in Google Search Console
- [ ] Test Open Graph with Facebook Debugger
- [ ] Test Twitter Card with Twitter Card Validator
- [ ] Monitor Core Web Vitals in Search Console
- [ ] Set up GA4 conversion events for download clicks

---

## 12. Maintenance Plan

| Task | Frequency | Details |
|------|-----------|---------|
| Update Play Store links | On app publish | Verify links resolve correctly |
| Update screenshots | Every major release | Refresh banner/hero images |
| Check analytics | Weekly | Monitor download clicks, bounce rate |
| Review Search Console | Weekly | Fix crawl errors, monitor impressions |
| Update sitemap `lastmod` | On content change | Reflects freshness to crawlers |
| Security headers review | Quarterly | CSP, HSTS, X-Frame-Options |
| Performance audit | Monthly | Lighthouse, Core Web Vitals |

---

## 13. Future Enhancements (Post-Launch)

1. **Blog/News section** — SEO content for organic traffic
2. **FAQ page** — Target long-tail keywords
3. **Changelog page** — Show app update history
4. **Screenshot gallery** — App screenshots carousel
5. **Video demo** — Embedded YouTube walkthrough
6. **Multi-language website** — Match app's 18 languages
7. **PWA support** — Installable web app with service worker
8. **Contact form** — User feedback and support
9. **App review aggregation** — Show Play Store reviews
10. **A/B testing** — Optimize CTA placement and copy

---

## 14. Legal Requirements

- **Privacy Policy** — Linked in footer → `https://sites.google.com/view/inoxtvpolicy`
- **Cookie Consent** — Required if serving in EU (GA4 uses cookies)
- **Terms of Service** — Recommended for production
- **GDPR Compliance** — GA4 configured with `anonymize_ip: true`
- **Copyright** — © 2026 InoxTV. All rights reserved.

---

*Document created: 2026-05-23*
*Last updated: 2026-05-23*
