"""Browser-side HM Symbol rendering: the createIcons-compatible shim.

The shim replaces the Lucide CDN script inside rendered pages. It keeps the
authored ``<i data-lucide>`` elements (annotations, node ids and classes stay
untouched for the snapshot pipeline) and paints each icon exactly the way the
exported ArkUI project will: exact and near resolutions render the device
glyph from the extracted HM Symbol font; misses stay an empty box of the
same size. If the font or manifest is unavailable the shim falls back to the
real pinned Lucide build, so pages never lose icons outright.
"""
from __future__ import annotations

import re

from uibench.arkui.symbols import HM_SYMBOL_FONT_FILE, pinned_lucide_version

# The generated pages declare 'HarmonyOS Sans SC' first in --dt-font-family,
# but without a served font file the browser silently falls back to the host
# system face (PingFang on macOS), so text metrics drift from the device.
# Both previewer faces are variable fonts (wght 40-900) repackaged as woff2
# at extraction time, so one @font-face with a weight range restores every
# weight the pages use.
HM_TEXT_FONTS: tuple[tuple[str, str], ...] = (
    ("HarmonyOS Sans SC", "HarmonyOS_Sans_SC.woff2"),
    ("HarmonyOS Sans", "HarmonyOS_Sans.woff2"),
)


_HM_FONTS_LINK = '<link rel="stylesheet" href="/hm-fonts.css">'
_HEAD_TAG_RE = re.compile(r"<head\b[^>]*>", re.IGNORECASE)


def inject_hm_fonts_link(html: str) -> str:
    """Bake the HarmonyOS text-font stylesheet link into a document.

    Generated pages are told to carry the link themselves; this keeps legacy
    documents on the same footing. The stylesheet is empty when the fonts are
    not extracted, so the link never breaks a page.
    """
    if "hm-fonts.css" in html.lower():
        return html
    head = _HEAD_TAG_RE.search(html)
    if head:
        return html[:head.end()] + _HM_FONTS_LINK + html[head.end():]
    return _HM_FONTS_LINK + html


def hm_fonts_css() -> str:
    """Render @font-face rules for the locally extracted HarmonyOS text fonts.

    Only faces that were actually extracted are declared; with none present
    the stylesheet is empty and pages keep today's system-font fallback.
    ``font-display: block`` keeps the capture path deterministic: the
    snapshot runtime already awaits ``document.fonts.ready``.
    """
    assets = HM_SYMBOL_FONT_FILE.parent
    rules = [
        (
            "@font-face {\n"
            f"  font-family: '{family}';\n"
            f"  src: url('/hm-fonts/{filename}') format('woff2');\n"
            "  font-weight: 100 900;\n"
            "  font-display: block;\n"
            "}"
        )
        for family, filename in HM_TEXT_FONTS
        if (assets / filename).is_file()
    ]
    return "\n".join(rules) + ("\n" if rules else "")

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
    var face = new FontFace(
      FONT_FAMILY, 'url(/hm-symbol/font.woff2) format("woff2")'
    );
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


__all__ = [
    "HM_SYMBOL_GLYPH_WEIGHT",
    "HM_TEXT_FONTS",
    "hm_fonts_css",
    "hm_symbol_shim_js",
    "inject_hm_fonts_link",
]
