/* docs.js — help centre behaviour. No dependencies; every page works without it. */
(function () {
  "use strict";

  /* ---- current year in the footer ------------------------------------- */
  var year = document.getElementById("year");
  if (year) year.textContent = new Date().getFullYear();

  /* ---- mobile navigation --------------------------------------------- */
  var toggle = document.getElementById("nav-toggle");
  var nav = document.getElementById("site-nav");

  if (toggle && nav) {
    var setOpen = function (open) {
      nav.classList.toggle("is-open", open);
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    };

    toggle.addEventListener("click", function () {
      setOpen(!nav.classList.contains("is-open"));
    });

    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape" && nav.classList.contains("is-open")) {
        setOpen(false);
        toggle.focus();
      }
    });

    document.addEventListener("click", function (event) {
      if (!nav.classList.contains("is-open")) return;
      if (nav.contains(event.target) || toggle.contains(event.target)) return;
      setOpen(false);
    });

    // A resize past the breakpoint reveals the desktop bar; leaving the panel
    // flagged open would strand aria-expanded on true.
    window.addEventListener("resize", function () {
      if (window.innerWidth > 860 && nav.classList.contains("is-open")) setOpen(false);
    });
  }

  /* ---- table of contents: mark the section being read ----------------- */
  var toc = document.querySelector(".toc");

  if (toc && "IntersectionObserver" in window) {
    var links = {};
    var targets = [];

    Array.prototype.forEach.call(toc.querySelectorAll('a[href^="#"]'), function (link) {
      var target = document.getElementById(decodeURIComponent(link.hash.slice(1)));
      if (!target) return;
      links[target.id] = link;
      targets.push(target);
    });

    if (targets.length) {
      var visible = [];

      var paint = function () {
        var id = visible.length ? visible[0] : null;
        Object.keys(links).forEach(function (key) {
          links[key].classList.toggle("is-active", key === id);
        });
      };

      var observer = new IntersectionObserver(
        function (entries) {
          entries.forEach(function (entry) {
            var id = entry.target.id;
            var at = visible.indexOf(id);
            if (entry.isIntersecting && at === -1) visible.push(id);
            if (!entry.isIntersecting && at !== -1) visible.splice(at, 1);
          });
          // Document order, so the topmost heading on screen wins.
          visible.sort(function (a, b) {
            return document.getElementById(a).offsetTop - document.getElementById(b).offsetTop;
          });
          paint();
        },
        { rootMargin: "-88px 0px -70% 0px", threshold: 0 }
      );

      targets.forEach(function (target) {
        observer.observe(target);
      });
    }
  }

  /* ---- open the FAQ entry a shared link points at --------------------- */
  var openFromHash = function () {
    if (!window.location.hash) return;
    var id = decodeURIComponent(window.location.hash.slice(1));
    var node = document.getElementById(id);
    while (node && node !== document.body) {
      if (node.tagName === "DETAILS") node.open = true;
      node = node.parentNode;
    }
  };

  openFromHash();
  window.addEventListener("hashchange", openFromHash);
})();
