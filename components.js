/* Monarch Digital shared behavior: header, navigation, reveal, forms, blog filter. */
(function () {
  'use strict';

  var RECAPTCHA_SITE_KEY = '6Lck8aQsAAAAALMA-T6nwfkSf7bv4K-mOhkszeKh';
  var FORM_ENDPOINT = 'https://myaieditor.com/api/form-notify';
  var PAGE_LOADED_AT = Date.now();

  // reCAPTCHA loads only when someone starts filling in a form, so pages stay fast.
  var recaptchaRequested = false;
  function ensureRecaptcha() {
    if (recaptchaRequested || typeof grecaptcha !== 'undefined') return;
    recaptchaRequested = true;
    var s = document.createElement('script');
    s.src = 'https://www.google.com/recaptcha/api.js?render=' + RECAPTCHA_SITE_KEY;
    s.async = true;
    document.head.appendChild(s);
  }

  // Always resolves: an empty string on any failure or after 8 seconds, so the
  // POST still goes out and form-notify can log a missing token for rescue.
  function getRecaptchaToken(action) {
    ensureRecaptcha();
    var attempt = new Promise(function (resolve) {
      var started = Date.now();
      (function wait() {
        if (typeof grecaptcha !== 'undefined' && typeof grecaptcha.execute === 'function') {
          try {
            grecaptcha.ready(function () {
              grecaptcha.execute(RECAPTCHA_SITE_KEY, { action: action || 'form_submit' })
                .then(function (t) { resolve(t || ''); }, function () { resolve(''); });
            });
          } catch (e) { resolve(''); }
        } else if (Date.now() - started < 7000) {
          setTimeout(wait, 150);
        } else {
          resolve('');
        }
      })();
    });
    var timeout = new Promise(function (resolve) { setTimeout(function () { resolve(''); }, 8000); });
    return Promise.race([attempt, timeout]);
  }

  // Shared with the AI assessment page.
  window.MonarchForms = { ensureRecaptcha: ensureRecaptcha, getRecaptchaToken: getRecaptchaToken, endpoint: FORM_ENDPOINT, loadedAt: PAGE_LOADED_AT };

  function initHeader() {
    var header = document.getElementById('header');
    if (!header) return;
    var onScroll = function () { header.classList.toggle('scrolled', window.scrollY > 12); };
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
  }

  function initMobileNav() {
    var btn = document.getElementById('hamburger');
    var panel = document.getElementById('mobileNav');
    if (!btn || !panel) return;
    function setOpen(open) {
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
      panel.classList.toggle('active', open);
      document.body.style.overflow = open ? 'hidden' : '';
    }
    btn.addEventListener('click', function () { setOpen(btn.getAttribute('aria-expanded') !== 'true'); });
    panel.querySelectorAll('a').forEach(function (a) { a.addEventListener('click', function () { setOpen(false); }); });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape') setOpen(false); });
  }

  function initDropdown() {
    document.querySelectorAll('.nav-drop').forEach(function (drop) {
      var btn = drop.querySelector('button');
      if (!btn) return;
      btn.addEventListener('click', function (e) {
        e.stopPropagation();
        var open = !drop.classList.contains('open');
        drop.classList.toggle('open', open);
        btn.setAttribute('aria-expanded', open ? 'true' : 'false');
      });
      document.addEventListener('click', function (e) {
        if (!drop.contains(e.target)) { drop.classList.remove('open'); btn.setAttribute('aria-expanded', 'false'); }
      });
      document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') { drop.classList.remove('open'); btn.setAttribute('aria-expanded', 'false'); }
      });
    });
  }

  function initReveal() {
    var items = document.querySelectorAll('.reveal');
    if (!items.length) return;
    var showAll = function () { items.forEach(function (el) { el.classList.add('in'); }); };
    if (!('IntersectionObserver' in window)) { showAll(); return; }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) { entry.target.classList.add('in'); io.unobserve(entry.target); }
      });
    }, { threshold: 0.08, rootMargin: '0px 0px -40px 0px' });
    items.forEach(function (el) { io.observe(el); });
    // Failsafe: never leave content hidden (embedded previews, print, odd viewports).
    setTimeout(showAll, 2500);
  }

  function initForms() {
    document.querySelectorAll('form[data-ajax]').forEach(function (form) {
      form.addEventListener('focusin', ensureRecaptcha, { once: true });
      form.addEventListener('input', ensureRecaptcha, { once: true });
      form.addEventListener('submit', function (e) {
        e.preventDefault();
        var honey = form.querySelector('[name="_honey"]');
        if (honey && honey.value) return;
        var btn = form.querySelector('[type="submit"]');
        var fields = form.querySelector('.form-fields');
        var success = form.querySelector('.form-success');
        var failure = form.querySelector('.form-error');
        var label = btn ? btn.textContent : '';
        if (btn) { btn.disabled = true; btn.textContent = 'Sending...'; }
        if (failure) failure.classList.remove('show');
        var formType = (form.querySelector('[name="form_type"]') || {}).value || 'contact';

        getRecaptchaToken(formType.replace(/[^a-z_]/gi, '_')).then(function (token) {
          var tokenField = form.querySelector('[name="recaptcha_token"]');
          if (tokenField) tokenField.value = token;
          var data = {};
          new FormData(form).forEach(function (v, k) { data[k] = v; });
          data._ts = String(PAGE_LOADED_AT);
          return fetch(FORM_ENDPOINT, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
          }).then(function (res) {
            return res.json().catch(function () { return {}; }).then(function (body) {
              return res.ok && body.accepted !== false;
            });
          });
        }).catch(function () { return false; }).then(function (accepted) {
          if (accepted) {
            if (fields) fields.style.display = 'none';
            if (success) success.classList.add('show');
            window.dataLayer = window.dataLayer || [];
            window.dataLayer.push({ event: 'form_submission', form_type: formType, form_location: window.location.pathname });
          } else {
            if (failure) failure.classList.add('show');
            if (btn) { btn.disabled = false; btn.textContent = label; }
          }
        });
      });
    });
  }

  function initBlogFilter() {
    var wrap = document.getElementById('blogFilters');
    if (!wrap) return;
    wrap.querySelectorAll('.filter-btn').forEach(function (btn) {
      btn.addEventListener('click', function () {
        wrap.querySelectorAll('.filter-btn').forEach(function (b) { b.classList.remove('active'); b.setAttribute('aria-pressed', 'false'); });
        btn.classList.add('active');
        btn.setAttribute('aria-pressed', 'true');
        var filter = btn.getAttribute('data-filter');
        document.querySelectorAll('#postGrid .post-card').forEach(function (card) {
          card.style.display = (filter === 'all' || card.getAttribute('data-cat') === filter) ? '' : 'none';
        });
      });
    });
  }

  function boot() {
    initHeader();
    initMobileNav();
    initDropdown();
    initReveal();
    initForms();
    initBlogFilter();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot); else boot();
})();
