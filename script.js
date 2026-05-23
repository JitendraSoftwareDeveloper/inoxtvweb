/* =============================================
   InoxTV Website — script.js
   Animations, Analytics, Interactions
   ============================================= */

document.addEventListener('DOMContentLoaded', () => {
  initNavbar();
  initScrollReveal();
  initMobileNav();
  initSmoothScroll();
  initScrollDepthTracking();
  initDownloadTracking();
});

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

/* --- Scroll Reveal with Intersection Observer --- */
function initScrollReveal() {
  const reveals = document.querySelectorAll('.reveal');
  if (!reveals.length) return;
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        // Track section views in GA4
        const sectionId = entry.target.closest('section')?.id;
        if (sectionId) {
          trackEvent('section_view', { section_name: sectionId });
        }
        // Track feature card views
        if (entry.target.classList.contains('feature-card')) {
          const featureName = entry.target.querySelector('h3')?.textContent;
          if (featureName) {
            trackEvent('feature_view', { feature_name: featureName });
          }
        }
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.15, rootMargin: '0px 0px -40px 0px' });
  reveals.forEach(el => observer.observe(el));
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
