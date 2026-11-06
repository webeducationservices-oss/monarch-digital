/* Free AI Restaurant Assessment: multi-step form, lead capture, AI report rendering. */
(function () {
  'use strict';

  var form = document.getElementById('assessForm');
  if (!form) return;
  var steps = Array.prototype.slice.call(form.querySelectorAll('.q-step'));
  var navLabels = form.querySelectorAll('.assess-steps-nav span');
  var bar = form.querySelector('.assess-progress span');
  var btnBack = document.getElementById('qBack');
  var btnNext = document.getElementById('qNext');
  var btnSubmit = document.getElementById('qSubmit');
  var errorBox = document.getElementById('qError');
  var working = document.getElementById('assessWorking');
  var reportBox = document.getElementById('assessReport');
  var current = 0;
  var LIMITS = { headaches: 3 };

  function forms() { return window.MonarchForms || {}; }

  function show(i, initial) {
    current = i;
    steps.forEach(function (s, n) { s.classList.toggle('active', n === i); });
    navLabels.forEach(function (s, n) { s.classList.toggle('on', n <= i); });
    bar.style.width = ((i + 1) / steps.length * 100) + '%';
    btnBack.hidden = i === 0;
    btnNext.hidden = i === steps.length - 1;
    btnSubmit.hidden = i !== steps.length - 1;
    errorBox.classList.remove('show');
    if (!initial) form.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  function fail(msg, el) {
    errorBox.textContent = msg;
    errorBox.classList.add('show');
    if (el && el.focus) el.focus();
    return false;
  }

  function validate(i) {
    var step = steps[i];
    var inputs = step.querySelectorAll('input[required], textarea[required]');
    for (var k = 0; k < inputs.length; k++) {
      var el = inputs[k];
      if (!el.value.trim()) return fail('Please fill in ' + (step.querySelector('label[for="' + el.id + '"]') || {}).textContent.replace('*', '').trim().toLowerCase() + '.', el);
      if (el.type === 'email' && !/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(el.value.trim())) return fail('Please enter a valid email address.', el);
    }
    var groups = step.querySelectorAll('.chips[data-required]');
    for (var j = 0; j < groups.length; j++) {
      if (!groups[j].querySelector('input:checked')) {
        var label = groups[j].parentNode.querySelector('.q-label');
        return fail('Please choose an answer for "' + label.textContent.replace('*', '').replace(/\(.*\)/, '').trim() + '".', groups[j].querySelector('input'));
      }
    }
    return true;
  }

  // Cap multi-select groups (headaches: pick up to 3).
  Object.keys(LIMITS).forEach(function (name) {
    form.querySelectorAll('input[name="' + name + '"]').forEach(function (box) {
      box.addEventListener('change', function () {
        var checked = form.querySelectorAll('input[name="' + name + '"]:checked');
        if (checked.length > LIMITS[name]) {
          box.checked = false;
          fail('Pick up to ' + LIMITS[name] + ' so the AI can focus on what matters most.');
        } else {
          errorBox.classList.remove('show');
        }
      });
    });
  });

  form.addEventListener('focusin', function () { if (forms().ensureRecaptcha) forms().ensureRecaptcha(); }, { once: true });
  btnNext.addEventListener('click', function () { if (validate(current)) show(current + 1); });
  btnBack.addEventListener('click', function () { show(current - 1); });

  function collect() {
    var data = {};
    ['restaurant_name', 'city_state', 'website', 'notes', 'first_name', 'last_name', 'email', 'phone', '_honey'].forEach(function (n) {
      var el = form.querySelector('[name="' + n + '"]');
      data[n] = el ? el.value.trim() : '';
    });
    ['concept', 'locations', 'seats', 'staff', 'pos', 'reservations', 'scheduling', 'training', 'marketing_owner', 'goal', 'role'].forEach(function (n) {
      var el = form.querySelector('input[name="' + n + '"]:checked');
      data[n] = el ? el.value : '';
    });
    ['headaches', 'projects', 'channels'].forEach(function (n) {
      data[n] = Array.prototype.map.call(form.querySelectorAll('input[name="' + n + '"]:checked'), function (el) { return el.value; });
    });
    return data;
  }

  // The lead goes to form-notify first, so Christy gets it even if the AI step fails.
  function sendLead(data) {
    var f = forms();
    var token = f.getRecaptchaToken ? f.getRecaptchaToken('ai_assessment_lead') : Promise.resolve('');
    return token.then(function (t) {
      var payload = {
        site_slug: 'monarch-digital', form_type: 'ai-assessment', recaptcha_token: t, _honey: data._honey,
        _ts: String(f.loadedAt || Date.now()),
        first_name: data.first_name, last_name: data.last_name, email: data.email, phone: data.phone,
        company: data.restaurant_name, city_state: data.city_state, website: data.website, role: data.role,
        concept: data.concept, locations: data.locations, seats: data.seats, staff: data.staff,
        pos: data.pos, reservations: data.reservations, scheduling: data.scheduling, training: data.training,
        headaches: data.headaches.join(', '), projects: data.projects.join(', '), channels: data.channels.join(', '),
        marketing_owner: data.marketing_owner, goal: data.goal, message: data.notes
      };
      return fetch(f.endpoint || 'https://myaieditor.com/api/form-notify', {
        method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload)
      }).then(function (r) { return r.ok; }).catch(function () { return false; });
    });
  }

  function runAssessment(data) {
    var f = forms();
    var token = f.getRecaptchaToken ? f.getRecaptchaToken('ai_assessment') : Promise.resolve('');
    return token.then(function (t) {
      var body = Object.assign({}, data, { recaptcha_token: t });
      var ctrl = new AbortController();
      var timer = setTimeout(function () { ctrl.abort(); }, 118000);
      return fetch('/api/assess', {
        method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body), signal: ctrl.signal
      }).then(function (r) {
        clearTimeout(timer);
        return r.json().catch(function () { return {}; }).then(function (j) { return r.ok && j.ok ? j : null; });
      }).catch(function () { clearTimeout(timer); return null; });
    });
  }

  function animateWorking() {
    var items = working.querySelectorAll('[data-w]');
    var n = 0;
    items.forEach(function (li) { li.classList.remove('done'); });
    var tick = setInterval(function () {
      if (n < items.length - 1) { items[n].classList.add('done'); n++; } else { clearInterval(tick); }
    }, 4500);
    return function () { clearInterval(tick); items.forEach(function (li) { li.classList.add('done'); }); };
  }

  function el(tag, cls, text) {
    var node = document.createElement(tag);
    if (cls) node.className = cls;
    if (text != null) node.textContent = text;
    return node;
  }

  function renderReport(res, data) {
    var r = res.report;
    reportBox.innerHTML = '';
    var card = el('div', 'form-card');

    var head = el('div', 'report-head');
    var ring = el('div', 'ring');
    ring.style.setProperty('--v', r.overall);
    var inner = el('div');
    var wrap = el('div');
    wrap.appendChild(el('strong', null, String(r.overall)));
    wrap.appendChild(el('small', null, 'of 100'));
    inner.appendChild(wrap);
    ring.appendChild(inner);
    head.appendChild(ring);
    var intro = el('div');
    intro.appendChild(el('div', 'label', 'Your AI assessment'));
    var h = el('h2', null, r.headline);
    h.style.fontSize = 'clamp(24px,3vw,32px)';
    h.style.marginBottom = '10px';
    intro.appendChild(h);
    intro.appendChild(el('p', null, r.summary));
    head.appendChild(intro);
    card.appendChild(head);

    var bars = el('div', 'score-bars');
    r.categories.forEach(function (c) {
      var b = el('div', 'score-bar');
      var top = el('div', 'sb-top');
      top.appendChild(el('span', null, c.label));
      top.appendChild(el('span', null, String(c.score)));
      b.appendChild(top);
      var track = el('div', 'sb-track');
      var fill = el('div', 'sb-fill');
      fill.style.width = c.score + '%';
      fill.style.background = c.score >= 75 ? 'var(--teal)' : (c.score >= 55 ? 'var(--gold)' : '#D25A4E');
      track.appendChild(fill);
      b.appendChild(track);
      b.appendChild(el('div', 'sb-note', c.summary));
      bars.appendChild(b);
    });
    card.appendChild(bars);

    if (r.strengths && r.strengths.length) {
      card.appendChild(el('h3', null, 'What is working'));
      var ul = el('ul', 'ticks');
      r.strengths.forEach(function (s) { var li = el('li'); li.appendChild(el('span', null, s)); ul.appendChild(li); });
      card.appendChild(ul);
    }

    card.appendChild(el('h3', null, 'Top findings'));
    r.findings.forEach(function (f) {
      var row = el('div', 'finding');
      var fi = el('div', 'fi', f.severity === 'high' ? '!' : (f.severity === 'medium' ? '~' : 'i'));
      fi.style.fontWeight = '800';
      if (f.severity === 'high') { fi.style.background = '#FBE5E2'; fi.style.color = '#B4382E'; }
      row.appendChild(fi);
      var body = el('div');
      body.appendChild(el('h4', null, f.title));
      body.appendChild(el('p', null, f.detail));
      body.appendChild(el('div', 'evidence', 'Based on: ' + f.evidence));
      row.appendChild(body);
      card.appendChild(row);
    });

    var cols = el('div', 'reco-cols');
    [['Quick wins: next 30 days', r.quick_wins], ['Your 90-day plan', r.ninety_day_plan]].forEach(function (pair) {
      var box = el('div', 'reco');
      box.appendChild(el('h4', null, pair[0]));
      var list = el('ul');
      (pair[1] || []).forEach(function (a) {
        var li = el('li');
        var txt = el('span');
        var strong = el('strong', null, a.action + ' ');
        txt.appendChild(strong);
        txt.appendChild(document.createTextNode(a.why));
        li.appendChild(txt);
        list.appendChild(li);
      });
      box.appendChild(list);
      cols.appendChild(box);
    });
    card.appendChild(cols);

    if (res.services && res.services.length) {
      card.appendChild(el('h3', null, 'Where Monarch can help'));
      var grid = el('div', 'grid grid-2');
      res.services.forEach(function (s) {
        var a = el('a', 'feature');
        a.href = s.url;
        a.appendChild(el('h3', null, s.title));
        a.appendChild(el('p', null, s.reason));
        a.appendChild(el('span', 'card-more', 'Learn more'));
        grid.appendChild(a);
      });
      card.appendChild(grid);
    }

    if (r.data_notes && r.data_notes.length) {
      var notes = el('p', 'fine', 'What the AI could see: ' + r.data_notes.join(' '));
      notes.style.textAlign = 'left';
      notes.style.marginTop = '24px';
      card.appendChild(notes);
    }

    var cta = el('div', 'report-cta');
    var ctaText = el('div');
    ctaText.appendChild(el('h3', null, 'Want help putting this to work?'));
    ctaText.appendChild(el('p', null, res.emailed
      ? 'A copy is on its way to ' + data.email + '. Christy will reach out to walk through it with you.'
      : 'Christy has your answers and will reach out to walk through this with you.'));
    cta.appendChild(ctaText);
    var btn = el('a', 'btn btn-gold', 'Talk to Christy');
    btn.href = '/contact/';
    cta.appendChild(btn);
    card.appendChild(cta);

    reportBox.appendChild(card);
    reportBox.classList.add('show');
  }

  function renderFallback(data) {
    reportBox.innerHTML = '';
    var card = el('div', 'form-card');
    card.style.textAlign = 'center';
    card.appendChild(el('div', 'label', 'Your answers are in'));
    var h = el('h2', null, 'Christy will send your assessment personally');
    h.style.marginBottom = '12px';
    card.appendChild(h);
    card.appendChild(el('p', null, 'The AI could not finish just now, but your answers reached us. Expect your evaluation at ' +
      data.email + ' within one business day. Need us sooner? Call 727-383-6038.'));
    reportBox.appendChild(card);
    reportBox.classList.add('show');
  }

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    if (!validate(current)) return;
    var data = collect();
    if (data._honey) return;
    form.style.display = 'none';
    working.classList.add('show');
    var nameSlot = document.getElementById('wName');
    if (nameSlot && data.restaurant_name) nameSlot.textContent = data.restaurant_name;
    working.scrollIntoView({ behavior: 'smooth', block: 'start' });
    var stop = animateWorking();

    sendLead(data).then(function () { return runAssessment(data); }).then(function (res) {
      stop();
      working.classList.remove('show');
      if (res && res.report) {
        renderReport(res, data);
        window.dataLayer = window.dataLayer || [];
        window.dataLayer.push({ event: 'form_submission', form_type: 'ai-assessment', form_location: window.location.pathname });
      } else {
        renderFallback(data);
      }
      reportBox.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
  });

  show(0, true);
})();
