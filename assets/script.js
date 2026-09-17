/* ============================================================
   TacBrokers — demonstration site
   Language state lives in this variable and nowhere else:
   no localStorage, no sessionStorage, no cookies.
   ============================================================ */
(function () {
  'use strict';

  var lang = 'en';                                  /* in-memory only */

  var TITLES = {
    en: 'TacBrokers — One account to invest, save, get paid and pay',
    ar: 'تاك بروكرز — حساب واحد تستثمر وتدخر وتقبض وتدفع منه'
  };

  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)');

  /* ---------------------------------------------- language ---- */
  var langBtn   = document.querySelector('[data-lang-toggle]');
  var langLabel = document.querySelector('[data-lang-label]');

  function applyLang(next) {
    lang = next;
    var isAr = lang === 'ar';
    var html = document.documentElement;

    html.setAttribute('lang', isAr ? 'ar' : 'en');
    html.setAttribute('dir', isAr ? 'rtl' : 'ltr');
    document.title = TITLES[lang];

    var key = 'data-' + lang;
    var i, els, val;

    els = document.querySelectorAll('[data-en]');
    for (i = 0; i < els.length; i++) {
      val = els[i].getAttribute(key);
      if (val !== null) { els[i].textContent = val; }
    }

    els = document.querySelectorAll('[data-en-placeholder]');
    for (i = 0; i < els.length; i++) {
      val = els[i].getAttribute(key + '-placeholder');
      if (val !== null) { els[i].setAttribute('placeholder', val); }
    }

    els = document.querySelectorAll('[data-en-aria]');
    for (i = 0; i < els.length; i++) {
      val = els[i].getAttribute(key + '-aria');
      if (val !== null) { els[i].setAttribute('aria-label', val); }
    }

    if (langLabel) {
      langLabel.textContent = isAr ? 'English' : 'العربية';
      langLabel.setAttribute('lang', isAr ? 'en' : 'ar');
    }
  }

  if (langBtn) {
    langBtn.addEventListener('click', function () {
      applyLang(lang === 'en' ? 'ar' : 'en');
    });
  }

  /* --------------------------------------------- mobile nav ---- */
  var navBtn = document.querySelector('[data-nav-toggle]');
  var nav    = document.querySelector('[data-nav]');

  function setNav(open) {
    if (!nav || !navBtn) { return; }
    nav.classList.toggle('is-open', open);
    navBtn.setAttribute('aria-expanded', open ? 'true' : 'false');
  }

  if (navBtn && nav) {
    navBtn.addEventListener('click', function () {
      setNav(navBtn.getAttribute('aria-expanded') !== 'true');
    });

    nav.addEventListener('click', function (e) {
      if (e.target.closest('a')) { setNav(false); }
    });

    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && navBtn.getAttribute('aria-expanded') === 'true') {
        setNav(false);
        navBtn.focus();
      }
    });

    document.addEventListener('click', function (e) {
      if (navBtn.getAttribute('aria-expanded') !== 'true') { return; }
      if (!e.target.closest('.tb-head')) { setNav(false); }
    });

    window.matchMedia('(min-width: 901px)').addEventListener('change', function (m) {
      if (m.matches) { setNav(false); }
    });
  }

  /* ------------------------------------------ header shadow ---- */
  var head = document.querySelector('.tb-head');
  var ticking = false;

  function onScroll() {
    if (ticking) { return; }
    ticking = true;
    window.requestAnimationFrame(function () {
      if (head) { head.classList.toggle('is-stuck', window.scrollY > 6); }
      ticking = false;
    });
  }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  /* ------------------------------------------ scroll reveal ---- */
  var reveals = document.querySelectorAll('.tb-reveal');

  function showAll() {
    for (var i = 0; i < reveals.length; i++) { reveals[i].classList.add('is-in'); }
  }

  if (reduced.matches || !('IntersectionObserver' in window)) {
    showAll();
  } else {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-in');
          io.unobserve(entry.target);
        }
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });

    for (var r = 0; r < reveals.length; r++) { io.observe(reveals[r]); }
  }

  /* --------------------------------------------- chat widget ---
     Buttons marked data-open-chat ask the AI widget to open.
     The widget snippet can listen for the event below, or expose
     an open() method, or simply render its own launcher.        */
  function openChat() {
    var ev;
    try {
      ev = new CustomEvent('tacbrokers:open-chat', { bubbles: true, cancelable: true });
    } catch (err) {
      ev = document.createEvent('CustomEvent');
      ev.initCustomEvent('tacbrokers:open-chat', true, true, null);
    }
    document.dispatchEvent(ev);
    if (ev.defaultPrevented) { return; }

    var api = window.TactfulChat || window.Tactful || window.tactful;
    if (api && typeof api.open === 'function') { api.open(); return; }

    var launcher = document.querySelector(
      '[data-tactful-launcher], #tactful-launcher, .tactful-launcher'
    );
    if (launcher) { launcher.click(); return; }

    var support = document.getElementById('support');
    if (support) {
      support.scrollIntoView({
        behavior: reduced.matches ? 'auto' : 'smooth',
        block: 'center'
      });
    }
  }

  var chatBtns = document.querySelectorAll('[data-open-chat]');
  for (var c = 0; c < chatBtns.length; c++) {
    chatBtns[c].addEventListener('click', openChat);
  }
})();
