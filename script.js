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
});

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
        window.scrollTo({ top, behavior: 'smooth' });
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

      // Update tab styles
      document.querySelectorAll('.gallery-tab').forEach(t => t.classList.remove('active'));
      tab.classList.add('active');

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

  // Pause autoplay on hover
  Object.keys(galleries).forEach(type => {
    const g = galleries[type];
    if (!g.wrapper) return;
    g.wrapper.addEventListener('mouseenter', () => stopAutoPlay(type));
    g.wrapper.addEventListener('mouseleave', () => {
      if (type === activeGallery) startAutoPlay(type);
    });
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
  const shareUrl = 'https://inoxtv.com';
  const shareTitle = 'InoxTV — Premium IPTV Player for Android';
  const shareText = 'Check out InoxTV! The most powerful IPTV player for Android Mobile & TV. Watch live TV, movies, and shows with a premium experience. Download free from Google Play Store!';

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

  // Copy Link button handler
  const copyBtn = document.getElementById('share-inline-copylink');
  if (copyBtn) {
    copyBtn.addEventListener('click', () => {
      navigator.clipboard.writeText(shareUrl).then(() => {
        const label = copyBtn.querySelector('span');
        const originalText = label.textContent;
        label.textContent = '✓ Copied!';
        copyBtn.classList.add('copied');
        trackEvent('share_click', { platform: 'copy_link', location: 'inline_section' });
        setTimeout(() => {
          label.textContent = originalText;
          copyBtn.classList.remove('copied');
        }, 2000);
      }).catch(() => {
        // Fallback for older browsers
        const input = document.createElement('input');
        input.value = shareUrl;
        document.body.appendChild(input);
        input.select();
        document.execCommand('copy');
        document.body.removeChild(input);
        const label = copyBtn.querySelector('span');
        label.textContent = '✓ Copied!';
        copyBtn.classList.add('copied');
        setTimeout(() => {
          label.textContent = 'Copy Link';
          copyBtn.classList.remove('copied');
        }, 2000);
      });
    });
  }

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
