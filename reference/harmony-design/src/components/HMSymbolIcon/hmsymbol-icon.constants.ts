import {
  hmSymbolGlyphsGenerated,
  hmSymbolUnicodeByName,
  type HMSymbolIconGeneratedName,
} from "./hmsymbol-icon.generated"

const hmSymbolLegacyAliases = {
  /* Historical local alias; official name_map_new.json uses circle_dashed for U+F0134. */
  square_dashed: "\u{F0134}",
  /* Pixso `.TV` — historical local alias for HM Symbol U+F0021 */
  tv: "\u{F0021}",
  /* Historical local alias; official name_map_new.json uses stopwatch_2 for U+F05F0. */
  stopwatch: "\u{F05F0}",
  mic: "\u{F0006}",
  mic_fill: "\u{F0315}",
  questionmark_circle: "\u{F0100}",
  triangle_down_fill: "\u{F023F}",
  /* Pixso segmented-button `.highlight` — absent from official name_map_new.json */
  segmented_button_highlight: "\u{F012F}",
  /* Pixso music list action: plus with horizontal list lines (item-id 143:59576). */
  plus_list: "\u{F0156}",

} as const

const hmSymbolLegacyUnicodeByName = {
  square_dashed: "F0134",
  tv: "F0021",
  stopwatch: "F05F0",
  mic: "F0006",
  mic_fill: "F0315",
  questionmark_circle: "F0100",
  triangle_down_fill: "F023F",
  segmented_button_highlight: "F012F",
  plus_list: "F0156",
} as const

export const hmSymbolGlyphs = {
  ...hmSymbolGlyphsGenerated,
  ...hmSymbolLegacyAliases,
} as const

export const hmSymbolUnicodes = {
  ...hmSymbolUnicodeByName,
  ...hmSymbolLegacyUnicodeByName,
} as const

export type HMSymbolIconName =
  | HMSymbolIconGeneratedName
  | keyof typeof hmSymbolLegacyAliases

export { hmSymbolGlyphsGenerated, hmSymbolUnicodeByName }
export type { HMSymbolIconGeneratedName }
