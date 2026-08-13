"""Extract and validate ArkUI-oriented metadata from generated HTML."""
from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, replace
from html.parser import HTMLParser
from typing import Literal

from uibench.arkui.components import ComponentDefinition, load_component_registry
from uibench.arkui.symbols import (
    SymbolResolution,
    is_known_lucide_icon,
    pinned_lucide_version,
    resolve_lucide_icon,
    resolve_lucide_icon_near,
    resolve_symbol,
)

# "notice" records that an annotation was read differently than written while
# the rendered result is unchanged; only "warning" means the ArkUI project can
# no longer look like the captured page.
DiagnosticSeverity = Literal["notice", "warning", "error"]
ComponentSource = Literal["explicit", "html"]
ExportReadiness = Literal["ready", "lossy", "blocked", "unavailable"]

_NODE_ID_RE = re.compile(r"^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$")
_ROLE_RE = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$")
_GENERATED_NODE_ID_ATTR = "data-uibench-generated-node-id"
_BUTTON_LABEL_REPAIR = "button-label"
_VOID_TAGS = frozenset({
    "area", "base", "br", "col", "embed", "hr", "img", "input", "link",
    "meta", "param", "source", "track", "wbr",
})
_P_IMPLIED_END_START_TAGS = frozenset({
    "address", "article", "aside", "blockquote", "details", "dialog", "div",
    "dl", "fieldset", "figcaption", "figure", "footer", "form", "h1", "h2",
    "h3", "h4", "h5", "h6", "header", "hgroup", "hr", "main", "menu",
    "nav", "ol", "p", "pre", "search", "section", "table", "ul",
})
_BUTTON_SCOPE_BOUNDARIES = frozenset({
    "applet", "caption", "html", "marquee", "object", "table", "td", "th",
    "template", "button",
})
_HEADING_TAGS = frozenset({"h1", "h2", "h3", "h4", "h5", "h6"})
_HEAD_CONTENT_TAGS = frozenset({
    "base", "basefont", "bgsound", "link", "meta", "noframes", "noscript",
    "script", "style", "template", "title",
})
MAX_HTML_TREE_DEPTH = 256
MAX_COMPONENT_TREE_DEPTH = 128


def _implied_end_cut(open_tags: list[str], incoming: str) -> int | None:
    """Approximate the common HTML tree-builder implied-end-tag rules.

    ``HTMLParser`` tokenizes HTML but does not build an HTML tree. Applying the
    common list, paragraph, select, and table rules here avoids treating normal
    optional-end-tag markup as deeper than the browser DOM.
    """
    working = list(open_tags)
    changed = False

    def close_in_scope(
        targets: frozenset[str], boundaries: frozenset[str],
    ) -> None:
        nonlocal working, changed
        for index in range(len(working) - 1, -1, -1):
            current = working[index]
            if current in targets:
                working = working[:index]
                changed = True
                return
            if current in boundaries:
                return

    if incoming == "li":
        close_in_scope(frozenset({"li"}), frozenset({"menu", "ol", "ul"}))
    elif incoming in {"dt", "dd"}:
        close_in_scope(frozenset({"dt", "dd"}), frozenset({"dl"}))
    elif incoming in {"rt", "rp"}:
        close_in_scope(frozenset({"rt", "rp"}), frozenset({"ruby"}))

    if incoming in _P_IMPLIED_END_START_TAGS:
        close_in_scope(frozenset({"p"}), _BUTTON_SCOPE_BOUNDARIES)

    if incoming in _HEADING_TAGS:
        close_in_scope(_HEADING_TAGS, frozenset({"body", "html"}))
    elif incoming == "button":
        close_in_scope(frozenset({"button"}), _BUTTON_SCOPE_BOUNDARIES - {"button"})

    if incoming == "option":
        close_in_scope(frozenset({"option"}), frozenset({"datalist", "select"}))
    elif incoming == "optgroup":
        close_in_scope(frozenset({"option"}), frozenset({"datalist", "select"}))
        close_in_scope(frozenset({"optgroup"}), frozenset({"select"}))

    if incoming in {"thead", "tbody", "tfoot"}:
        close_in_scope(
            frozenset({"thead", "tbody", "tfoot"}),
            frozenset({"html", "table", "template"}),
        )
    elif incoming == "tr":
        close_in_scope(
            frozenset({"tr"}),
            frozenset({"html", "table", "tbody", "tfoot", "thead", "template"}),
        )
    elif incoming in {"td", "th"}:
        close_in_scope(
            frozenset({"td", "th"}),
            frozenset({"html", "table", "tr", "template"}),
        )

    return len(working) if changed else None


def _set_text_mode_for_slash_start(parser: HTMLParser, tag: str) -> None:
    """Make ``<script/>`` and other non-void slash tags behave like HTML starts."""
    if tag in parser.CDATA_CONTENT_ELEMENTS or (
        getattr(parser, "scripting", False) and tag == "noscript"
    ) or tag == "plaintext":
        parser.set_cdata_mode(tag, escapable=False)
    elif tag in parser.RCDATA_CONTENT_ELEMENTS:
        parser.set_cdata_mode(tag, escapable=True)


@dataclass
class _DocumentStructureState:
    """Track singleton document elements omitted by ``HTMLParser``'s tokenizer."""

    html_started: bool = False
    head_started: bool = False
    head_closed: bool = False
    body_started: bool = False

    def prepare_start(
        self, tag: str, open_tags: list[str],
    ) -> tuple[bool, int | None]:
        """Return whether to process the token and an open-head cut, if any."""
        if tag == "html":
            if self.html_started or self.head_started or self.body_started:
                return False, None
            self.html_started = True
            return True, None

        if tag == "head":
            if self.head_started or self.head_closed or self.body_started:
                return False, None
            self.head_started = True
            return True, None

        if tag == "body":
            if self.body_started:
                # The tree builder merges missing attributes into the existing
                # body, but never creates or pushes another body element.
                return False, None
            self.body_started = True
            self.head_closed = True
            return True, self._open_head_cut(open_tags)

        open_head_cut = self._open_head_cut(open_tags)
        if open_head_cut is not None and tag not in _HEAD_CONTENT_TAGS:
            self.head_closed = True
            self.body_started = True
            return True, open_head_cut

        if not self.head_started and not self.body_started:
            if tag in _HEAD_CONTENT_TAGS:
                # parse5 creates an implicit head for these tokens.
                self.head_started = True
            else:
                # Any ordinary content creates an implicit body. A later body
                # start tag may merge attributes but must not increase depth.
                self.head_closed = True
                self.body_started = True
        elif self.head_closed and not self.body_started and tag not in _HEAD_CONTENT_TAGS:
            self.body_started = True
        return True, None

    def observe_end(self, tag: str, open_tags: list[str]) -> None:
        if tag == "head" and "head" in open_tags:
            self.head_started = True
            self.head_closed = True

    @staticmethod
    def _open_head_cut(open_tags: list[str]) -> int | None:
        for index in range(len(open_tags) - 1, -1, -1):
            if open_tags[index] == "head":
                return index
        return None


@dataclass(frozen=True)
class ComponentDiagnostic:
    code: str
    severity: DiagnosticSeverity
    message: str
    line: int
    column: int
    node_id: str | None = None
    component: str | None = None


@dataclass(frozen=True)
class ComponentNode:
    node_id: str | None
    component: str
    arkui_component: str
    source: ComponentSource
    tag: str
    ui_role: str | None
    parent_index: int | None
    line: int
    column: int
    metadata: tuple[tuple[str, str], ...]
    attributes: tuple[tuple[str, str], ...]
    text_content: str
    renderer_supported: bool
    # Direct text fragments in document order. Each entry pairs the fragment
    # with the number of direct component children registered before it, so
    # rich text such as ``共 <span>3</span> 台`` keeps the parent's fragments
    # positioned around the styled spans instead of collapsing into one
    # order-less string.
    text_runs: tuple[tuple[int, str], ...] = ()
    # A SymbolGlyph cannot be a child of ArkUI Text. This marker preserves the
    # model's intent until the browser snapshot can prove which layout
    # container (Row or Column) rendered the mixed icon/text content.
    mixed_symbol_content: bool = False


@dataclass(frozen=True)
class ComponentMetadataReport:
    nodes: tuple[ComponentNode, ...]
    diagnostics: tuple[ComponentDiagnostic, ...]

    @property
    def errors(self) -> tuple[ComponentDiagnostic, ...]:
        return tuple(item for item in self.diagnostics if item.severity == "error")

    @property
    def warnings(self) -> tuple[ComponentDiagnostic, ...]:
        return tuple(item for item in self.diagnostics if item.severity == "warning")

    @property
    def notices(self) -> tuple[ComponentDiagnostic, ...]:
        return tuple(item for item in self.diagnostics if item.severity == "notice")

    @property
    def component_counts(self) -> dict[str, int]:
        return dict(sorted(Counter(node.component for node in self.nodes).items()))

    @property
    def explicit_components(self) -> int:
        return sum(node.source == "explicit" for node in self.nodes)

    @property
    def inferred_components(self) -> int:
        return sum(node.source == "html" for node in self.nodes)

    @property
    def unsupported_components(self) -> dict[str, int]:
        return dict(sorted(Counter(
            node.component for node in self.nodes if not node.renderer_supported
        ).items()))

    @property
    def root_components(self) -> int:
        return sum(node.parent_index is None for node in self.nodes)

    @property
    def addressable_coverage(self) -> float:
        if not self.nodes:
            return 0.0
        addressable = sum(node.node_id is not None for node in self.nodes)
        return round(addressable / len(self.nodes), 4)

    @property
    def export_readiness(self) -> ExportReadiness:
        if self.explicit_components == 0:
            return "unavailable"
        # Screen IR needs one addressable root and a stable id per node; both
        # are only warnings here because they can come from inferred markup.
        if (
            self.errors
            or self.unsupported_components
            or any(node.node_id is None for node in self.nodes)
            or self.root_components != 1
        ):
            return "blocked"
        if self.warnings:
            return "lossy"
        return "ready"

    def to_manifest(self) -> dict[str, object]:
        registry = load_component_registry()
        return {
            "kind": "uibench-component-manifest",
            "manifestVersion": 1,
            # Retained for clients written against the first UIBench manifest.
            "schemaVersion": 1,
            "screenIrSchemaVersion": registry.screen_ir_schema_version,
            "rendererContractVersion": registry.renderer_contract_version,
            "components": [
                {
                    "nodeId": node.node_id,
                    "component": node.component,
                    "arkuiComponent": node.arkui_component,
                    "source": node.source,
                    "tag": node.tag,
                    "uiRole": node.ui_role,
                    "rendererSupported": node.renderer_supported,
                    "parentNodeId": (
                        self.nodes[node.parent_index].node_id
                        if node.parent_index is not None else None
                    ),
                    "content": node.text_content or None,
                    "attributes": dict(node.attributes),
                    "metadata": dict(node.metadata),
                }
                for node in self.nodes
            ],
            "summary": {
                "componentCounts": self.component_counts,
                "explicitComponents": self.explicit_components,
                "inferredComponents": self.inferred_components,
                "metadataPresent": self.explicit_components > 0,
                "addressableCoverage": self.addressable_coverage,
                "rendererSupportedComponents": sum(
                    node.renderer_supported for node in self.nodes
                ),
                "rootComponents": self.root_components,
                "unsupportedComponents": self.unsupported_components,
                "exportReadiness": self.export_readiness,
                "exportable": self.export_readiness in {"ready", "lossy"},
                "errors": len(self.errors),
                "warnings": len(self.warnings),
                "notices": len(self.notices),
            },
            "diagnostics": [
                {
                    "code": item.code,
                    "severity": item.severity,
                    "message": item.message,
                    "line": item.line,
                    "column": item.column,
                    "nodeId": item.node_id,
                    "component": item.component,
                }
                for item in self.diagnostics
            ],
        }


@dataclass
class _Frame:
    tag: str
    node_index: int | None


class _HtmlDepthParser(HTMLParser):
    """Find excessive authored nesting without constructing an HTML tree."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.frames: list[str] = []
        self.violation: tuple[int, int] | None = None
        self.document = _DocumentStructureState()

    def _record_depth(self) -> None:
        if self.violation is None and len(self.frames) + 1 > MAX_HTML_TREE_DEPTH:
            self.violation = self.getpos()

    def _close_implied_frames(self, incoming: str) -> None:
        cut = _implied_end_cut(self.frames, incoming)
        if cut is not None:
            del self.frames[cut:]

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        del attrs
        normalized = tag.lower()
        process, head_cut = self.document.prepare_start(normalized, self.frames)
        if not process:
            return
        if head_cut is not None:
            del self.frames[head_cut:]
        self._close_implied_frames(normalized)
        if normalized in _VOID_TAGS:
            return
        self._record_depth()
        self.frames.append(normalized)

    def handle_startendtag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        normalized = tag.lower()
        self.handle_starttag(tag, attrs)
        if normalized not in _VOID_TAGS:
            # In HTML (unlike XML), a slash does not close a non-void element.
            # HTMLParser skips its usual raw-text transition for this callback,
            # so reproduce that part of normal start-tag handling as well.
            _set_text_mode_for_slash_start(self, normalized)

    def handle_endtag(self, tag: str) -> None:
        normalized = tag.lower()
        self.document.observe_end(normalized, self.frames)
        for index in range(len(self.frames) - 1, -1, -1):
            if self.frames[index] == normalized:
                del self.frames[index:]
                return


def find_html_tree_depth_violation(html: str) -> tuple[int, int] | None:
    """Return the first source location deeper than the supported HTML bound."""
    if not isinstance(html, str):
        raise TypeError("html must be a string")
    parser = _HtmlDepthParser()
    parser.feed(html)
    parser.close()
    return parser.violation


def _native_component(tag: str, attrs: dict[str, str]) -> str | None:
    if tag == "button":
        return "button"
    if tag == "img":
        return "image"
    if tag == "textarea":
        return "text-area"
    if tag == "select":
        return "select"
    if tag == "progress":
        return "progress"
    if tag == "hr":
        return "divider"
    if tag == "i" and attrs.get("data-lucide"):
        return "symbol"
    if tag != "input":
        return None

    input_type = attrs.get("type", "text").strip().lower()
    return {
        "button": "button",
        "checkbox": "checkbox",
        "radio": "radio",
        "range": "slider",
        "reset": "button",
        "search": "search",
        "submit": "button",
    }.get(input_type, "text-input")


@dataclass(frozen=True)
class _NodeIdRepairCandidate:
    insertion_offset: int


@dataclass
class _NodeIdRepairFrame:
    tag: str
    component: str | None
    node_id: str | None
    direct_element_children: int = 0
    direct_component_children: int = 0
    has_direct_text: bool = False
    missing_button_label: _NodeIdRepairCandidate | None = None


class _MissingNodeIdRepairParser(HTMLParser):
    """Locate button labels whose stable ID has one unambiguous derivation."""

    def __init__(self, html: str) -> None:
        super().__init__(convert_charrefs=True)
        self.frames: list[_NodeIdRepairFrame] = []
        self.buttons: list[_NodeIdRepairFrame] = []
        self.node_id_counts: Counter[str] = Counter()
        self.document = _DocumentStructureState()
        self.line_offsets: list[int] = []
        offset = 0
        for line in html.splitlines(keepends=True):
            self.line_offsets.append(offset)
            offset += len(line)
        if not self.line_offsets:
            self.line_offsets.append(0)

    def _close_implied_frames(self, incoming: str) -> None:
        cut = _implied_end_cut(
            [frame.tag for frame in self.frames], incoming,
        )
        if cut is not None:
            del self.frames[cut:]

    def _start_offset(self) -> int:
        line, column = self.getpos()
        return self.line_offsets[line - 1] + column

    def _attribute_insertion_offset(self) -> int:
        raw_tag = self.get_starttag_text()
        if not raw_tag or not raw_tag.endswith(">"):
            raise ValueError("HTML start tag is unavailable for node-id repair")
        relative = len(raw_tag) - 1
        while relative > 0 and raw_tag[relative - 1].isspace():
            relative -= 1
        if relative > 0 and raw_tag[relative - 1] == "/":
            relative -= 1
        return self._start_offset() + relative

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        normalized_tag = tag.lower()
        process, head_cut = self.document.prepare_start(
            normalized_tag, [frame.tag for frame in self.frames],
        )
        if not process:
            return
        if head_cut is not None:
            del self.frames[head_cut:]
        self._close_implied_frames(normalized_tag)

        attributes = {name.lower(): value or "" for name, value in attrs}
        explicit_component = attributes.get("data-component", "").strip().lower()
        component = explicit_component or _native_component(
            normalized_tag, attributes
        )
        node_id = attributes.get("data-node-id", "").strip() or None
        if node_id is not None:
            self.node_id_counts[node_id] += 1

        parent = self.frames[-1] if self.frames else None
        if parent is not None:
            parent.direct_element_children += 1
        if parent is not None and component is not None:
            parent.direct_component_children += 1
            if (
                parent.component == "button"
                and explicit_component == "text"
                and "data-node-id" not in attributes
                and _GENERATED_NODE_ID_ATTR not in attributes
            ):
                parent.missing_button_label = _NodeIdRepairCandidate(
                    insertion_offset=self._attribute_insertion_offset(),
                )

        if normalized_tag in _VOID_TAGS:
            return
        frame = _NodeIdRepairFrame(
            tag=normalized_tag,
            component=component,
            node_id=node_id,
        )
        self.frames.append(frame)
        if component == "button":
            self.buttons.append(frame)

    def handle_startendtag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        self.handle_starttag(tag, attrs)
        normalized = tag.lower()
        if normalized not in _VOID_TAGS:
            _set_text_mode_for_slash_start(self, normalized)

    def handle_endtag(self, tag: str) -> None:
        normalized = tag.lower()
        self.document.observe_end(
            normalized, [frame.tag for frame in self.frames],
        )
        for index in range(len(self.frames) - 1, -1, -1):
            if self.frames[index].tag == normalized:
                del self.frames[index:]
                return

    def handle_data(self, data: str) -> None:
        if self.frames and data.strip(" \t\r\n\f"):
            self.frames[-1].has_direct_text = True

    def repaired_html(self, html: str) -> str:
        used_ids = set(self.node_id_counts)
        insertions: list[tuple[int, str]] = []
        for button in self.buttons:
            parent_id = button.node_id
            candidate = button.missing_button_label
            if (
                parent_id is None
                or candidate is None
                or button.direct_element_children != 1
                or button.direct_component_children != 1
                or button.has_direct_text
                or not _NODE_ID_RE.fullmatch(parent_id)
                or self.node_id_counts[parent_id] != 1
            ):
                continue
            base = f"{parent_id}.label"
            generated_id = base
            suffix = 2
            while generated_id in used_ids:
                generated_id = f"{base}-{suffix}"
                suffix += 1
            used_ids.add(generated_id)
            insertions.append((
                candidate.insertion_offset,
                f' data-node-id="{generated_id}" '
                f'{_GENERATED_NODE_ID_ATTR}="{_BUTTON_LABEL_REPAIR}"',
            ))

        repaired = html
        for offset, attributes in sorted(insertions, reverse=True):
            repaired = repaired[:offset] + attributes + repaired[offset:]
        return repaired


def repair_missing_component_node_ids(html: str) -> str:
    """Add deterministic IDs only where component structure proves the name.

    A Button with exactly one direct component child can only be presenting
    that Text as its label. Other missing IDs remain untouched so ambiguous
    component trees continue to fail closed during metadata validation.
    """
    if not isinstance(html, str):
        raise TypeError("html must be a string")
    parser = _MissingNodeIdRepairParser(html)
    parser.feed(html)
    parser.close()
    return parser.repaired_html(html)


def _metadata(attrs: dict[str, str]) -> tuple[tuple[str, str], ...]:
    return tuple(sorted(
        (name, value)
        for name, value in attrs.items()
        if name.startswith("data-") and name not in {
            "data-component",
            "data-node-id",
            "data-ui-role",
            _GENERATED_NODE_ID_ATTR,
        }
    ))


def _relevant_attributes(attrs: dict[str, str]) -> tuple[tuple[str, str], ...]:
    names = {
        "alt", "aria-label", "checked", "disabled", "name", "src",
        "title", "type", "value",
    }
    return tuple(sorted(
        (name, value) for name, value in attrs.items() if name in names
    ))


_WHITESPACE_RUN_RE = re.compile(r"\s+")


def _normalized_text_runs(
    fragments: list[tuple[int, str]],
    child_count: int,
) -> tuple[tuple[int, str], ...]:
    """Collapse raw text fragments the way inline HTML whitespace renders.

    Runs of whitespace become one space; leading whitespace before the first
    child and trailing whitespace after the last child disappear at the block
    edge. A single space *between* a fragment and a neighbouring child stays,
    because the browser renders it (``共 <span>3</span> 台``).
    """
    merged: list[tuple[int, str]] = []
    for position, text in fragments:
        if merged and merged[-1][0] == position:
            merged[-1] = (position, merged[-1][1] + text)
        else:
            merged.append((position, text))
    runs: list[tuple[int, str]] = []
    for position, text in merged:
        collapsed = _WHITESPACE_RUN_RE.sub(" ", text)
        if position == 0:
            collapsed = collapsed.lstrip()
        if position == child_count:
            collapsed = collapsed.rstrip()
        if collapsed:
            runs.append((position, collapsed))
    return tuple(runs)


class _ComponentMetadataParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.registry = load_component_registry()
        self.nodes: list[ComponentNode] = []
        self.diagnostics: list[ComponentDiagnostic] = []
        self.frames: list[_Frame] = []
        self.seen_ids: dict[str, tuple[int, int]] = {}
        # Text fragments per node, each tagged with how many direct component
        # children that node held when the fragment arrived (its "run
        # position" between the child components).
        self.node_text: list[list[tuple[int, str]]] = []
        self.node_child_counts: list[int] = []
        self.node_depths: list[int] = []
        self.mixed_symbol_parents: set[int] = set()
        self.component_depth_exceeded = False
        self.document = _DocumentStructureState()

    def _diagnostic(
        self,
        code: str,
        severity: DiagnosticSeverity,
        message: str,
        *,
        node_id: str | None = None,
        component: str | None = None,
        line: int | None = None,
        column: int | None = None,
    ) -> None:
        current_line, current_column = self.getpos()
        self.diagnostics.append(ComponentDiagnostic(
            code=code,
            severity=severity,
            message=message,
            line=current_line if line is None else line,
            column=current_column if column is None else column,
            node_id=node_id,
            component=component,
        ))

    def _parent_index(self) -> int | None:
        for frame in reversed(self.frames):
            if frame.node_index is not None:
                return frame.node_index
        return None

    def _close_implied_frames(self, incoming: str) -> None:
        cut = _implied_end_cut(
            [frame.tag for frame in self.frames], incoming,
        )
        if cut is not None:
            del self.frames[cut:]

    def _validate_id(self, node_id: str | None, component: str, explicit: bool) -> None:
        if node_id is None:
            self._diagnostic(
                "ARKUI_NODE_ID_MISSING",
                "error" if explicit else "warning",
                f"{component!r} component has no stable data-node-id",
                component=component,
            )
            return
        if not _NODE_ID_RE.fullmatch(node_id):
            self._diagnostic(
                "ARKUI_NODE_ID_INVALID",
                "error",
                f"data-node-id {node_id!r} must be a lower-case stable path",
                node_id=node_id,
                component=component,
            )
        previous = self.seen_ids.get(node_id)
        if previous is not None:
            self._diagnostic(
                "ARKUI_NODE_ID_DUPLICATE",
                "error",
                f"data-node-id {node_id!r} is already used at {previous[0]}:{previous[1]}",
                node_id=node_id,
                component=component,
            )
        else:
            self.seen_ids[node_id] = self.getpos()

    def _promote_orphan_span(
        self,
        definition: ComponentDefinition,
        parent_index: int | None,
        node_id: str | None,
    ) -> ComponentDefinition:
        """Read a span outside a text as the Text it can only have meant.

        ArkUI has no legal form for ``Span`` outside ``Text``, so a standalone
        span has exactly one sensible reading. Applying the registry fallback
        keeps the node, its text and its geometry intact, which is why this is
        a notice — the annotation was re-read but the rendered result is
        unchanged — rather than one of the blocking structural errors. Other
        fallbacks stay unused: they would change what the page means.
        """
        if definition.key != "span":
            return definition
        parent = self.nodes[parent_index] if parent_index is not None else None
        if parent is not None and parent.component == "text":
            return definition
        fallback = self.registry.components[definition.fallback or "text"]
        self._diagnostic(
            "ARKUI_SPAN_PROMOTED_TO_TEXT",
            "notice",
            f"span outside a text parent was exported as {fallback.key!r}; "
            "annotate standalone text as text and keep span for styled "
            "fragments inside a text",
            node_id=node_id,
            component=definition.key,
        )
        return fallback

    def _promote_orphan_list_item(
        self,
        definition: ComponentDefinition,
        parent_index: int | None,
        node_id: str | None,
    ) -> ComponentDefinition:
        """Read a list-item outside a list as the plain container it must be.

        ArkUI has no legal form for ``ListItem`` outside ``List``, so, exactly
        like the orphan span above, the registry fallback is the one reading
        that keeps the node, its children and its geometry. Only the
        collection semantics that had no list to belong to are dropped, which
        is why this is a notice and not a structural error.
        """
        if definition.key != "list-item":
            return definition
        parent = self.nodes[parent_index] if parent_index is not None else None
        if parent is not None and parent.component == "list":
            return definition
        fallback = self.registry.components[definition.fallback or "column"]
        self._diagnostic(
            "ARKUI_LIST_ITEM_PROMOTED_TO_COLUMN",
            "notice",
            f"list-item outside a list parent was exported as "
            f"{fallback.key!r}; keep list-item for the entries of a list",
            node_id=node_id,
            component=definition.key,
        )
        return fallback

    def _resolve_symbol(
        self,
        definition: ComponentDefinition,
        attributes: dict[str, str],
        node_id: str | None,
    ) -> ComponentDefinition:
        """Bind a symbol node to a HarmonyOS resource that actually exists.

        ``data-lucide`` is evidence: the page cannot render without it and the
        icon library is fixed, so it beats a hand-written ``data-symbol``,
        which is only the model's guess at a mapping it has no way to verify.
        An icon HarmonyOS has no resource for degrades to an empty container of
        the same size, which keeps the surrounding layout intact.
        """
        lucide_name = attributes.get("data-lucide", "").strip()
        declared = attributes.get("data-symbol", "").strip()
        if lucide_name and not is_known_lucide_icon(lucide_name):
            # The pinned Lucide build cannot render this name, so the browser
            # page shows no icon here at all. Resolving it against HarmonyOS
            # symbols (a name such as "person" happens to exist there), or
            # honouring a declared data-symbol, would invent a glyph the
            # captured page never had.
            attributes.pop("data-symbol", None)
            self._diagnostic(
                "ARKUI_LUCIDE_ICON_UNKNOWN",
                "warning",
                f"data-lucide {lucide_name!r} is not an icon of the pinned "
                f"Lucide catalogue ({pinned_lucide_version()}); the browser "
                "renders no icon for it, so it was exported as an empty "
                "placeholder of the same size",
                node_id=node_id,
                component=definition.key,
            )
            return self.registry.components[definition.fallback or "column"]
        resolution = (
            resolve_lucide_icon(lucide_name) if lucide_name
            else SymbolResolution(status="malformed")
        )
        if not resolution.supported and declared:
            resolution = resolve_symbol(declared)
        if not resolution.supported and lucide_name:
            # Last tier before the placeholder: a reviewed visually similar
            # substitute. It keeps a real glyph on the page but cannot claim
            # fidelity, so the hit is reported as a lossy warning.
            resolution = resolve_lucide_icon_near(lucide_name)
        if resolution.supported:
            assert resolution.canonical is not None
            attributes["data-symbol"] = resolution.canonical
            if resolution.approximate:
                self._diagnostic(
                    "ARKUI_SYMBOL_APPROXIMATED",
                    "warning",
                    f"data-lucide {lucide_name!r} has no exact HarmonyOS "
                    f"symbol; the visually similar {resolution.canonical!r} "
                    "was substituted",
                    node_id=node_id,
                    component=definition.key,
                )
            return definition

        described = (
            f"data-lucide {lucide_name!r}" if lucide_name
            else f"data-symbol {declared!r}" if declared
            else "symbol without data-lucide"
        )
        hint = (
            f"; closest available: {', '.join(resolution.suggestions)}"
            if resolution.suggestions else ""
        )
        attributes.pop("data-symbol", None)
        self._diagnostic(
            "ARKUI_SYMBOL_UNAVAILABLE",
            "warning",
            f"{described} has no HarmonyOS system symbol; exported as an "
            "empty placeholder of the same size" + hint,
            node_id=node_id,
            component=definition.key,
        )
        return self.registry.components[definition.fallback or "column"]

    def _validate_structure(
        self,
        definition: ComponentDefinition,
        parent_index: int | None,
        node_id: str | None,
        authored_component: str,
    ) -> None:
        parent = self.nodes[parent_index] if parent_index is not None else None
        parent_invalid = definition.allowed_parents is not None and (
            parent is None or parent.component not in definition.allowed_parents
        )
        if parent_invalid:
            assert definition.allowed_parents is not None
            expected = ", ".join(sorted(definition.allowed_parents))
            actual = parent.component if parent is not None else "document root"
            self._diagnostic(
                "ARKUI_COMPONENT_PARENT_INVALID",
                "error",
                f"{definition.key!r} requires parent {expected}; found {actual}",
                node_id=node_id,
                component=definition.key,
            )
        if parent is None:
            return
        parent_definition = self.registry.components[parent.component]
        if (
            parent_definition.allowed_children is not None
            and definition.key not in parent_definition.allowed_children
        ):
            if (
                parent.component == "text"
                and authored_component == "symbol"
                and not parent_invalid
            ):
                if parent_index not in self.mixed_symbol_parents:
                    self._diagnostic(
                        "ARKUI_TEXT_SYMBOL_LAYOUT_ADAPTED",
                        "notice",
                        "text directly contains a symbol; the browser layout "
                        "will be exported as a Row or Column with generated "
                        "Text children",
                        node_id=parent.node_id,
                        component=parent.component,
                    )
                self.mixed_symbol_parents.add(parent_index)
                return
            if parent.component in {"list", "grid"} and not parent_invalid:
                # ArkUI's List holds nothing but ListItems and its Grid
                # nothing but GridItems, so a component that may legally sit
                # inside one has exactly one reading here: the content of one
                # entry. Screen IR generates that item wrapper around it and
                # the child keeps its own geometry.
                item_key = "list-item" if parent.component == "list" else "grid-item"
                self._diagnostic(
                    "ARKUI_LIST_CHILD_WRAPPED_AS_ITEM"
                    if parent.component == "list"
                    else "ARKUI_GRID_CHILD_WRAPPED_AS_ITEM",
                    "notice",
                    f"{definition.key!r} directly inside a {parent.component} "
                    f"was exported inside a generated {item_key}; annotate "
                    f"each {parent.component} entry as {item_key}",
                    node_id=node_id,
                    component=definition.key,
                )
                return
            expected = ", ".join(sorted(parent_definition.allowed_children))
            self._diagnostic(
                "ARKUI_COMPONENT_CHILD_INVALID",
                "error",
                f"{parent.component!r} accepts {expected}; found {definition.key!r}",
                node_id=node_id,
                component=definition.key,
            )

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        normalized_tag = tag.lower()
        process, head_cut = self.document.prepare_start(
            normalized_tag, [frame.tag for frame in self.frames],
        )
        if not process:
            return
        if head_cut is not None:
            del self.frames[head_cut:]
        self._close_implied_frames(normalized_tag)
        attributes = {name.lower(): value or "" for name, value in attrs}
        explicit_value = attributes.get("data-component", "").strip().lower()
        native_value = _native_component(normalized_tag, attributes)
        component = explicit_value or native_value
        node_index: int | None = None

        if explicit_value and explicit_value not in self.registry.components:
            self._diagnostic(
                "ARKUI_COMPONENT_UNKNOWN",
                "error",
                f"data-component {explicit_value!r} is not in the ArkUI registry",
                node_id=attributes.get("data-node-id") or None,
                component=explicit_value,
            )
            component = None
        elif explicit_value and native_value and explicit_value != native_value:
            if explicit_value == "list-item":
                # A native control annotated as list-item has exactly one
                # reading: the tag is evidence for what the element is, and
                # its entry-ness is supplied by the generated ListItem that
                # Screen IR wraps around plain list children anyway.
                self._diagnostic(
                    "ARKUI_LIST_ITEM_READ_AS_NATIVE",
                    "notice",
                    f"<{normalized_tag}> annotated as list-item was exported "
                    f"as {native_value!r}; the list entry itself comes from "
                    "a generated list-item",
                    node_id=attributes.get("data-node-id") or None,
                    component=explicit_value,
                )
                component = native_value
            else:
                self._diagnostic(
                    "ARKUI_COMPONENT_TAG_CONFLICT",
                    "error",
                    f"<{normalized_tag}> implies {native_value!r}, "
                    f"not {explicit_value!r}",
                    node_id=attributes.get("data-node-id") or None,
                    component=explicit_value,
                )

        if component is not None:
            definition = self.registry.components[component]
            authored_component = component
            node_id = attributes.get("data-node-id", "").strip() or None
            ui_role = attributes.get("data-ui-role", "").strip() or None
            parent_index = self._parent_index()
            definition = self._promote_orphan_span(definition, parent_index, node_id)
            definition = self._promote_orphan_list_item(
                definition, parent_index, node_id,
            )
            component = definition.key
            if ui_role is not None and not _ROLE_RE.fullmatch(ui_role):
                self._diagnostic(
                    "ARKUI_UI_ROLE_INVALID",
                    "error",
                    f"data-ui-role {ui_role!r} must be lower-case kebab-case",
                    node_id=node_id,
                    component=component,
                )
            self._validate_id(node_id, component, bool(explicit_value))
            if attributes.get(_GENERATED_NODE_ID_ATTR) == _BUTTON_LABEL_REPAIR:
                self._diagnostic(
                    "ARKUI_NODE_ID_GENERATED",
                    "notice",
                    "button's only text child had no data-node-id; generated "
                    f"the stable id {node_id!r} from its parent",
                    node_id=node_id,
                    component=component,
                )
            if not definition.renderer_supported:
                self._diagnostic(
                    "ARKUI_COMPONENT_NOT_RENDERER_SUPPORTED",
                    "error" if explicit_value else "warning",
                    f"{component!r} is planned but not supported by html-to-arkui",
                    node_id=node_id,
                    component=component,
                )
            for attribute in definition.required_metadata:
                if not attributes.get(attribute, "").strip():
                    self._diagnostic(
                        "ARKUI_COMPONENT_METADATA_MISSING",
                        "error" if explicit_value else "warning",
                        f"{component!r} requires {attribute}",
                        node_id=node_id,
                        component=component,
                    )
            if component == "symbol":
                definition = self._resolve_symbol(definition, attributes, node_id)
                component = definition.key
            if component == "image" and not attributes.get("src", "").strip():
                # An Image with nothing to show is a placeholder box the model
                # drew with CSS, and ArkUI's Image cannot stand in for it.
                self._diagnostic(
                    "ARKUI_IMAGE_SRC_MISSING",
                    "warning",
                    "image has no src and was exported as a plain container",
                    node_id=node_id,
                    component=component,
                )
                definition = self.registry.components[
                    definition.fallback or "column"
                ]
                component = definition.key
            self._validate_structure(
                definition, parent_index, node_id, authored_component
            )
            component_depth = (
                1 if parent_index is None else self.node_depths[parent_index] + 1
            )
            if (
                component_depth > MAX_COMPONENT_TREE_DEPTH
                and not self.component_depth_exceeded
            ):
                self.component_depth_exceeded = True
                self._diagnostic(
                    "ARKUI_COMPONENT_TREE_DEPTH_EXCEEDED",
                    "error",
                    "ArkUI component nesting exceeds the supported "
                    f"depth of {MAX_COMPONENT_TREE_DEPTH}",
                    node_id=node_id,
                    component=component,
                )
            node_index = len(self.nodes)
            self.nodes.append(ComponentNode(
                node_id=node_id,
                component=component,
                arkui_component=definition.arkui_component,
                source="explicit" if explicit_value else "html",
                tag=normalized_tag,
                ui_role=ui_role,
                parent_index=parent_index,
                line=self.getpos()[0],
                column=self.getpos()[1],
                metadata=_metadata(attributes),
                attributes=_relevant_attributes(attributes),
                text_content="",
                renderer_supported=definition.renderer_supported,
            ))
            self.node_text.append([])
            self.node_child_counts.append(0)
            self.node_depths.append(component_depth)
            if parent_index is not None:
                self.node_child_counts[parent_index] += 1

        if normalized_tag not in _VOID_TAGS:
            self.frames.append(_Frame(tag=normalized_tag, node_index=node_index))

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)
        normalized = tag.lower()
        if normalized not in _VOID_TAGS:
            _set_text_mode_for_slash_start(self, normalized)

    def handle_endtag(self, tag: str) -> None:
        normalized = tag.lower()
        self.document.observe_end(
            normalized, [frame.tag for frame in self.frames],
        )
        for index in range(len(self.frames) - 1, -1, -1):
            if self.frames[index].tag == normalized:
                del self.frames[index:]
                return

    def handle_data(self, data: str) -> None:
        for frame in reversed(self.frames):
            if frame.node_index is not None:
                self.node_text[frame.node_index].append(
                    (self.node_child_counts[frame.node_index], data)
                )
                return

    def finish(self) -> ComponentMetadataReport:
        self.nodes = [
            replace(
                node,
                text_content=" ".join(" ".join(
                    text for _, text in self.node_text[index]
                ).split()),
                text_runs=_normalized_text_runs(
                    self.node_text[index], self.node_child_counts[index]
                ),
                mixed_symbol_content=index in self.mixed_symbol_parents,
            )
            for index, node in enumerate(self.nodes)
        ]
        child_counts = Counter(
            node.parent_index
            for node in self.nodes
            if node.parent_index is not None
        )
        for index, node in enumerate(self.nodes):
            maximum = self.registry.components[node.component].max_component_children
            actual = child_counts.get(index, 0)
            if maximum is not None and actual > maximum:
                if maximum >= 1:
                    # A single-slot container still holds these children in the
                    # browser; Screen IR gives them the one wrapper ArkUI needs.
                    self._diagnostic(
                        "ARKUI_CONTENT_WRAPPED_FOR_SINGLE_SLOT",
                        "notice",
                        f"{node.component!r} accepts at most {maximum} "
                        f"component child but holds {actual}; they were "
                        "exported inside one generated layout child",
                        node_id=node.node_id,
                        component=node.component,
                        line=node.line,
                        column=node.column,
                    )
                else:
                    self._diagnostic(
                        "ARKUI_COMPONENT_CHILD_COUNT_EXCEEDED",
                        "error",
                        f"{node.component!r} is a leaf component and cannot "
                        f"hold component children; found {actual}",
                        node_id=node.node_id,
                        component=node.component,
                        line=node.line,
                        column=node.column,
                    )
            if node.component == "span" and not node.text_content:
                self._diagnostic(
                    "ARKUI_SPAN_CONTENT_MISSING",
                    "error",
                    "span requires non-empty text content",
                    node_id=node.node_id,
                    component=node.component,
                    line=node.line,
                    column=node.column,
                )
        return ComponentMetadataReport(
            nodes=tuple(self.nodes),
            diagnostics=tuple(sorted(
                self.diagnostics,
                key=lambda item: (
                    item.line, item.column, item.code, item.node_id or ""
                ),
            )),
        )


def analyze_component_metadata(html: str) -> ComponentMetadataReport:
    """Extract component metadata without executing or rewriting the HTML.

    Resolved ``data-symbol`` values are reported in their canonical SDK
    spelling; the HTML document itself is never modified.
    """
    if not isinstance(html, str):
        raise TypeError("html must be a string")
    depth_violation = find_html_tree_depth_violation(html)
    parser = _ComponentMetadataParser()
    parser.feed(html)
    parser.close()
    report = parser.finish()
    if depth_violation is None:
        return report
    line, column = depth_violation
    diagnostics = (*report.diagnostics, ComponentDiagnostic(
        code="ARKUI_HTML_TREE_DEPTH_EXCEEDED",
        severity="error",
        message=(
            "HTML nesting exceeds the supported "
            f"depth of {MAX_HTML_TREE_DEPTH}"
        ),
        line=line,
        column=column,
    ))
    return ComponentMetadataReport(
        nodes=report.nodes,
        diagnostics=tuple(sorted(
            diagnostics,
            key=lambda item: (
                item.line, item.column, item.code, item.node_id or ""
            ),
        )),
    )
