# Built-in application icons

Every brand application icon is raster artwork from the app's active Apple
China listing, checked on 2026-08-14. `sources.json` records the seller, bundle
ID, store version, release date, 512px artwork URL, check date, and hash of the
local 256px PNG. The only presentation change is the standard rounded
application-icon alpha mask; the artwork inside the mask is unchanged.

Brand entries intentionally have no local SVG. A brand logo vector and a
currently distributed application icon are different assets, and mixing the
two previously caused stale proportions and double application backgrounds.

`camera`, `maps`, `photos`, and `contacts` are original generic UIBench assets,
not third-party brand marks. PNG files are 256×256 raster exports used by HTML
and ArkUI packaging; these original system icons retain editable SVG sources.
