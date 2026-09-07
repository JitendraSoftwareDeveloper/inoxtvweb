/* =============================================
   InoxTV Website — script.js
   Animations, Gallery, FAQ, Analytics
   ============================================= */

document.addEventListener('DOMContentLoaded', () => {
  initNavbar();
  initEnhancedScrollReveal();
  initMobileNav();
  initSmoothScroll();
  initScrollDepthTracking();
  initDownloadTracking();
  initParallaxScroll();
  assignStaggerIndices();
  initGallery();
  initFAQ();
  initShareButtons();
  initDownloaderCode();
  initFooterYear();
});

/* --- Does the visitor prefer reduced motion? (a11y) --- */
function prefersReducedMotion() {
  return typeof window.matchMedia === 'function' &&
    window.matchMedia('(prefers-reduced-motion: reduce)').matches;
}

/* --- Keep the footer copyright year current --- */
function initFooterYear() {
  const el = document.getElementById('footer-year');
  if (el) el.textContent = new Date().getFullYear();
}

/* --- Assign stagger indices to grid children --- */
function assignStaggerIndices() {
  const grids = document.querySelectorAll('.features-grid, .platform-grid, .playlist-grid, .languages-grid');
  grids.forEach(grid => {
    grid.classList.add('stagger-children');
    Array.from(grid.children).forEach((child, i) => {
      child.style.setProperty('--stagger-index', i);
    });
  });
}

/* --- Navbar Scroll Effect --- */
function initNavbar() {
  const navbar = document.getElementById('navbar');
  if (!navbar) return;
  const onScroll = () => {
    if (window.scrollY > 60) {
      navbar.classList.add('scrolled');
    } else {
      navbar.classList.remove('scrolled');
    }
  };
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();
}

/* --- Enhanced Scroll Reveal — triggers ONCE, no flickering --- */
function initEnhancedScrollReveal() {
  const revealSelectors = '.reveal, .reveal-left, .reveal-right, .reveal-scale, .reveal-blur, .reveal-rotate';
  const reveals = document.querySelectorAll(revealSelectors);
  if (!reveals.length) return;

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');

        // Mark parent section as revealed for glow line + badge pop
        const section = entry.target.closest('.section');
        if (section) section.classList.add('section-revealed');

        // GA4: track section views
        const sectionId = entry.target.closest('section')?.id;
        if (sectionId && entry.target.classList.contains('section-header')) {
          trackEvent('section_view', { section_name: sectionId });
        }
        // GA4: track feature card views
        if (entry.target.classList.contains('feature-card')) {
          const featureName = entry.target.querySelector('h3')?.textContent;
          if (featureName) {
            trackEvent('feature_view', { feature_name: featureName });
          }
        }

        // Stop observing once visible — prevents flickering
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.08, rootMargin: '0px 0px -40px 0px' });

  reveals.forEach(el => observer.observe(el));

  // Also observe sections for the glow-line effect (this one can toggle)
  document.querySelectorAll('.section').forEach(section => {
    const sectionObserver = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('section-revealed');
        }
      });
    }, { threshold: 0.05 });
    sectionObserver.observe(section);
  });
}

/* --- Parallax-lite on scroll --- */
function initParallaxScroll() {
  // JS-driven motion — CSS can't suppress inline transforms, so opt out here.
  if (prefersReducedMotion()) return;
  const heroLogo = document.querySelector('.hero-logo');
  const heroBanner = document.querySelector('.hero-banner');
  const orbs = document.querySelectorAll('.bg-particles .orb');
  if (!heroLogo && !heroBanner && !orbs.length) return;

  let ticking = false;
  window.addEventListener('scroll', () => {
    if (!ticking) {
      requestAnimationFrame(() => {
        const scrollY = window.scrollY;
        const vh = window.innerHeight;

        // Subtle parallax on hero elements — only when hero is visible
        if (scrollY < vh * 1.5) {
          if (heroLogo) heroLogo.style.transform = `scale(1) translateY(${scrollY * 0.12}px)`;
          if (heroBanner) heroBanner.style.transform = `translateY(${scrollY * 0.06}px)`;
        }

        // Shift orbs slightly based on scroll for depth
        orbs.forEach((orb, i) => {
          const speed = 0.02 + i * 0.015;
          orb.style.transform = `translateY(${scrollY * speed}px)`;
        });

        ticking = false;
      });
      ticking = true;
    }
  }, { passive: true });
}

/* --- Mobile Navigation --- */
function initMobileNav() {
  const toggle = document.getElementById('nav-toggle');
  const nav = document.getElementById('navbar-nav');
  if (!toggle || !nav) return;
  toggle.addEventListener('click', () => {
    toggle.classList.toggle('active');
    nav.classList.toggle('open');
    document.body.style.overflow = nav.classList.contains('open') ? 'hidden' : '';
  });
  // Close on link click
  nav.querySelectorAll('a').forEach(link => {
    link.addEventListener('click', () => {
      toggle.classList.remove('active');
      nav.classList.remove('open');
      document.body.style.overflow = '';
    });
  });
  // Close on outside click
  document.addEventListener('click', (e) => {
    if (nav.classList.contains('open') && !nav.contains(e.target) && !toggle.contains(e.target)) {
      toggle.classList.remove('active');
      nav.classList.remove('open');
      document.body.style.overflow = '';
    }
  });
}

/* --- Smooth Scroll for Anchor Links --- */
function initSmoothScroll() {
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', (e) => {
      const targetId = anchor.getAttribute('href');
      if (targetId === '#') return;
      const target = document.querySelector(targetId);
      if (target) {
        e.preventDefault();
        const navHeight = document.getElementById('navbar')?.offsetHeight || 70;
        const top = target.getBoundingClientRect().top + window.scrollY - navHeight;
        window.scrollTo({ top, behavior: prefersReducedMotion() ? 'auto' : 'smooth' });
      }
    });
  });
}

/* --- Scroll Depth Tracking --- */
function initScrollDepthTracking() {
  const milestones = [25, 50, 75, 100];
  const reached = new Set();
  window.addEventListener('scroll', () => {
    const scrollPercent = Math.round(
      (window.scrollY / (document.documentElement.scrollHeight - window.innerHeight)) * 100
    );
    milestones.forEach(m => {
      if (scrollPercent >= m && !reached.has(m)) {
        reached.add(m);
        trackEvent('scroll_depth', { percent: m });
      }
    });
  }, { passive: true });
}

/* --- Downloader App Code Copy (Fire TV section) --- */
function initDownloaderCode() {
  const btn = document.getElementById('downloader-copy-btn');
  if (!btn) return;
  const code = btn.getAttribute('data-code') || '';
  const label = btn.querySelector('span');
  const originalText = label ? label.textContent : '';

  const showCopied = () => {
    if (label) label.textContent = '✓ Copied!';
    btn.classList.add('copied');
    trackEvent('downloader_code_copy', { code });
    setTimeout(() => {
      if (label) label.textContent = originalText;
      btn.classList.remove('copied');
    }, 2000);
  };

  btn.addEventListener('click', () => {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(code).then(showCopied).catch(() => {
        legacyCopy(code);
        showCopied();
      });
    } else {
      legacyCopy(code);
      showCopied();
    }
  });
}

/* --- Clipboard fallback for older browsers --- */
function legacyCopy(text) {
  const input = document.createElement('input');
  input.value = text;
  document.body.appendChild(input);
  input.select();
  document.execCommand('copy');
  document.body.removeChild(input);
}

/* --- Download Button Tracking --- */
function initDownloadTracking() {
  document.querySelectorAll('[data-download]').forEach(btn => {
    btn.addEventListener('click', () => {
      const platform = btn.getAttribute('data-download');
      trackEvent('download_click', { platform });
      trackEvent('cta_click', { cta_location: btn.closest('section')?.id || 'unknown' });
    });
  });
  // Privacy policy click tracking
  document.querySelectorAll('[data-track="privacy"]').forEach(link => {
    link.addEventListener('click', () => {
      trackEvent('privacy_click');
    });
  });
}

/* --- Google Analytics Helper --- */
function trackEvent(eventName, params) {
  if (typeof gtag === 'function') {
    gtag('event', eventName, params || {});
  }
}

/* =============================================
   Screenshot Gallery Slider
   ============================================= */
function initGallery() {
  const galleries = {
    mobile: {
      track: document.getElementById('gallery-track-mobile'),
      dotsContainer: document.getElementById('gallery-dots-mobile'),
      wrapper: document.getElementById('gallery-mobile'),
      currentIndex: 0,
      autoPlayTimer: null,
    },
    tv: {
      track: document.getElementById('gallery-track-tv'),
      dotsContainer: document.getElementById('gallery-dots-tv'),
      wrapper: document.getElementById('gallery-tv'),
      currentIndex: 0,
      autoPlayTimer: null,
    }
  };

  let activeGallery = 'mobile';

  // Calculate visible slides based on screen width
  function getVisibleCount(type) {
    const width = window.innerWidth;
    if (type === 'mobile') {
      if (width <= 768) return 1;
      return 3;
    } else {
      if (width <= 768) return 1;
      return 2;
    }
  }

  function getSlideCount(type) {
    const g = galleries[type];
    if (!g.track) return 0;
    return g.track.children.length;
  }

  function getMaxIndex(type) {
    const total = getSlideCount(type);
    const visible = getVisibleCount(type);
    return Math.max(0, total - visible);
  }

  function updateGallery(type) {
    const g = galleries[type];
    if (!g.track) return;

    const slideWidth = 100 / getVisibleCount(type);
    const offset = -(g.currentIndex * slideWidth);
    g.track.style.transform = `translateX(${offset}%)`;

    // Update dots
    if (g.dotsContainer) {
      const dots = g.dotsContainer.querySelectorAll('.gallery-dot');
      dots.forEach((dot, i) => {
        dot.classList.toggle('active', i === g.currentIndex);
      });
    }

    // Update arrow states
    if (g.wrapper) {
      const leftArrow = g.wrapper.querySelector('.gallery-arrow-left');
      const rightArrow = g.wrapper.querySelector('.gallery-arrow-right');
      if (leftArrow) leftArrow.disabled = g.currentIndex <= 0;
      if (rightArrow) rightArrow.disabled = g.currentIndex >= getMaxIndex(type);
    }
  }

  function createDots(type) {
    const g = galleries[type];
    if (!g.dotsContainer) return;
    g.dotsContainer.innerHTML = '';
    const maxIndex = getMaxIndex(type);
    for (let i = 0; i <= maxIndex; i++) {
      const dot = document.createElement('button');
      dot.className = 'gallery-dot' + (i === 0 ? ' active' : '');
      dot.setAttribute('aria-label', `Go to slide ${i + 1}`);
      dot.addEventListener('click', () => {
        g.currentIndex = i;
        updateGallery(type);
        resetAutoPlay(type);
      });
      g.dotsContainer.appendChild(dot);
    }
  }

  function goNext(type) {
    const g = galleries[type];
    if (g.currentIndex < getMaxIndex(type)) {
      g.currentIndex++;
    } else {
      g.currentIndex = 0; // Loop back
    }
    updateGallery(type);
  }

  function goPrev(type) {
    const g = galleries[type];
    if (g.currentIndex > 0) {
      g.currentIndex--;
    } else {
      g.currentIndex = getMaxIndex(type); // Loop to end
    }
    updateGallery(type);
  }

  function startAutoPlay(type) {
    const g = galleries[type];
    stopAutoPlay(type);
    // Respect the OS "reduce motion" setting — never auto-advance.
    if (prefersReducedMotion()) return;
    g.autoPlayTimer = setInterval(() => {
      goNext(type);
    }, 4000);
  }

  function stopAutoPlay(type) {
    const g = galleries[type];
    if (g.autoPlayTimer) {
      clearInterval(g.autoPlayTimer);
      g.autoPlayTimer = null;
    }
  }

  function resetAutoPlay(type) {
    stopAutoPlay(type);
    startAutoPlay(type);
  }

  // Tab switching
  document.querySelectorAll('[data-gallery-tab]').forEach(tab => {
    tab.addEventListener('click', () => {
      const target = tab.getAttribute('data-gallery-tab');
      activeGallery = target;

      // Update tab styles + expose the active state to screen readers
      document.querySelectorAll('.gallery-tab').forEach(t => {
        t.classList.remove('active');
        t.setAttribute('aria-pressed', 'false');
      });
      tab.classList.add('active');
      tab.setAttribute('aria-pressed', 'true');

      // Show/hide galleries
      Object.keys(galleries).forEach(key => {
        const g = galleries[key];
        if (g.wrapper) {
          g.wrapper.style.display = key === target ? '' : 'none';
        }
        if (key === target) {
          startAutoPlay(key);
        } else {
          stopAutoPlay(key);
        }
      });

      trackEvent('gallery_tab_switch', { tab: target });
    });
  });

  // Arrow buttons
  document.querySelectorAll('[data-gallery-arrow]').forEach(arrow => {
    arrow.addEventListener('click', () => {
      const val = arrow.getAttribute('data-gallery-arrow');
      const [type, dir] = val.split('-');
      if (dir === 'left') goPrev(type);
      else goNext(type);
      resetAutoPlay(type);
    });
  });

  // Touch/swipe support
  Object.keys(galleries).forEach(type => {
    const g = galleries[type];
    if (!g.wrapper) return;
    const container = g.wrapper.querySelector('.gallery-track-container');
    if (!container) return;

    let startX = 0, startY = 0, isDragging = false;

    container.addEventListener('touchstart', (e) => {
      startX = e.touches[0].clientX;
      startY = e.touches[0].clientY;
      isDragging = true;
      stopAutoPlay(type);
    }, { passive: true });

    container.addEventListener('touchend', (e) => {
      if (!isDragging) return;
      isDragging = false;
      const endX = e.changedTouches[0].clientX;
      const endY = e.changedTouches[0].clientY;
      const diffX = startX - endX;
      const diffY = startY - endY;

      // Only handle horizontal swipes (ignore vertical scrolling)
      if (Math.abs(diffX) > 40 && Math.abs(diffX) > Math.abs(diffY)) {
        if (diffX > 0) goNext(type);
        else goPrev(type);
      }
      resetAutoPlay(type);
    }, { passive: true });
  });

  // Pause autoplay on hover, and on keyboard focus (a11y: WCAG 2.2.2)
  Object.keys(galleries).forEach(type => {
    const g = galleries[type];
    if (!g.wrapper) return;
    const resume = () => { if (type === activeGallery) startAutoPlay(type); };
    g.wrapper.addEventListener('mouseenter', () => stopAutoPlay(type));
    g.wrapper.addEventListener('mouseleave', resume);
    g.wrapper.addEventListener('focusin', () => stopAutoPlay(type));
    g.wrapper.addEventListener('focusout', resume);
  });

  // Pause autoplay while the tab is in the background (saves battery/CPU)
  document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
      Object.keys(galleries).forEach(t => stopAutoPlay(t));
    } else {
      startAutoPlay(activeGallery);
    }
  });

  // Initialize
  Object.keys(galleries).forEach(type => {
    createDots(type);
    updateGallery(type);
  });
  startAutoPlay('mobile');

  // Handle resize
  let resizeTimer;
  window.addEventListener('resize', () => {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(() => {
      Object.keys(galleries).forEach(type => {
        const g = galleries[type];
        if (g.currentIndex > getMaxIndex(type)) {
          g.currentIndex = getMaxIndex(type);
        }
        createDots(type);
        updateGallery(type);
      });
    }, 200);
  });
}

/* =============================================
   FAQ Accordion
   ============================================= */
function initFAQ() {
  const faqItems = document.querySelectorAll('.faq-item');
  if (!faqItems.length) return;

  faqItems.forEach(item => {
    const question = item.querySelector('.faq-question');
    if (!question) return;

    question.addEventListener('click', () => {
      const isOpen = item.classList.contains('open');

      // Close all other items (accordion behavior)
      faqItems.forEach(other => {
        if (other !== item && other.classList.contains('open')) {
          other.classList.remove('open');
          const otherBtn = other.querySelector('.faq-question');
          if (otherBtn) otherBtn.setAttribute('aria-expanded', 'false');
        }
      });

      // Toggle current item
      item.classList.toggle('open', !isOpen);
      question.setAttribute('aria-expanded', !isOpen ? 'true' : 'false');

      // Track FAQ interaction
      const questionText = question.querySelector('span')?.textContent;
      if (questionText && !isOpen) {
        trackEvent('faq_open', { question: questionText });
      }
    });
  });
}

/* --- Counter Animation (for stats if added) --- */
function animateCounters() {
  document.querySelectorAll('[data-count]').forEach(el => {
    const target = parseInt(el.getAttribute('data-count'), 10);
    const duration = 2000;
    const start = performance.now();
    const animate = (now) => {
      const progress = Math.min((now - start) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      el.textContent = Math.floor(eased * target);
      if (progress < 1) requestAnimationFrame(animate);
    };
    requestAnimationFrame(animate);
  });
}

/* --- Typewriter Effect (optional enhancement) --- */
function typewriter(element, text, speed = 50) {
  let i = 0;
  element.textContent = '';
  const type = () => {
    if (i < text.length) {
      element.textContent += text.charAt(i);
      i++;
      setTimeout(type, speed);
    }
  };
  type();
}

/* =============================================
   Social Share Buttons
   ============================================= */
function initShareButtons() {
  // A page that is not the home page states its own three values, on whichever
  // of the two share blocks it carries; the defaults below are the home page's.
  const source = document.getElementById('share-buttons-inline') ||
                 document.getElementById('share-float');
  const own = source ? source.dataset : {};
  const shareUrl = own.shareUrl || 'https://inoxtv.com';
  const shareTitle = own.shareTitle || 'InoxTV — IPTV player for Android TV, Fire TV and mobile';
  const shareText = own.shareText || 'InoxTV plays your own M3U, Xtream Codes or Stalker Portal playlist on Android TV, Fire TV and Android phones, with a proper TV guide and remappable remote keys. Free on Google Play.';

  // Build share URLs
  const whatsappUrl = `https://wa.me/?text=${encodeURIComponent(shareText + '\n\n' + shareUrl)}`;
  const redditUrl = `https://www.reddit.com/submit?url=${encodeURIComponent(shareUrl)}&title=${encodeURIComponent(shareTitle)}`;
  const twitterUrl = `https://twitter.com/intent/tweet?text=${encodeURIComponent(shareText)}&url=${encodeURIComponent(shareUrl)}`;
  const facebookUrl = `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(shareUrl)}`;
  const linkedinUrl = `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(shareUrl)}`;
  const telegramUrl = `https://t.me/share/url?url=${encodeURIComponent(shareUrl)}&text=${encodeURIComponent(shareText)}`;
  const emailUrl = `mailto:?subject=${encodeURIComponent(shareTitle)}&body=${encodeURIComponent(shareText + '\n\n' + shareUrl)}`;

  // Apply URLs to all share buttons (both inline and floating)
  const btnMap = [
    { selectors: ['#share-inline-whatsapp', '#share-float-whatsapp'], url: whatsappUrl, platform: 'whatsapp' },
    { selectors: ['#share-inline-reddit', '#share-float-reddit'], url: redditUrl, platform: 'reddit' },
    { selectors: ['#share-inline-twitter', '#share-float-twitter'], url: twitterUrl, platform: 'twitter' },
    { selectors: ['#share-inline-facebook', '#share-float-facebook'], url: facebookUrl, platform: 'facebook' },
    { selectors: ['#share-inline-linkedin', '#share-float-linkedin'], url: linkedinUrl, platform: 'linkedin' },
    { selectors: ['#share-inline-telegram', '#share-float-telegram'], url: telegramUrl, platform: 'telegram' },
    { selectors: ['#share-inline-email', '#share-float-email'], url: emailUrl, platform: 'email' },
  ];

  btnMap.forEach(({ selectors, url, platform }) => {
    selectors.forEach(sel => {
      const el = document.querySelector(sel);
      if (el) {
        el.href = url;
        el.addEventListener('click', (e) => {
          if (platform !== 'email') {
            e.preventDefault();
            window.open(url, '_blank', 'noopener,noreferrer,width=600,height=500');
          }
          trackEvent('share_click', { platform, location: sel.includes('float') ? 'floating_bar' : 'inline_section' });
        });
      }
    });
  });

  // Copy Link — the inline button carries a text label and the floating one is
  // an icon, so the outcome is written to whichever the button actually has,
  // plus a live region for anyone listening rather than looking.
  const status = document.getElementById('share-float-status');

  const copyToClipboard = (text) => {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      return navigator.clipboard.writeText(text);
    }
    // Older browsers, and any page served without a secure context.
    return new Promise((resolve, reject) => {
      const input = document.createElement('input');
      input.value = text;
      input.setAttribute('readonly', '');
      input.style.position = 'fixed';
      input.style.top = '-1000px';
      document.body.appendChild(input);
      input.select();
      let ok = false;
      try { ok = document.execCommand('copy'); } catch (err) { ok = false; }
      document.body.removeChild(input);
      if (ok) resolve(); else reject();
    });
  };

  const wireCopyButton = (btn, location) => {
    if (!btn) return;
    const label = btn.querySelector('span');
    const idle = label ? label.textContent : '';
    let timer = null;
    btn.addEventListener('click', () => {
      copyToClipboard(shareUrl).then(() => {
        btn.classList.add('copied');
        if (label) label.textContent = '✓ Copied!';
        if (status) status.textContent = 'Link copied to the clipboard';
        trackEvent('share_click', { platform: 'copy_link', location });
      }, () => {
        if (label) label.textContent = 'Copy failed';
        if (status) status.textContent = 'Could not copy the link';
      }).then(() => {
        window.clearTimeout(timer);
        timer = window.setTimeout(() => {
          btn.classList.remove('copied');
          if (label) label.textContent = idle;
          if (status) status.textContent = '';
        }, 2000);
      });
    });
  };

  wireCopyButton(document.getElementById('share-inline-copylink'), 'inline_section');
  wireCopyButton(document.getElementById('share-float-copylink'), 'floating_bar');

  // System share sheet — the only route to whatever app the reader actually
  // uses, so it is offered wherever the browser provides one and stays hidden
  // where it does not.
  const wireNativeButton = (btn, location) => {
    if (!btn || !navigator.share) return;
    btn.hidden = false;
    btn.addEventListener('click', () => {
      navigator.share({ title: shareTitle, text: shareText, url: shareUrl }).then(
        () => trackEvent('share_click', { platform: 'system_sheet', location }),
        () => {}  // dismissing the sheet rejects too; nothing to report either way
      );
    });
  };

  wireNativeButton(document.getElementById('share-inline-native'), 'inline_section');
  wireNativeButton(document.getElementById('share-float-native'), 'floating_bar');

  // Floating bar visibility — show after scrolling past hero
  const shareFloat = document.getElementById('share-float');
  if (shareFloat) {
    const hero = document.getElementById('hero');
    let isVisible = false;

    const checkVisibility = () => {
      const threshold = hero ? hero.offsetHeight * 0.7 : 400;
      const shouldShow = window.scrollY > threshold;
      if (shouldShow !== isVisible) {
        isVisible = shouldShow;
        shareFloat.classList.toggle('visible', shouldShow);
      }
    };

    window.addEventListener('scroll', checkVisibility, { passive: true });
    checkVisibility();
  }
}
