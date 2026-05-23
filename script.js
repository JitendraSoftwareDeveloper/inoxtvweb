/* =============================================
   InoxTV Website — script.js
   Animations, Analytics, Interactions
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

/* --- Enhanced Scroll Reveal with Bi-directional Animations --- */
function initEnhancedScrollReveal() {
  const revealSelectors = '.reveal, .reveal-left, .reveal-right, .reveal-scale, .reveal-blur, .reveal-rotate';
  const reveals = document.querySelectorAll(revealSelectors);
  if (!reveals.length) return;

  // Observe elements — animate in when scrolling into view,
  // reset when scrolling out so they re-animate on return
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
      } else {
        // Reset when element leaves viewport — enables re-animation on scroll back
        entry.target.classList.remove('visible');
      }
    });
  }, { threshold: 0.12, rootMargin: '0px 0px -60px 0px' });

  reveals.forEach(el => observer.observe(el));

  // Also observe sections for the glow-line effect
  document.querySelectorAll('.section').forEach(section => {
    const sectionObserver = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('section-revealed');
        } else {
          entry.target.classList.remove('section-revealed');
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
