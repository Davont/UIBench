"""Browser-side HM Symbol rendering: the createIcons-compatible shim.

The shim replaces the Lucide CDN script inside rendered pages. It keeps the
authored ``<i data-lucide>`` elements (annotations, node ids and classes stay
untouched for the snapshot pipeline) and paints each icon exactly the way the
exported ArkUI project will: exact and near resolutions render the device
glyph from the extracted ``HMSymbolVF.ttf``; misses stay an empty box of the
same size. If the font or manifest is unavailable the shim falls back to the
real pinned Lucide build, so pages never lose icons outright.
"""
from __future__ import annotations

from uibench.arkui.symbols import pinned_lucide_version

# Lucide draws its icons with stroke-width 2 on a 24-unit grid (a stroke
# ratio of 2/24 = 0.0833 em); the HM Symbol default weight measures 0.0620 em
# on the same basis (the `minus` glyph's bar is 62/1000 em tall), 1.34x
# thinner. Weight 600 on the variable wght axis is the reviewed equivalent of
# the Lucide look. The shim writes it onto the element, the snapshot captures
# it as computed evidence, and the export emits the same SymbolGlyph weight,
# so browser and device thicken together from this single constant.
HM_SYMBOL_GLYPH_WEIGHT = 600

_SHIM_TEMPLATE = r"""(function () {
  'use strict';
  var FALLBACK_LUCIDE_SRC = '__FALLBACK_LUCIDE_SRC__';
  var FONT_FAMILY = 'HM Symbol';
  var assetsPromise = null;
  var fallbackStarted = false;
  var readyResolve;
  // The snapshot runtime awaits this before capturing, so glyph substitution
  // can never race the computed-style freeze.
  window.__uibenchHmSymbolReady = new Promise(function (resolve) {
    readyResolve = resolve;
  });

  function loadAssets() {
    if (assetsPromise) return assetsPromise;
    var face = new FontFace(FONT_FAMILY, 'url(/hm-symbol/font.ttf)');
    assetsPromise = Promise.all([
      fetch('/hm-symbol/manifest.json').then(function (response) {
        if (!response.ok) throw new Error('manifest ' + response.status);
        return response.json();
      }),
      face.load().then(function (loaded) { document.fonts.add(loaded); })
    ]).then(function (results) { return results[0]; });
    return assetsPromise;
  }

  function fallbackToLucide() {
    if (fallbackStarted) return;
    fallbackStarted = true;
    var script = document.createElement('script');
    script.src = FALLBACK_LUCIDE_SRC;
    script.onload = function () {
      // The real UMD build overwrites window.lucide with itself.
      if (window.lucide && window.lucide.createIcons) {
        window.lucide.createIcons();
      }
      readyResolve();
    };
    script.onerror = function () { readyResolve(); };
    document.head.appendChild(script);
  }

  function renderIcon(element, entry) {
    var status = entry ? entry.status : 'miss';
    element.setAttribute('data-hm-symbol', status);
    element.style.fontStyle = 'normal';
    element.style.lineHeight = '1';
    element.style.display = 'inline-flex';
    element.style.alignItems = 'center';
    element.style.justifyContent = 'center';
    if (entry && typeof entry.codepoint === 'number') {
      element.style.fontFamily = '"' + FONT_FAMILY + '"';
      // Match Lucide's stroke-2 visual weight; the snapshot captures this
      // as computed evidence, so the exported SymbolGlyph inherits it too.
      element.style.fontWeight = '__GLYPH_WEIGHT__';
      var box = element.getBoundingClientRect();
      var size = Math.min(box.width || 0, box.height || 0);
      if (size > 0) element.style.fontSize = size + 'px';
      element.textContent = String.fromCodePoint(entry.codepoint);
    } else {
      // The export degrades unresolved icons to an empty placeholder of the
      // same size; the preview shows the same hole instead of pretending.
      element.textContent = '';
    }
  }

  function createIcons() {
    var elements = Array.prototype.slice.call(
      document.querySelectorAll('i[data-lucide]')
    );
    return loadAssets().then(function (manifest) {
      elements.forEach(function (element) {
        var name = String(element.getAttribute('data-lucide') || '')
          .trim().toLowerCase();
        renderIcon(element, manifest.icons[name] || null);
      });
      readyResolve();
    }).catch(function () {
      fallbackToLucide();
    });
  }

  window.lucide = { createIcons: createIcons };
})();
"""


def hm_symbol_shim_js() -> str:
    """Render the shim with the pinned Lucide build as its failure fallback."""
    return _SHIM_TEMPLATE.replace(
        "__FALLBACK_LUCIDE_SRC__",
        f"https://unpkg.com/lucide@{pinned_lucide_version()}",
    ).replace(
        "__GLYPH_WEIGHT__",
        str(HM_SYMBOL_GLYPH_WEIGHT),
    )


__all__ = ["HM_SYMBOL_GLYPH_WEIGHT", "hm_symbol_shim_js"]
