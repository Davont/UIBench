"""Regression tests for safe Harmony HTML interaction enhancement and fallback."""

from __future__ import annotations

import json
from pathlib import Path
import re
import shutil
import subprocess

import pytest


ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / "skills" / "harmony-html-generator"
FINALIZER = SKILL_DIR / "scripts" / "finalize-html.mjs"
STATIC_VALIDATOR = SKILL_DIR / "scripts" / "validate-html.mjs"
INTERACTIVE_VALIDATOR = SKILL_DIR / "scripts" / "validate-interactive.mjs"
ENHANCER = SKILL_DIR / "scripts" / "enhance-html.mjs"
RUNTIME_CSS = SKILL_DIR / "assets" / "harmony-runtime.css"


def _run_node(script: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["node", str(script), *args],
        check=False,
        capture_output=True,
        text=True,
    )


def _source() -> str:
    return """
<main data-component="column" data-node-id="page"
      class="min-h-screen bg-ui-canvas text-ui-fg font-ui flex flex-col">
  <button type="button" data-component="button" data-node-id="page.toggle"
          data-action="toggle-panel" data-target="page.panel"
          aria-expanded="true"
          class="bg-ui-component-subtle rounded-ui-control">
    切换详情
  </button>
  <div id="details-panel" data-component="text" data-node-id="page.panel"
       class="text-ui-body">
    这是静态基线中已经存在的详情。
  </div>
</main>
""".strip()


def _make_static(tmp_path: Path, *, name: str = "static") -> Path:
    source = tmp_path / f"{name}-source.html"
    output = tmp_path / name
    source.write_text(_source(), encoding="utf-8")
    finalized = _run_node(
        FINALIZER,
        "--input",
        str(source),
        "--out",
        str(output),
        "--title",
        "Interaction Test",
        "--theme",
        "dark",
    )
    assert finalized.returncode == 0, finalized.stdout + finalized.stderr
    baseline = _run_node(STATIC_VALIDATOR, str(output / "index.html"))
    assert baseline.returncode == 0, baseline.stdout + baseline.stderr
    return output


def _valid_javascript() -> str:
    return """
const trigger = document.querySelector('[data-action="toggle-panel"]')
const panel = document.querySelector('[data-node-id="page.panel"]')

trigger.addEventListener("click", () => {
  const expanded = trigger.getAttribute("aria-expanded") === "true"
  trigger.setAttribute("aria-expanded", String(!expanded))
  panel.hidden = expanded
  panel.setAttribute("aria-hidden", String(expanded))
})
""".strip()


def _make_interactive(
    tmp_path: Path,
    *,
    javascript: str | None = None,
    script_tag: str = '<script src="assets/app.js" defer></script>',
    name: str = "interactive",
) -> Path:
    baseline = _make_static(tmp_path, name=f"{name}-baseline")
    output = tmp_path / name
    shutil.copytree(baseline, output)
    index = output / "index.html"
    html = index.read_text(encoding="utf-8")
    index.write_text(
        html.replace("</body>", f"{script_tag}\n</body>"),
        encoding="utf-8",
    )
    if javascript is not None:
        (output / "assets" / "app.js").write_text(javascript, encoding="utf-8")
    return output


def _tree_bytes(directory: Path) -> dict[str, bytes]:
    return {
        path.relative_to(directory).as_posix(): path.read_bytes()
        for path in sorted(directory.rglob("*"))
        if path.is_file()
    }


def _error_codes(result: subprocess.CompletedProcess[str]) -> set[str]:
    payload = json.loads(result.stdout)
    return {item["code"] for item in payload["errors"]}


def test_runtime_hidden_attribute_overrides_layout_display() -> None:
    css = RUNTIME_CSS.read_text(encoding="utf-8")

    assert re.search(
        r"\[hidden\]\s*\{\s*display:\s*none\s*!important;\s*\}",
        css,
    )


def test_static_validator_catches_html_id_used_as_data_target(
    tmp_path: Path,
) -> None:
    output = _make_static(tmp_path)
    index = output / "index.html"
    index.write_text(
        index.read_text(encoding="utf-8").replace(
            'data-target="page.panel"',
            'data-target="details-panel" aria-controls="details-panel"',
        ),
        encoding="utf-8",
    )

    result = _run_node(STATIC_VALIDATOR, str(index), "--json")

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    error = next(
        item for item in payload["errors"]
        if item["code"] == "DATA_TARGET_INVALID"
    )
    assert error["nodeId"] == "page.toggle"
    assert "HTML id" in error["message"]
    assert "data-node-id" in error["message"]


def test_interactive_validator_accepts_one_local_deferred_script(
    tmp_path: Path,
) -> None:
    output = _make_interactive(tmp_path, javascript=_valid_javascript())

    result = _run_node(INTERACTIVE_VALIDATOR, str(output / "index.html"), "--json")

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["summary"] == {
        "staticErrors": 0,
        "interactionErrors": 0,
        "errors": 0,
        "warnings": 0,
        "selectors": 2,
    }
    assert payload["staticSummary"]["errors"] == 0


@pytest.mark.parametrize(
    ("script_tag", "expected_code"),
    [
        ("", "SCRIPT_COUNT_INVALID"),
        (
            '<script src="assets/app.js" defer></script>'
            '<script src="assets/app.js" defer></script>',
            "SCRIPT_COUNT_INVALID",
        ),
        (
            '<script src="https://example.com/app.js" defer></script>',
            "SCRIPT_SRC_INVALID",
        ),
        ('<script src="assets/other.js" defer></script>', "SCRIPT_SRC_INVALID"),
        ('<script src="assets/app.js"></script>', "SCRIPT_DEFER_INVALID"),
        (
            '<script src="assets/app.js" defer async></script>',
            "SCRIPT_ATTRIBUTES_INVALID",
        ),
        (
            '<script src="assets/app.js" defer>console.log("inline")</script>',
            "SCRIPT_INLINE_FORBIDDEN",
        ),
    ],
)
def test_interactive_validator_requires_the_exact_script_contract(
    tmp_path: Path,
    script_tag: str,
    expected_code: str,
) -> None:
    output = _make_interactive(
        tmp_path,
        javascript=_valid_javascript(),
        script_tag=script_tag,
    )

    result = _run_node(INTERACTIVE_VALIDATOR, str(output / "index.html"), "--json")

    assert result.returncode == 1
    assert expected_code in _error_codes(result)


def test_interactive_validator_rejects_a_missing_script_file(tmp_path: Path) -> None:
    output = _make_interactive(tmp_path, javascript=None)

    result = _run_node(INTERACTIVE_VALIDATOR, str(output / "index.html"), "--json")

    assert result.returncode == 1
    assert "SCRIPT_FILE_MISSING" in _error_codes(result)


def test_interactive_validator_rejects_inline_event_attributes(tmp_path: Path) -> None:
    output = _make_interactive(tmp_path, javascript=_valid_javascript())
    index = output / "index.html"
    index.write_text(
        index.read_text(encoding="utf-8").replace(
            '<button type="button"',
            '<button type="button" onclick="alert(1)"',
            1,
        ),
        encoding="utf-8",
    )

    result = _run_node(INTERACTIVE_VALIDATOR, str(index), "--json")

    assert result.returncode == 1
    assert "INLINE_EVENT_HANDLER_FORBIDDEN" in _error_codes(result)


@pytest.mark.parametrize(
    ("javascript", "expected_code"),
    [
        ('fetch("/api")', "JS_NETWORK_API_FORBIDDEN"),
        ("const request = new XMLHttpRequest()", "JS_NETWORK_API_FORBIDDEN"),
        ('const socket = new WebSocket("wss://example.com")', "JS_NETWORK_API_FORBIDDEN"),
        ('const events = new EventSource("/events")', "JS_NETWORK_API_FORBIDDEN"),
        ('navigator.sendBeacon("/events", "x")', "JS_NETWORK_API_FORBIDDEN"),
        ('eval("1 + 1")', "JS_DYNAMIC_CODE_FORBIDDEN"),
        ('const fn = new Function("return 1")', "JS_DYNAMIC_CODE_FORBIDDEN"),
        ('document.write("unsafe")', "JS_HTML_INJECTION_FORBIDDEN"),
        ('panel.innerHTML = "unsafe"', "JS_HTML_INJECTION_FORBIDDEN"),
        ('panel.outerHTML = "unsafe"', "JS_HTML_INJECTION_FORBIDDEN"),
        (
            'panel.insertAdjacentHTML("beforeend", "unsafe")',
            "JS_HTML_INJECTION_FORBIDDEN",
        ),
        ('import("./feature.js")', "JS_DYNAMIC_IMPORT_FORBIDDEN"),
        ('localStorage.setItem("x", "1")', "JS_STORAGE_FORBIDDEN"),
        ('sessionStorage.setItem("x", "1")', "JS_STORAGE_FORBIDDEN"),
    ],
)
def test_interactive_validator_rejects_dangerous_javascript_apis(
    tmp_path: Path,
    javascript: str,
    expected_code: str,
) -> None:
    output = _make_interactive(tmp_path, javascript=javascript)

    result = _run_node(INTERACTIVE_VALIDATOR, str(output / "index.html"), "--json")

    assert result.returncode == 1
    assert expected_code in _error_codes(result)


@pytest.mark.parametrize(
    "javascript",
    [
        'document.createElement("div")',
        "panel.cloneNode(true)",
        "panel.appendChild(child)",
        "panel.remove()",
    ],
)
def test_interactive_validator_rejects_dom_tree_creation_or_reordering(
    tmp_path: Path,
    javascript: str,
) -> None:
    output = _make_interactive(tmp_path, javascript=javascript)

    result = _run_node(INTERACTIVE_VALIDATOR, str(output / "index.html"), "--json")

    assert result.returncode == 1
    assert "JS_DOM_MUTATION_FORBIDDEN" in _error_codes(result)


@pytest.mark.parametrize(
    ("javascript", "expected_code"),
    [
        (
            'document.querySelector(\'[data-node-id="missing"]\')?.focus()',
            "DOM_SELECTOR_TARGET_MISSING",
        ),
        (
            'const selector = \'[data-action]\'; document.querySelector(selector)',
            "DOM_SELECTOR_DYNAMIC",
        ),
        (
            'document.querySelector(".rounded-ui-control")?.focus()',
            "DOM_SELECTOR_UNSUPPORTED",
        ),
        ('document.getElementById("missing")?.focus()', "DOM_SELECTOR_TARGET_MISSING"),
    ],
)
def test_interactive_validator_requires_static_declared_dom_targets(
    tmp_path: Path,
    javascript: str,
    expected_code: str,
) -> None:
    output = _make_interactive(tmp_path, javascript=javascript)

    result = _run_node(INTERACTIVE_VALIDATOR, str(output / "index.html"), "--json")

    assert result.returncode == 1
    assert expected_code in _error_codes(result)


def test_interactive_validator_allows_existing_id_and_action_hooks(
    tmp_path: Path,
) -> None:
    javascript = """
const trigger = document.querySelector('[data-action]')
const panel = document.getElementById('details-panel')
trigger.addEventListener('click', () => panel.focus())
""".strip()
    output = _make_interactive(tmp_path, javascript=javascript)

    result = _run_node(INTERACTIVE_VALIDATOR, str(output / "index.html"), "--json")

    assert result.returncode == 0, result.stdout + result.stderr


def test_javascript_words_in_strings_and_comments_are_not_treated_as_apis(
    tmp_path: Path,
) -> None:
    javascript = """
const trigger = document.querySelector('[data-action="toggle-panel"]')
const copy = 'fetch, innerHTML, and localStorage are forbidden API names'
// fetch('/not-a-call')
trigger.addEventListener('click', () => {
  trigger.textContent = copy
})
""".strip()
    output = _make_interactive(tmp_path, javascript=javascript)

    result = _run_node(INTERACTIVE_VALIDATOR, str(output / "index.html"), "--json")

    assert result.returncode == 0, result.stdout + result.stderr


def test_dangerous_api_inside_a_template_expression_is_still_rejected(
    tmp_path: Path,
) -> None:
    output = _make_interactive(
        tmp_path,
        javascript='const message = `result: ${fetch("/api")}`',
    )

    result = _run_node(INTERACTIVE_VALIDATOR, str(output / "index.html"), "--json")

    assert result.returncode == 1
    assert "JS_NETWORK_API_FORBIDDEN" in _error_codes(result)


@pytest.mark.parametrize(
    "remote_url",
    [
        "http://example.com/api",
        "https://example.com/api",
        "ws://example.com/socket",
        "wss://example.com/socket",
        "//example.com/app.js",
    ],
)
def test_interactive_validator_rejects_remote_urls_in_javascript_strings(
    tmp_path: Path,
    remote_url: str,
) -> None:
    javascript = f"""
const trigger = document.querySelector('[data-action="toggle-panel"]')
const remote = '{remote_url}'
trigger.addEventListener('click', () => {{
  trigger.textContent = remote
}})
""".strip()
    output = _make_interactive(tmp_path, javascript=javascript)

    result = _run_node(INTERACTIVE_VALIDATOR, str(output / "index.html"), "--json")

    assert result.returncode == 1
    assert "JS_REMOTE_URL_FORBIDDEN" in _error_codes(result)


@pytest.mark.parametrize(
    "assignment",
    [
        'location = "/next"',
        'location.href = "/next"',
        'window.location.href = "/next"',
        'document.location = "/next"',
        'globalThis.location = "/next"',
    ],
)
def test_interactive_validator_rejects_navigation_assignments(
    tmp_path: Path,
    assignment: str,
) -> None:
    javascript = f"""
const trigger = document.querySelector('[data-action="toggle-panel"]')
trigger.addEventListener('click', () => {{
  {assignment}
}})
""".strip()
    output = _make_interactive(tmp_path, javascript=javascript)

    result = _run_node(INTERACTIVE_VALIDATOR, str(output / "index.html"), "--json")

    assert result.returncode == 1
    assert "JS_EXTERNAL_EFFECT_FORBIDDEN" in _error_codes(result)


def test_interactive_validator_rejects_static_imports(tmp_path: Path) -> None:
    javascript = """
import feature from './feature.js'
const trigger = document.querySelector('[data-action="toggle-panel"]')
trigger.addEventListener('click', feature)
""".strip()
    output = _make_interactive(tmp_path, javascript=javascript)

    result = _run_node(INTERACTIVE_VALIDATOR, str(output / "index.html"), "--json")

    assert result.returncode == 1
    assert "JS_DYNAMIC_IMPORT_FORBIDDEN" in _error_codes(result)


def test_interactive_validator_caps_app_javascript_at_256_kib(
    tmp_path: Path,
) -> None:
    output = _make_interactive(
        tmp_path,
        javascript="x" * (256 * 1024 + 1),
    )

    result = _run_node(INTERACTIVE_VALIDATOR, str(output / "index.html"), "--json")

    assert result.returncode == 1
    assert "SCRIPT_FILE_TOO_LARGE" in _error_codes(result)


def test_class_list_remove_is_an_allowed_state_change(tmp_path: Path) -> None:
    javascript = """
const trigger = document.querySelector('[data-action="toggle-panel"]')
const panel = document.querySelector('[data-node-id="page.panel"]')
trigger.addEventListener('click', () => {
  panel.classList.remove('text-ui-body')
})
""".strip()
    output = _make_interactive(tmp_path, javascript=javascript)

    result = _run_node(INTERACTIVE_VALIDATOR, str(output / "index.html"), "--json")

    assert result.returncode == 0, result.stdout + result.stderr


def test_interactive_validator_rejects_javascript_on_handler_assignment(
    tmp_path: Path,
) -> None:
    javascript = """
const trigger = document.querySelector('[data-action="toggle-panel"]')
trigger.onclick = () => {
  trigger.textContent = 'clicked'
}
""".strip()
    output = _make_interactive(tmp_path, javascript=javascript)

    result = _run_node(INTERACTIVE_VALIDATOR, str(output / "index.html"), "--json")

    assert result.returncode == 1
    codes = _error_codes(result)
    assert "JS_EVENT_HANDLER_PROPERTY_FORBIDDEN" in codes
    assert "JS_EVENT_LISTENER_MISSING" in codes


@pytest.mark.parametrize(
    ("javascript", "expected_code"),
    [
        (
            "document.querySelector('[data-action]').focus()",
            "JS_EVENT_LISTENER_MISSING",
        ),
        (
            "document.addEventListener('click', () => {})",
            "DOM_LOOKUP_MISSING",
        ),
    ],
)
def test_interactive_validator_requires_a_listener_and_static_dom_lookup(
    tmp_path: Path,
    javascript: str,
    expected_code: str,
) -> None:
    output = _make_interactive(tmp_path, javascript=javascript)

    result = _run_node(INTERACTIVE_VALIDATOR, str(output / "index.html"), "--json")

    assert result.returncode == 1
    assert expected_code in _error_codes(result)


def test_interactive_validator_reuses_all_static_validation_rules(
    tmp_path: Path,
) -> None:
    output = _make_interactive(tmp_path, javascript=_valid_javascript())
    index = output / "index.html"
    index.write_text(
        index.read_text(encoding="utf-8").replace(
            'href="assets/harmony-runtime.css"',
            'href="assets/missing-runtime.css"',
        ),
        encoding="utf-8",
    )

    result = _run_node(INTERACTIVE_VALIDATOR, str(index), "--json")

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["summary"]["staticErrors"] > 0
    assert "RUNTIME_STYLESHEET_MISSING" in _error_codes(result)
    static_error = next(
        item for item in payload["errors"]
        if item["code"] == "RUNTIME_STYLESHEET_MISSING"
    )
    assert static_error["source"] == "static"


def test_enhancer_publishes_valid_interaction_without_mutating_static_input(
    tmp_path: Path,
) -> None:
    baseline = _make_static(tmp_path)
    before = _tree_bytes(baseline)
    javascript = tmp_path / "valid-app.js"
    javascript.write_text(_valid_javascript(), encoding="utf-8")
    output = tmp_path / "enhanced"

    result = _run_node(
        ENHANCER,
        "--input",
        str(baseline),
        "--script",
        str(javascript),
        "--out",
        str(output),
    )

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["mode"] == "interactive"
    assert _tree_bytes(baseline) == before
    assert (output / "assets" / "app.js").read_text(encoding="utf-8") == _valid_javascript()
    assert '<script src="assets/app.js" defer></script>' in (
        output / "index.html"
    ).read_text(encoding="utf-8")
    validation = _run_node(INTERACTIVE_VALIDATOR, str(output / "index.html"))
    assert validation.returncode == 0, validation.stdout + validation.stderr


@pytest.mark.parametrize(
    ("name", "javascript"),
    [
        ("dangerous", 'fetch("/api")'),
        ("syntax-error", "const broken ="),
    ],
)
def test_enhancer_falls_back_to_an_identical_static_tree(
    tmp_path: Path,
    name: str,
    javascript: str,
) -> None:
    baseline = _make_static(tmp_path, name=f"{name}-static")
    before = _tree_bytes(baseline)
    script = tmp_path / f"{name}.js"
    script.write_text(javascript, encoding="utf-8")
    output = tmp_path / f"{name}-output"

    result = _run_node(
        ENHANCER,
        "--input",
        str(baseline),
        "--script",
        str(script),
        "--out",
        str(output),
    )

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["mode"] == "fallback-static"
    assert payload["interactionError"]
    assert "published the validated static baseline" in result.stderr
    assert _tree_bytes(output) == before
    assert _tree_bytes(baseline) == before
    assert not (output / "assets" / "app.js").exists()
    validation = _run_node(STATIC_VALIDATOR, str(output / "index.html"))
    assert validation.returncode == 0, validation.stdout + validation.stderr


def test_enhancer_rejects_invalid_static_baseline_without_creating_output(
    tmp_path: Path,
) -> None:
    baseline = _make_static(tmp_path)
    index = baseline / "index.html"
    index.write_text(
        re.sub(r"<!doctype\s+html\s*>", "", index.read_text(encoding="utf-8"), flags=re.I),
        encoding="utf-8",
    )
    before = _tree_bytes(baseline)
    script = tmp_path / "valid-app.js"
    script.write_text(_valid_javascript(), encoding="utf-8")
    output = tmp_path / "must-not-exist"

    result = _run_node(
        ENHANCER,
        "--input",
        str(baseline),
        "--script",
        str(script),
        "--out",
        str(output),
    )

    assert result.returncode != 0
    assert "static baseline is not valid" in result.stderr
    assert not output.exists()
    assert _tree_bytes(baseline) == before
