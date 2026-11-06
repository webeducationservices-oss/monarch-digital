/* =============================================================
   ADA Accessibility Widget — Web Education Services
   Drop-in accessibility controls for any static site.

   Usage:
     <script src="path/to/ada-widget.js" data-color="#7D8B61" defer></script>

   Options (via data attributes on the script tag):
     data-color   Accent color for button & toggles (default: #2e6b4f)
     data-pos     "left" or "right" (default: left)
     data-mobile-bottom  Bottom offset on mobile in px (default: 72)
   ============================================================= */
(function () {
  // Read config from script tag
  var script = document.currentScript;
  var accent = (script && script.getAttribute('data-color')) || '#2e6b4f';
  var pos = (script && script.getAttribute('data-pos')) || 'left';
  var mobileBottom = (script && script.getAttribute('data-mobile-bottom')) || '72';
  var side = pos === 'right' ? 'right' : 'left';
  var otherSide = pos === 'right' ? 'left' : 'right';

  // Inject CSS
  var style = document.createElement('style');
  style.textContent = '' +
    '.ada-btn{position:fixed;bottom:20px;' + side + ':20px;' + otherSide + ':auto;z-index:9999;width:48px;height:48px;border-radius:50%;background:' + accent + ';border:none;cursor:pointer;display:flex;align-items:center;justify-content:center;box-shadow:0 4px 16px rgba(0,0,0,.25);transition:transform .2s,box-shadow .2s;}' +
    '.ada-btn:hover{transform:scale(1.08);box-shadow:0 6px 24px rgba(0,0,0,.3);}' +
    '.ada-btn svg{width:26px;height:26px;fill:#fff;}' +
    '.ada-panel{position:fixed;bottom:78px;' + side + ':20px;' + otherSide + ':auto;z-index:9999;width:300px;background:#fff;border-radius:12px;box-shadow:0 12px 48px rgba(0,0,0,.2);padding:20px;display:none;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;}' +
    '.ada-panel.open{display:block;}' +
    '.ada-panel h3{margin:0 0 14px;font-size:1rem;font-weight:700;color:#1e2219;display:flex;align-items:center;gap:8px;}' +
    '.ada-panel h3 svg{width:20px;height:20px;fill:' + accent + ';}' +
    '.ada-close{position:absolute;top:12px;right:12px;background:none;border:none;cursor:pointer;font-size:1.2rem;color:#999;line-height:1;}' +
    '.ada-close:hover{color:#333;}' +
    '.ada-row{display:flex;align-items:center;justify-content:space-between;padding:10px 0;border-bottom:1px solid #f0f0f0;}' +
    '.ada-row:last-child{border-bottom:none;}' +
    '.ada-row-label{font-size:.85rem;color:#444;}' +
    '.ada-row-controls{display:flex;align-items:center;gap:6px;}' +
    '.ada-row-controls button{width:32px;height:32px;border-radius:6px;border:1px solid #ddd;background:#fafafa;cursor:pointer;font-size:.9rem;font-weight:700;color:#444;display:flex;align-items:center;justify-content:center;transition:background .15s;}' +
    '.ada-row-controls button:hover{background:#eee;}' +
    '.ada-toggle{position:relative;width:42px;height:24px;background:#ddd;border-radius:12px;border:none;cursor:pointer;transition:background .2s;padding:0;}' +
    '.ada-toggle.on{background:' + accent + ';}' +
    '.ada-toggle::after{content:"";position:absolute;top:2px;left:2px;width:20px;height:20px;border-radius:50%;background:#fff;transition:transform .2s;box-shadow:0 1px 3px rgba(0,0,0,.2);}' +
    '.ada-toggle.on::after{transform:translateX(18px);}' +
    '.ada-reset{display:block;width:100%;margin-top:12px;padding:8px;border:1px solid #ddd;border-radius:8px;background:#fafafa;cursor:pointer;font-size:.8rem;color:#666;text-align:center;transition:background .15s;}' +
    '.ada-reset:hover{background:#eee;}' +
    '@media(max-width:768px){' +
      '.ada-btn{bottom:' + mobileBottom + 'px;' + side + ':12px;width:42px;height:42px;}' +
      '.ada-btn svg{width:22px;height:22px;}' +
      '.ada-panel{bottom:' + (parseInt(mobileBottom) + 52) + 'px;' + side + ':12px;width:calc(100vw - 24px);max-width:320px;}' +
    '}' +
    /* Big cursor */
    'body.ada-big-cursor,body.ada-big-cursor *{cursor:url("data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' width=\'32\' height=\'32\' viewBox=\'0 0 32 32\'%3E%3Cpath d=\'M5 2l18 14h-11l6 12-4 2-6-12-3 8z\' fill=\'%23000\' stroke=\'%23fff\' stroke-width=\'1.5\'/%3E%3C/svg%3E") 4 2,auto!important;}' +
    /* Highlight links */
    'body.ada-highlight-links a{outline:2px solid #ff0!important;outline-offset:2px!important;background:rgba(255,255,0,.15)!important;}' +
    /* High contrast — dark bg, light text, strong borders */
    'body.ada-high-contrast{background:#000!important;color:#fff!important;}' +
    'body.ada-high-contrast *:not(.ada-btn):not(.ada-panel):not(.ada-panel *){background-color:#000!important;color:#fff!important;border-color:#fff!important;}' +
    'body.ada-high-contrast img{filter:brightness(1.1) contrast(1.2);}' +
    'body.ada-high-contrast a{color:#ff0!important;text-decoration:underline!important;}' +
    'body.ada-high-contrast .ada-panel{background:#222!important;border:1px solid #555!important;}' +
    'body.ada-high-contrast .ada-panel *{background-color:#222!important;color:#eee!important;border-color:#555!important;}' +
    'body.ada-high-contrast .ada-panel a{color:#ff0!important;}' +
    'body.ada-high-contrast .ada-btn{opacity:1!important;}';
  document.head.appendChild(style);

  // Inject HTML
  var wrapper = document.createElement('div');
  wrapper.id = 'ada-widget-root';
  wrapper.innerHTML = '' +
    '<button class="ada-btn" id="ada-btn" aria-label="Accessibility options" title="Accessibility">' +
      '<svg viewBox="0 0 24 24"><circle cx="12" cy="4" r="2"/><path d="M12 8c-3.3 0-6 .9-6 2v1h3v9h2v-5h2v5h2v-9h3v-1c0-1.1-2.7-2-6-2z"/></svg>' +
    '</button>' +
    '<div class="ada-panel" id="ada-panel" role="dialog" aria-label="Accessibility settings">' +
      '<button class="ada-close" id="ada-close" aria-label="Close accessibility panel">&times;</button>' +
      '<h3><svg viewBox="0 0 24 24"><circle cx="12" cy="4" r="2"/><path d="M12 8c-3.3 0-6 .9-6 2v1h3v9h2v-5h2v5h2v-9h3v-1c0-1.1-2.7-2-6-2z"/></svg> Accessibility</h3>' +
      '<div class="ada-row"><span class="ada-row-label">Text Size</span><div class="ada-row-controls"><button id="ada-font-down" aria-label="Decrease text size">A\u2212</button><button id="ada-font-reset" aria-label="Reset text size" style="font-size:.75rem">Reset</button><button id="ada-font-up" aria-label="Increase text size">A+</button></div></div>' +
      '<div class="ada-row"><span class="ada-row-label">High Contrast</span><button class="ada-toggle" id="ada-contrast" aria-label="Toggle high contrast"></button></div>' +
      '<div class="ada-row"><span class="ada-row-label">Highlight Links</span><button class="ada-toggle" id="ada-links" aria-label="Toggle link highlighting"></button></div>' +
      '<div class="ada-row"><span class="ada-row-label">Big Cursor</span><button class="ada-toggle" id="ada-cursor" aria-label="Toggle big cursor"></button></div>' +
      '<button class="ada-reset" id="ada-reset">Reset All</button>' +
    '</div>';
  document.body.appendChild(wrapper);

  // Wire interactions
  function ready(fn) {
    if (document.readyState !== 'loading') fn();
    else document.addEventListener('DOMContentLoaded', fn);
  }

  ready(function () {
    var btn = document.getElementById('ada-btn');
    var panel = document.getElementById('ada-panel');
    var close = document.getElementById('ada-close');
    if (!btn || !panel) return;

    var fontLevel = 0;

    // Open / close panel
    btn.addEventListener('click', function () { panel.classList.toggle('open'); });
    close.addEventListener('click', function () { panel.classList.remove('open'); });
    document.addEventListener('click', function (e) {
      if (!btn.contains(e.target) && !panel.contains(e.target)) {
        panel.classList.remove('open');
      }
    });

    // Font size
    document.getElementById('ada-font-up').addEventListener('click', function () {
      if (fontLevel < 4) { fontLevel++; document.documentElement.style.fontSize = (100 + fontLevel * 12.5) + '%'; }
    });
    document.getElementById('ada-font-down').addEventListener('click', function () {
      if (fontLevel > -2) { fontLevel--; document.documentElement.style.fontSize = (100 + fontLevel * 12.5) + '%'; }
    });
    document.getElementById('ada-font-reset').addEventListener('click', function () {
      fontLevel = 0; document.documentElement.style.fontSize = '';
    });

    // Toggle helpers
    function bindToggle(btnId, bodyClass) {
      document.getElementById(btnId).addEventListener('click', function () {
        this.classList.toggle('on');
        document.body.classList.toggle(bodyClass);
      });
    }
    bindToggle('ada-contrast', 'ada-high-contrast');
    bindToggle('ada-links', 'ada-highlight-links');
    bindToggle('ada-cursor', 'ada-big-cursor');

    // Reset all
    document.getElementById('ada-reset').addEventListener('click', function () {
      fontLevel = 0;
      document.documentElement.style.fontSize = '';
      document.body.classList.remove('ada-high-contrast', 'ada-highlight-links', 'ada-big-cursor');
      panel.querySelectorAll('.ada-toggle').forEach(function (t) { t.classList.remove('on'); });
    });
  });
})();
