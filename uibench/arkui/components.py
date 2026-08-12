"""UIBench annotation vocabulary aligned with the html-to-arkui contract.

``component_registry.json`` contains UIBench-owned HTML annotations and
fallbacks. ``renderer_contract.json`` is a pinned copy of the public
html-to-arkui component contract. Only components present in that renderer
contract may be advertised as exportable.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, replace
from functools import lru_cache
from pathlib import Path
from types import MappingProxyType
from typing import Mapping

REGISTRY_FILE = Path(__file__).with_name("component_registry.json")
RENDERER_CONTRACT_FILE = Path(__file__).with_name("renderer_contract.json")
_KEY_RE = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$")
_PHASES = frozenset({"P0", "P1", "P2"})


class ComponentRegistryError(ValueError):
    """Raised when the checked-in ArkUI component registry is invalid."""


@dataclass(frozen=True)
class ComponentDefinition:
    """One platform-neutral component key and its ArkUI target contract."""

    key: str
    arkui_component: str
    category: str
    phase: str
    fallback: str | None
    allowed_children: frozenset[str] | None
    allowed_parents: frozenset[str] | None
    max_component_children: int | None
    required_metadata: tuple[str, ...]
    state_properties: tuple[str, ...]
    actions: tuple[str, ...]
    min_api_version: int | None
    renderer_supported: bool = False


@dataclass(frozen=True)
class RendererComponentDefinition:
    """One component from the public html-to-arkui renderer contract."""

    name: str
    kind: str
    accepts_children: bool
    min_children: int
    max_children: int | None
    allowed_parents: frozenset[str] | None
    allowed_children: frozenset[str] | None
    required_fields: tuple[str, ...]
    min_api_version: int


@dataclass(frozen=True)
class RendererContract:
    """Pinned public renderer contract used for capability gating."""

    contract_version: int
    screen_ir_schema_version: int
    components: Mapping[str, RendererComponentDefinition]


@dataclass(frozen=True)
class ComponentRegistry:
    """Validated immutable ArkUI component registry."""

    schema_version: int
    annotation_version: int
    framework: str
    language: str
    profile: str
    renderer_contract_version: int
    screen_ir_schema_version: int
    components: Mapping[str, ComponentDefinition]

    def keys_for_phases(self, *phases: str) -> tuple[str, ...]:
        selected = set(phases)
        return tuple(
            key
            for key, definition in self.components.items()
            if definition.phase in selected
        )

    def renderer_keys(self) -> tuple[str, ...]:
        """Return only annotation keys currently accepted by the renderer."""
        return tuple(
            key
            for key, definition in self.components.items()
            if definition.renderer_supported
        )

    def planned_keys(self) -> tuple[str, ...]:
        """Return keys UIBench reserves but the renderer cannot export yet."""
        return tuple(
            key
            for key, definition in self.components.items()
            if not definition.renderer_supported
        )


def _string_list(value: object, label: str) -> tuple[str, ...]:
    if value is None:
        return ()
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ComponentRegistryError(f"{label} must be a string array")
    if len(set(value)) != len(value):
        raise ComponentRegistryError(f"{label} contains duplicates")
    return tuple(value)


def _optional_key_set(value: object, label: str) -> frozenset[str] | None:
    if value is None:
        return None
    return frozenset(_string_list(value, label))


def _parse_definition(key: str, value: object) -> ComponentDefinition:
    if not _KEY_RE.fullmatch(key):
        raise ComponentRegistryError(f"invalid component key {key!r}")
    if not isinstance(value, dict):
        raise ComponentRegistryError(f"component {key!r} must be an object")

    arkui_component = value.get("arkuiComponent")
    category = value.get("category")
    phase = value.get("phase")
    fallback = value.get("fallback")
    min_api_version = value.get("minApiVersion")
    max_children = value.get("maxComponentChildren")

    if not isinstance(arkui_component, str) or not arkui_component:
        raise ComponentRegistryError(f"component {key!r} needs arkuiComponent")
    if not isinstance(category, str) or not category:
        raise ComponentRegistryError(f"component {key!r} needs category")
    if phase not in _PHASES:
        raise ComponentRegistryError(f"component {key!r} has invalid phase {phase!r}")
    if fallback is not None and not isinstance(fallback, str):
        raise ComponentRegistryError(f"component {key!r} fallback must be a key or null")
    if min_api_version is not None and (
        not isinstance(min_api_version, int) or isinstance(min_api_version, bool)
        or min_api_version <= 0
    ):
        raise ComponentRegistryError(
            f"component {key!r} minApiVersion must be a positive integer or null"
        )
    if max_children is not None and (
        not isinstance(max_children, int) or isinstance(max_children, bool)
        or max_children < 0
    ):
        raise ComponentRegistryError(
            f"component {key!r} maxComponentChildren must be non-negative"
        )

    return ComponentDefinition(
        key=key,
        arkui_component=arkui_component,
        category=category,
        phase=phase,
        fallback=fallback,
        allowed_children=_optional_key_set(
            value.get("allowedChildren"), f"components.{key}.allowedChildren"
        ),
        allowed_parents=_optional_key_set(
            value.get("allowedParents"), f"components.{key}.allowedParents"
        ),
        max_component_children=max_children,
        required_metadata=_string_list(
            value.get("requiredMetadata"), f"components.{key}.requiredMetadata"
        ),
        state_properties=_string_list(
            value.get("stateProperties"), f"components.{key}.stateProperties"
        ),
        actions=_string_list(value.get("actions"), f"components.{key}.actions"),
        min_api_version=min_api_version,
    )


def validate_renderer_contract(document: object) -> RendererContract:
    """Validate the checked-in public renderer capability snapshot."""
    if not isinstance(document, dict):
        raise ComponentRegistryError("renderer contract must be an object")
    contract_version = document.get("contractVersion")
    screen_ir_schema_version = document.get("screenIrSchemaVersion")
    if not isinstance(contract_version, int) or contract_version <= 0:
        raise ComponentRegistryError("renderer contractVersion must be positive")
    if not isinstance(screen_ir_schema_version, int) or screen_ir_schema_version <= 0:
        raise ComponentRegistryError(
            "renderer screenIrSchemaVersion must be positive"
        )
    raw_components = document.get("components")
    if not isinstance(raw_components, list) or not raw_components:
        raise ComponentRegistryError("renderer components must be a non-empty array")

    components: dict[str, RendererComponentDefinition] = {}
    for index, value in enumerate(raw_components):
        label = f"renderer.components[{index}]"
        if not isinstance(value, dict):
            raise ComponentRegistryError(f"{label} must be an object")
        name = value.get("name")
        kind = value.get("kind")
        accepts_children = value.get("acceptsChildren")
        min_children = value.get("minChildren")
        max_children = value.get("maxChildren")
        min_api_version = value.get("minApiVersion")
        if not isinstance(name, str) or not name:
            raise ComponentRegistryError(f"{label}.name must be non-empty")
        if name in components:
            raise ComponentRegistryError(f"renderer component {name!r} is duplicated")
        if not isinstance(kind, str) or not kind:
            raise ComponentRegistryError(f"{label}.kind must be non-empty")
        if not isinstance(accepts_children, bool):
            raise ComponentRegistryError(f"{label}.acceptsChildren must be boolean")
        if (
            not isinstance(min_children, int)
            or isinstance(min_children, bool)
            or min_children < 0
        ):
            raise ComponentRegistryError(f"{label}.minChildren must be non-negative")
        if max_children is not None and (
            not isinstance(max_children, int)
            or isinstance(max_children, bool)
            or max_children < min_children
        ):
            raise ComponentRegistryError(f"{label}.maxChildren is invalid")
        if (
            not isinstance(min_api_version, int)
            or isinstance(min_api_version, bool)
            or min_api_version <= 0
        ):
            raise ComponentRegistryError(f"{label}.minApiVersion must be positive")
        components[name] = RendererComponentDefinition(
            name=name,
            kind=kind,
            accepts_children=accepts_children,
            min_children=min_children,
            max_children=max_children,
            allowed_parents=(
                None if value.get("allowedParents") is None
                else frozenset(_string_list(
                    value.get("allowedParents"), f"{label}.allowedParents"
                ))
            ),
            allowed_children=(
                None if value.get("allowedChildren") is None
                else frozenset(_string_list(
                    value.get("allowedChildren"), f"{label}.allowedChildren"
                ))
            ),
            required_fields=_string_list(
                value.get("requiredFields"), f"{label}.requiredFields"
            ),
            min_api_version=min_api_version,
        )

    return RendererContract(
        contract_version=contract_version,
        screen_ir_schema_version=screen_ir_schema_version,
        components=MappingProxyType(components),
    )


@lru_cache(maxsize=1)
def load_renderer_contract() -> RendererContract:
    """Load the pinned html-to-arkui public component contract."""
    try:
        document = json.loads(RENDERER_CONTRACT_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ComponentRegistryError(f"cannot load renderer contract: {exc}") from exc
    return validate_renderer_contract(document)


def validate_component_registry(
    document: object,
    renderer_contract: RendererContract | None = None,
) -> ComponentRegistry:
    """Validate a decoded registry document and return an immutable view."""
    if not isinstance(document, dict):
        raise ComponentRegistryError("component registry must be an object")
    if document.get("schemaVersion") != 1:
        raise ComponentRegistryError("schemaVersion must be 1")
    if document.get("annotationVersion") != 1:
        raise ComponentRegistryError("annotationVersion must be 1")

    target = document.get("target")
    if not isinstance(target, dict):
        raise ComponentRegistryError("target must be an object")
    for key in ("framework", "language", "profile"):
        if not isinstance(target.get(key), str) or not target[key]:
            raise ComponentRegistryError(f"target.{key} must be a non-empty string")

    raw_components = document.get("components")
    if not isinstance(raw_components, dict) or not raw_components:
        raise ComponentRegistryError("components must be a non-empty object")
    definitions = {
        key: _parse_definition(key, value)
        for key, value in raw_components.items()
    }
    known = set(definitions)
    for key, definition in definitions.items():
        references = {
            *(definition.allowed_children or ()),
            *(definition.allowed_parents or ()),
        }
        if definition.fallback is not None:
            references.add(definition.fallback)
        unknown = sorted(references - known)
        if unknown:
            raise ComponentRegistryError(
                f"component {key!r} references unknown keys: {', '.join(unknown)}"
            )
    renderer = renderer_contract or load_renderer_contract()
    component_keys_by_name: dict[str, str] = {}
    for key, definition in definitions.items():
        previous = component_keys_by_name.get(definition.arkui_component)
        if previous is not None:
            raise ComponentRegistryError(
                f"components {previous!r} and {key!r} both map to "
                f"{definition.arkui_component!r}"
            )
        component_keys_by_name[definition.arkui_component] = key

    missing_mappings = sorted(set(renderer.components) - set(component_keys_by_name))
    if missing_mappings:
        raise ComponentRegistryError(
            "renderer components have no UIBench annotation key: "
            + ", ".join(missing_mappings)
        )

    for key, definition in tuple(definitions.items()):
        renderer_definition = renderer.components.get(definition.arkui_component)
        if renderer_definition is None:
            continue
        allowed_parents = (
            None if renderer_definition.allowed_parents is None
            else frozenset(
                component_keys_by_name[name]
                for name in renderer_definition.allowed_parents
            )
        )
        allowed_children = (
            None if renderer_definition.allowed_children is None
            else frozenset(
                component_keys_by_name[name]
                for name in renderer_definition.allowed_children
            )
        )
        if (
            definition.min_api_version is not None
            and definition.min_api_version != renderer_definition.min_api_version
        ):
            raise ComponentRegistryError(
                f"component {key!r} minApiVersion conflicts with renderer contract"
            )
        if (
            definition.max_component_children is not None
            and definition.max_component_children != renderer_definition.max_children
        ):
            raise ComponentRegistryError(
                f"component {key!r} maxComponentChildren conflicts with renderer contract"
            )
        if (
            definition.allowed_parents is not None
            and definition.allowed_parents != allowed_parents
        ):
            raise ComponentRegistryError(
                f"component {key!r} allowedParents conflicts with renderer contract"
            )
        if (
            definition.allowed_children is not None
            and definition.allowed_children != allowed_children
        ):
            raise ComponentRegistryError(
                f"component {key!r} allowedChildren conflicts with renderer contract"
            )
        definitions[key] = replace(
            definition,
            allowed_parents=allowed_parents,
            allowed_children=allowed_children,
            max_component_children=renderer_definition.max_children,
            min_api_version=renderer_definition.min_api_version,
            renderer_supported=True,
        )
    return ComponentRegistry(
        schema_version=1,
        annotation_version=1,
        framework=target["framework"],
        language=target["language"],
        profile=target["profile"],
        renderer_contract_version=renderer.contract_version,
        screen_ir_schema_version=renderer.screen_ir_schema_version,
        components=MappingProxyType(definitions),
    )


@lru_cache(maxsize=1)
def load_component_registry() -> ComponentRegistry:
    """Load and validate the checked-in ArkUI component registry."""
    try:
        document = json.loads(REGISTRY_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ComponentRegistryError(f"cannot load component registry: {exc}") from exc
    return validate_component_registry(document)
