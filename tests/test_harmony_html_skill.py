"""Direct regression tests for the bundled Harmony HTML Agent Skill."""

from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import stat
import subprocess


ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / "skills" / "harmony-html-generator"


def _run_node(script: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["node", str(script), *args],
        check=False,
        capture_output=True,
        text=True,
    )


def _source(label: str) -> str:
    return f"""
<main data-component="column" data-node-id="page"
      class="min-h-screen bg-ui-canvas text-ui-fg font-ui flex flex-col">
  <div data-component="text" data-node-id="page.title">
    <span class="text-ui-title">{label}</span>
  </div>
</main>
""".strip()


def _finalize_source(
    tmp_path: Path,
    source_html: str,
    *,
    name: str,
) -> tuple[subprocess.CompletedProcess[str], Path, dict[str, object]]:
    source = tmp_path / f"{name}.html"
    output = tmp_path / name
    source.write_text(source_html, encoding="utf-8")
    result = _run_node(
        SKILL_DIR / "scripts" / "finalize-html.mjs",
        "--input",
        str(source),
        "--out",
        str(output),
        "--title",
        "Test Page",
        "--theme",
        "dark",
    )
    assert result.returncode == 0, result.stderr
    return result, output, json.loads(result.stdout)


def test_skill_declares_the_fast_black_box_workflow() -> None:
    content = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")

    assert "它是该阶段唯一需要加载的参考文件" in content
    assert "禁止读取 `scripts/finalize-html.mjs`" in content
    assert "禁止读取 `assets/harmony-runtime.css`" in content
    assert "禁止读取 [`references/component-contract.json`]" in content
    assert "禁止完整读取 [`references/icon-map.json`]" in content
    assert "禁止创建 todo" in content
    assert "禁止使用 `ls`、`find`、`glob`、`tree`" in content
    assert "`column` 必须有 `flex flex-col`" in content
    assert "`row` 必须有 `flex flex-row`" in content
    assert "独立文字用一个 `text` 节点直接承载文字" in content
    assert "不要把按钮文字误标成 `span`" in content
    assert "`radio` 还必须提供非空 `name` 和 `value`" in content
    assert "可见标签按钮行放在 `tabs` 外" in content
    assert "同类演示数据最多渲染 3 条" in content
    assert 'data-media-query' in content
    assert "只复制命中的图片" in content
    assert "--theme <light|dark> && \\" in content
    assert "禁止重写整个源文件" in content


def test_skill_defaults_actionable_pages_to_interactive_with_static_opt_out() -> None:
    skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    output_modes = skill.split("## 输出模式", 1)[1].split("\n## ", 1)[0]
    workflow = skill.split("## 创建与修改工作流", 1)[1].split("\n## ", 1)[0]
    design_language = (
        SKILL_DIR / "references" / "design-language.md"
    ).read_text(encoding="utf-8")
    interaction_language = (
        SKILL_DIR / "references" / "interaction-language.md"
    ).read_text(encoding="utf-8")

    assert "交互模式（默认最终输出）" in output_modes
    assert "静态模式（显式退出）" in output_modes
    assert "功能描述本身就是交互需求" in output_modes
    assert "单文件 HTML" in output_modes and "不是关闭交互的指令" in output_modes
    assert "不为凑 `app.js` 虚构功能" in output_modes
    assert "只有已选择静态输出时才到此结束" in workflow
    assert "不调用增强器" in workflow
    assert "默认交互输出在静态基线通过后" in workflow
    assert "mode=fallback-static" in workflow
    assert "仅在用户明确要求交互" not in skill
    assert "仅在用户明确要求交互" not in interaction_language
    assert "页面只表达静态结构和初始状态" not in design_language


def test_recommended_minimal_text_and_button_structure_validates(
    tmp_path: Path,
) -> None:
    source = """
<main data-component="column" data-node-id="page"
      class="min-h-screen bg-ui-canvas text-ui-fg font-ui flex flex-col">
  <p data-component="text" data-node-id="page.title" class="text-ui-title">快速播放</p>
  <button type="button" data-component="button" data-node-id="page.pause"
          class="bg-ui-component-subtle rounded-ui-control">暂停</button>
  <button type="button" data-component="button" data-node-id="page.favorite"
          class="bg-ui-component-subtle rounded-ui-control" aria-label="收藏">
    <i data-lucide="heart" data-component="symbol" data-node-id="page.favorite.icon"
       aria-hidden="true" class="size-5"></i>
  </button>
  <button type="button" data-component="button" data-node-id="page.action"
          class="bg-ui-primary text-ui-on-primary rounded-ui-control">
    <div data-component="row" data-node-id="page.action.content"
         class="flex flex-row items-center gap-2">
      <i data-lucide="play" data-component="symbol" data-node-id="page.action.icon"
         aria-hidden="true" class="size-5"></i>
      <span data-component="text" data-node-id="page.action.label">播放</span>
    </div>
  </button>
</main>
""".strip()

    _, output, _ = _finalize_source(tmp_path, source, name="minimal-components")
    validation = _run_node(
        SKILL_DIR / "scripts" / "validate-html.mjs",
        str(output / "index.html"),
    )

    assert validation.returncode == 0, validation.stdout + validation.stderr
    assert "errors=0" in validation.stdout


def test_validator_rejects_full_width_control_row_that_only_wraps_toggle(
    tmp_path: Path,
) -> None:
    _, output, _ = _finalize_source(
        tmp_path,
        """
<main data-component="column" data-node-id="page"
      class="min-h-screen bg-ui-canvas text-ui-fg font-ui flex flex-col">
  <div class="flex flex-row items-center justify-between"
       data-component="row" data-node-id="page.background">
    <div class="flex flex-col min-w-0 flex-1"
         data-component="column" data-node-id="page.background.text">
      <div class="text-ui-body font-medium"
           data-component="text" data-node-id="page.background.title">
        后台播放与锁屏控制
      </div>
      <div class="text-ui-caption text-ui-fg-tertiary"
           data-component="text" data-node-id="page.background.description">
        已开启通知栏与锁屏控制
      </div>
    </div>
    <label class="flex flex-row items-center w-full"
           data-component="row" data-ui-role="control-row"
           data-node-id="page.background.control">
      <input type="checkbox" data-component="toggle"
             data-node-id="page.background.toggle"
             aria-label="后台播放开关" checked>
    </label>
  </div>
</main>
""".strip(),
        name="control-only-full-width-label",
    )

    validation = _run_node(
        SKILL_DIR / "scripts" / "validate-html.mjs",
        str(output / "index.html"),
    )

    assert validation.returncode == 1
    assert (
        "ERROR CONTROL_ROW_LABEL_CONTENT_MISSING "
        "[page.background.control]"
    ) in validation.stdout


def test_complete_control_rows_keep_label_content_and_controls_together(
    tmp_path: Path,
) -> None:
    _, output, _ = _finalize_source(
        tmp_path,
        """
<main data-component="column" data-node-id="page"
      class="min-h-screen bg-ui-canvas text-ui-fg font-ui flex flex-col">
  <label class="flex flex-row items-center justify-between w-full"
         data-component="row" data-ui-role="control-row"
         data-node-id="page.background">
    <div class="flex flex-col min-w-0 flex-1"
         data-component="column" data-node-id="page.background.text">
      <div class="text-ui-body font-medium"
           data-component="text" data-node-id="page.background.title">
        后台播放与锁屏控制
      </div>
      <div class="text-ui-caption text-ui-fg-tertiary"
           data-component="text" data-node-id="page.background.description">
        已开启通知栏与锁屏控制
      </div>
    </div>
    <input type="checkbox" data-component="toggle"
           data-node-id="page.background.toggle"
           aria-label="后台播放开关" checked>
  </label>
  <label class="flex flex-row items-center w-full gap-2"
         data-component="row" data-ui-role="control-row"
         data-node-id="page.quality.lossless">
    <input type="radio" data-component="radio"
           data-node-id="page.quality.lossless.radio"
           name="quality" value="lossless" aria-label="无损音质">
    <div class="text-ui-body" data-component="text"
         data-node-id="page.quality.lossless.label">无损音质</div>
  </label>
</main>
""".strip(),
        name="complete-control-row-label",
    )

    validation = _run_node(
        SKILL_DIR / "scripts" / "validate-html.mjs",
        str(output / "index.html"),
    )

    assert validation.returncode == 0, validation.stdout + validation.stderr
    assert "errors=0" in validation.stdout


def test_finalize_reruns_when_skill_assets_are_read_only(tmp_path: Path) -> None:
    copied_skill = tmp_path / "harmony-html-generator"
    shutil.copytree(SKILL_DIR, copied_skill)
    copied_assets = copied_skill / "assets"
    for path in sorted(copied_assets.rglob("*"), reverse=True):
        os.chmod(path, 0o555 if path.is_dir() else 0o444)
    os.chmod(copied_assets, 0o555)

    source = tmp_path / "source.html"
    output = tmp_path / "deliverable"
    finalize = copied_skill / "scripts" / "finalize-html.mjs"
    validate = copied_skill / "scripts" / "validate-html.mjs"
    args = (
        "--input",
        str(source),
        "--out",
        str(output),
        "--title",
        "Test Page",
        "--theme",
        "dark",
    )

    source.write_text(_source("First pass"), encoding="utf-8")
    first = _run_node(finalize, *args)
    assert first.returncode == 0, first.stderr

    runtime = output / "assets" / "harmony-runtime.css"
    fonts = output / "assets" / "fonts"
    assert runtime.stat().st_mode & stat.S_IWUSR
    assert fonts.stat().st_mode & stat.S_IWUSR
    assert all(
        font.stat().st_mode & stat.S_IWUSR
        for font in fonts.iterdir()
        if font.is_file()
    )

    source.write_text(_source("Second pass"), encoding="utf-8")
    second = _run_node(finalize, *args)
    assert second.returncode == 0, second.stderr
    assert "Second pass" in (output / "index.html").read_text(encoding="utf-8")

    validation = _run_node(validate, str(output / "index.html"))
    assert validation.returncode == 0, validation.stdout + validation.stderr
    assert "errors=0" in validation.stdout


def test_finalize_adds_only_missing_required_layout_classes(tmp_path: Path) -> None:
    source = """
<main data-component="column" data-node-id="page"
      class="min-h-screen bg-ui-canvas text-ui-fg font-ui flex">
  <div data-component="row" data-node-id="page.row" class="items-center"></div>
  <div data-component="stack" data-node-id="page.stack"></div>
  <div data-component="grid" data-node-id="page.grid" class="grid-cols-2">
    <div data-component="grid-item" data-node-id="page.grid.item"></div>
  </div>
</main>
""".strip()

    _, output, payload = _finalize_source(
        tmp_path,
        source,
        name="missing-layout-classes",
    )
    html = (output / "index.html").read_text(encoding="utf-8")

    assert 'class="min-h-screen bg-ui-canvas text-ui-fg font-ui flex flex-col"' in html
    assert 'class="items-center flex flex-row"' in html
    assert 'data-node-id="page.stack" class="relative"' in html
    assert 'class="grid-cols-2 grid"' in html
    assert payload["normalizations"] == {
        "count": 4,
        "nodes": [
            {
                "nodeId": "page",
                "component": "column",
                "addedClasses": ["flex-col"],
            },
            {
                "nodeId": "page.row",
                "component": "row",
                "addedClasses": ["flex", "flex-row"],
            },
            {
                "nodeId": "page.stack",
                "component": "stack",
                "addedClasses": ["relative"],
            },
            {
                "nodeId": "page.grid",
                "component": "grid",
                "addedClasses": ["grid"],
            },
        ],
    }

    validation = _run_node(
        SKILL_DIR / "scripts" / "validate-html.mjs",
        str(output / "index.html"),
    )
    assert validation.returncode == 0, validation.stdout + validation.stderr


def test_finalize_leaves_conflicting_layout_classes_unchanged(tmp_path: Path) -> None:
    source = """
<main data-component="column" data-node-id="page"
      class="min-h-screen bg-ui-canvas text-ui-fg font-ui grid">
  <div data-component="row" data-node-id="page.row" class="flex flex-col"></div>
  <div data-component="stack" data-node-id="page.stack" class="absolute"></div>
  <div data-component="grid" data-node-id="page.grid" class="flex"></div>
</main>
""".strip()

    _, output, payload = _finalize_source(
        tmp_path,
        source,
        name="conflicting-layout-classes",
    )
    html = (output / "index.html").read_text(encoding="utf-8")

    assert 'class="min-h-screen bg-ui-canvas text-ui-fg font-ui grid"' in html
    assert 'data-node-id="page.row" class="flex flex-col"' in html
    assert 'data-node-id="page.stack" class="absolute"' in html
    assert 'data-node-id="page.grid" class="flex"' in html
    assert payload["normalizations"] == {"count": 0, "nodes": []}


def test_finalize_layout_class_normalization_is_idempotent(tmp_path: Path) -> None:
    first_result, first_output, first_payload = _finalize_source(
        tmp_path,
        """
<main data-component="column" data-node-id="page"
      class="min-h-screen bg-ui-canvas text-ui-fg font-ui">
  <div data-component="row" data-node-id="page.row"></div>
</main>
""".strip(),
        name="first-pass",
    )
    assert first_result.returncode == 0
    assert first_payload["normalizations"]["count"] == 2

    first_html = (first_output / "index.html").read_text(encoding="utf-8")
    second_result, second_output, second_payload = _finalize_source(
        tmp_path,
        first_html,
        name="second-pass",
    )
    assert second_result.returncode == 0
    assert second_payload["normalizations"] == {"count": 0, "nodes": []}
    assert (second_output / "index.html").read_text(encoding="utf-8") == first_html


def test_finalize_scanner_preserves_greater_than_inside_quoted_attribute(
    tmp_path: Path,
) -> None:
    source = """
<main data-component="column" data-node-id="page"
      class="min-h-screen bg-ui-canvas text-ui-fg font-ui">
  <div aria-label="上一项 > 下一项" data-component="row"
       data-node-id="page.row" class="items-center"></div>
</main>
""".strip()

    _, output, payload = _finalize_source(
        tmp_path,
        source,
        name="quoted-greater-than",
    )
    html = (output / "index.html").read_text(encoding="utf-8")

    assert 'aria-label="上一项 > 下一项"' in html
    assert 'class="items-center flex flex-row"' in html
    assert payload["normalizations"]["count"] == 2


def test_runtime_accepts_perf_v1_width_and_subtle_foreground_classes(
    tmp_path: Path,
) -> None:
    runtime_source = (
        SKILL_DIR / "assets" / "harmony-runtime.css"
    ).read_text(encoding="utf-8")
    design_language = (
        SKILL_DIR / "references" / "design-language.md"
    ).read_text(encoding="utf-8")

    assert ".w-6 { width: 24px; }" in runtime_source
    assert ".w-10 { width: 40px; }" in runtime_source
    assert ".text-ui-fg-subtle { color: var(--ui-fg-tertiary); }" in runtime_source
    assert runtime_source.count("--ui-fg-tertiary:") == 2
    assert "`text-ui-fg-subtle` 是 `text-ui-fg-tertiary` 的兼容别名" in design_language
    assert "`w-6 w-10 w-full" in design_language

    _, output, _ = _finalize_source(
        tmp_path,
        """
<main data-component="column" data-node-id="page"
      class="min-h-screen bg-ui-canvas text-ui-fg font-ui flex flex-col">
  <div data-component="row" data-node-id="page.row" class="flex flex-row">
    <div data-component="column" data-node-id="page.index"
         class="flex flex-col w-6"></div>
    <div data-component="text" data-node-id="page.time"
         class="w-10 text-ui-fg-subtle">
      <span data-component="span" data-node-id="page.time.label"
            class="text-ui-caption text-ui-fg-subtle">02:14</span>
    </div>
  </div>
</main>
""".strip(),
        name="perf-v1-runtime-classes",
    )
    validation = _run_node(
        SKILL_DIR / "scripts" / "validate-html.mjs",
        str(output / "index.html"),
    )

    assert validation.returncode == 0, validation.stdout + validation.stderr
    assert "RUNTIME_CLASS_UNKNOWN" not in validation.stdout


def test_runtime_accepts_perf_v2_size_and_border_classes(tmp_path: Path) -> None:
    runtime_source = (
        SKILL_DIR / "assets" / "harmony-runtime.css"
    ).read_text(encoding="utf-8")
    design_language = (
        SKILL_DIR / "references" / "design-language.md"
    ).read_text(encoding="utf-8")
    skill_source = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")

    assert ".h-10 { height: 40px; }" in runtime_source
    assert ".size-10 { width: 40px; height: 40px; }" in runtime_source
    assert (
        '[data-component="symbol"].size-10 '
        "{ width: 40px; height: 40px; font-size: 40px; }"
    ) in runtime_source
    assert ".border-b { border-bottom-style: solid; border-bottom-width: 1px; }" in runtime_source
    assert ".border-b-2 { border-bottom-style: solid; border-bottom-width: 2px; }" in runtime_source
    assert ".border-ui-primary { border-color: var(--ui-primary); }" in runtime_source
    assert "`w-6 w-10 w-full h-10 h-full" in design_language
    assert "border-b-2 border-ui-primary" in design_language
    assert "内置离线图片库" in skill_source
    assert "不读取图片 manifest" in skill_source

    _, output, _ = _finalize_source(
        tmp_path,
        """
<main data-component="column" data-node-id="page"
      class="min-h-screen bg-ui-canvas text-ui-fg font-ui flex flex-col">
  <div data-component="row" data-node-id="page.tabs"
       class="flex flex-row h-10 border-b border-ui-divider">
    <button type="button" data-component="button" data-node-id="page.active"
            class="size-10 border-b-2 border-ui-primary" aria-label="当前标签">
      <i data-lucide="music" data-component="symbol" data-node-id="page.active.icon"
         aria-hidden="true" class="size-10"></i>
    </button>
  </div>
</main>
""".strip(),
        name="perf-v2-runtime-classes",
    )
    validation = _run_node(
        SKILL_DIR / "scripts" / "validate-html.mjs",
        str(output / "index.html"),
    )

    assert validation.returncode == 0, validation.stdout + validation.stderr
    assert "RUNTIME_CLASS_UNKNOWN" not in validation.stdout


def test_builtin_media_catalog_is_self_contained() -> None:
    media_root = SKILL_DIR / "assets" / "media-library"
    manifest = json.loads((media_root / "manifest.json").read_text(encoding="utf-8"))
    photos = [
        photo
        for category in manifest["categories"].values()
        for photo in category["photos"]
    ]

    assert manifest["source"] == "unsplash"
    assert manifest["bundled_variant"] == "small"
    assert manifest["photo_count"] == len(photos) == 132
    assert len(manifest["categories"]) == 11
    assert all(set(photo["files"]) == {"small"} for photo in photos)
    assert all((media_root / photo["files"]["small"]).is_file() for photo in photos)
    assert all(not (media_root / photo["files"]["small"]).is_symlink() for photo in photos)
    assert all(
        os.path.commonpath([
            str(media_root.resolve()),
            str((media_root / photo["files"]["small"]).resolve()),
        ]) == str(media_root.resolve())
        for photo in photos
    )


def test_finalize_materializes_only_selected_builtin_media_deterministically(
    tmp_path: Path,
) -> None:
    source = """
<main data-component="column" data-node-id="page"
      class="min-h-screen bg-ui-canvas text-ui-fg font-ui flex flex-col">
  <img data-component="image" data-node-id="page.hero"
       data-media-query="luxury resort ocean"
       data-media-orientation="landscape"
       alt="海边度假酒店" class="w-full aspect-video object-cover">
  <img data-component="image" data-node-id="page.suite"
       data-media-query="luxury resort ocean"
       data-media-orientation="landscape"
       alt="酒店套房" class="w-full aspect-video object-cover">
</main>
""".strip()

    _, first_output, first_payload = _finalize_source(
        tmp_path,
        source,
        name="builtin-media-first",
    )
    _, second_output, second_payload = _finalize_source(
        tmp_path,
        source,
        name="builtin-media-second",
    )

    first_items = first_payload["media"]["items"]
    second_items = second_payload["media"]["items"]
    assert first_payload["media"]["count"] == 2
    assert [item["photoId"] for item in first_items] == [
        item["photoId"] for item in second_items
    ]
    assert len({item["photoId"] for item in first_items}) == 2
    assert all(item["category"] == "travel" for item in first_items)
    manifest = json.loads(
        (SKILL_DIR / "assets" / "media-library" / "manifest.json").read_text(
            encoding="utf-8",
        ),
    )
    photo_by_id = {
        photo["id"]: photo
        for category in manifest["categories"].values()
        for photo in category["photos"]
    }
    people_keywords = {"couple", "man", "people", "person", "woman"}
    assert all(
        people_keywords.isdisjoint(photo_by_id[item["photoId"]]["keywords"])
        for item in first_items
    )

    html = (first_output / "index.html").read_text(encoding="utf-8")
    assert html.count('data-media-query="luxury resort ocean"') == 2
    assert html.count('src="assets/media/builtin/travel/') == 2
    copied = sorted((first_output / "assets" / "media" / "builtin").rglob("*.jpg"))
    assert len(copied) == 2
    assert all(path.stat().st_size > 0 for path in copied)

    _, third_output, third_payload = _finalize_source(
        tmp_path,
        html,
        name="builtin-media-refinalized",
    )
    assert [item["photoId"] for item in third_payload["media"]["items"]] == [
        item["photoId"] for item in first_items
    ]
    assert len(list((third_output / "assets" / "media" / "builtin").rglob("*.jpg"))) == 2

    validation = _run_node(
        SKILL_DIR / "scripts" / "validate-html.mjs",
        str(first_output / "index.html"),
    )
    assert validation.returncode == 0, validation.stdout + validation.stderr


def test_builtin_media_matches_photo_keywords_across_categories(
    tmp_path: Path,
) -> None:
    _, output, payload = _finalize_source(
        tmp_path,
        """
<main data-component="column" data-node-id="page"
      class="min-h-screen bg-ui-canvas text-ui-fg font-ui flex flex-col">
  <img data-component="image" data-node-id="page.breakfast"
       data-media-query="croissant" data-media-orientation="portrait"
       alt="窗边的可颂早餐" class="w-full aspect-video object-cover">
</main>
""".strip(),
        name="cross-category-media-keyword",
    )

    assert payload["media"]["count"] == 1
    assert payload["media"]["items"][0]["category"] == "books"
    assert payload["media"]["items"][0]["photoId"] == "b4lcWyZ0acg"
    assert len(list((output / "assets" / "media" / "builtin").rglob("*.jpg"))) == 1


def test_builtin_media_distinguishes_subjects_from_ambiguous_people_terms(
    tmp_path: Path,
) -> None:
    _, _, payload = _finalize_source(
        tmp_path,
        """
<main data-component="column" data-node-id="page"
      class="min-h-screen bg-ui-canvas text-ui-fg font-ui flex flex-col">
  <img data-component="image" data-node-id="page.cat"
       data-media-query="cat portrait" alt="猫咪肖像">
  <img data-component="image" data-node-id="page.ai"
       data-media-query="AI model" alt="人工智能模型">
</main>
""".strip(),
        name="ambiguous-people-media-terms",
    )

    items = payload["media"]["items"]
    assert [item["category"] for item in items] == ["animal", "tech"]

    manifest = json.loads(
        (SKILL_DIR / "assets" / "media-library" / "manifest.json").read_text(
            encoding="utf-8",
        ),
    )
    photo_by_id = {
        photo["id"]: photo
        for category in manifest["categories"].values()
        for photo in category["photos"]
    }
    assert "cat" in photo_by_id[items[0]["photoId"]]["keywords"]


def test_builtin_media_fallback_prefers_a_photo_without_people(
    tmp_path: Path,
) -> None:
    _, _, payload = _finalize_source(
        tmp_path,
        """
<main data-component="column" data-node-id="page"
      class="min-h-screen bg-ui-canvas text-ui-fg font-ui flex flex-col">
  <img data-component="image" data-node-id="page.background"
       data-media-query="calm neutral background" alt="中性背景">
</main>
""".strip(),
        name="non-person-media-fallback",
    )

    item = payload["media"]["items"][0]
    manifest = json.loads(
        (SKILL_DIR / "assets" / "media-library" / "manifest.json").read_text(
            encoding="utf-8",
        ),
    )
    photo_by_id = {
        photo["id"]: photo
        for category in manifest["categories"].values()
        for photo in category["photos"]
    }
    people_keywords = {
        "athlete", "boy", "bride", "child", "children", "colleague",
        "couple", "customer", "family", "friends", "girl", "groom",
        "headshot", "human", "lady", "man", "member", "people", "person",
        "runner", "selfie", "student", "woman",
    }

    assert item["category"] == "life"
    assert people_keywords.isdisjoint(photo_by_id[item["photoId"]]["keywords"])


def test_finalize_rejects_invalid_builtin_media_orientation(tmp_path: Path) -> None:
    source = tmp_path / "invalid-media.html"
    output = tmp_path / "invalid-media"
    source.write_text(
        """
<main data-component="column" data-node-id="page"
      class="min-h-screen bg-ui-canvas text-ui-fg font-ui flex flex-col">
  <img data-component="image" data-node-id="page.hero"
       data-media-query="mountain landscape" data-media-orientation="wide"
       alt="山景" class="w-full aspect-video object-cover">
</main>
""".strip(),
        encoding="utf-8",
    )

    result = _run_node(
        SKILL_DIR / "scripts" / "finalize-html.mjs",
        "--input",
        str(source),
        "--out",
        str(output),
        "--title",
        "Invalid media",
        "--theme",
        "light",
    )

    assert result.returncode == 2
    assert "invalid data-media-orientation: wide [page.hero]" in result.stderr


def test_finalize_does_not_replace_user_media_with_a_query(tmp_path: Path) -> None:
    source = tmp_path / "user-media-conflict.html"
    output = tmp_path / "user-media-conflict"
    source.write_text(
        """
<main data-component="column" data-node-id="page"
      class="min-h-screen bg-ui-canvas text-ui-fg font-ui flex flex-col">
  <img data-component="image" data-node-id="page.hero"
       src="assets/media/user-photo.jpg" data-media-query="mountain landscape"
       alt="用户提供的山景" class="w-full aspect-video object-cover">
</main>
""".strip(),
        encoding="utf-8",
    )

    result = _run_node(
        SKILL_DIR / "scripts" / "finalize-html.mjs",
        "--input",
        str(source),
        "--out",
        str(output),
        "--title",
        "User media",
        "--theme",
        "light",
    )

    assert result.returncode == 2
    assert "data-media-query cannot replace a user-provided src [page.hero]" in result.stderr


def test_finalize_cleans_only_reserved_builtin_media(tmp_path: Path) -> None:
    output = tmp_path / "media-cleanup"
    user_media = output / "assets" / "media" / "user-photo.jpg"
    stale_builtin = output / "assets" / "media" / "builtin" / "stale.jpg"
    user_media.parent.mkdir(parents=True)
    stale_builtin.parent.mkdir(parents=True)
    user_media.write_bytes(b"user")
    stale_builtin.write_bytes(b"stale")

    _, finalized_output, payload = _finalize_source(
        tmp_path,
        _source("No built-in media"),
        name="media-cleanup",
    )

    assert payload["media"] == {"count": 0, "items": []}
    assert (finalized_output / "assets" / "media" / "user-photo.jpg").read_bytes() == b"user"
    assert not (finalized_output / "assets" / "media" / "builtin").exists()


def test_finalize_rejects_output_inside_the_skill(tmp_path: Path) -> None:
    copied_skill = tmp_path / "harmony-html-generator"
    shutil.copytree(SKILL_DIR, copied_skill)
    source = tmp_path / "source.html"
    source.write_text(_source("Unsafe output"), encoding="utf-8")
    runtime = copied_skill / "assets" / "harmony-runtime.css"
    runtime_before = runtime.read_bytes()

    result = _run_node(
        copied_skill / "scripts" / "finalize-html.mjs",
        "--input",
        str(source),
        "--out",
        str(copied_skill),
        "--title",
        "Unsafe output",
        "--theme",
        "light",
    )

    assert result.returncode == 2
    assert "--out must not be the Skill directory" in result.stderr
    assert runtime.read_bytes() == runtime_before


def test_finalize_rejects_symlinked_output_assets(tmp_path: Path) -> None:
    source = tmp_path / "source.html"
    source.write_text(_source("Symlink output"), encoding="utf-8")
    output = tmp_path / "symlink-output"
    external = tmp_path / "external-assets"
    output.mkdir()
    external.mkdir()
    sentinel = external / "sentinel.txt"
    sentinel.write_text("keep", encoding="utf-8")
    (output / "assets").symlink_to(external, target_is_directory=True)

    result = _run_node(
        SKILL_DIR / "scripts" / "finalize-html.mjs",
        "--input",
        str(source),
        "--out",
        str(output),
        "--title",
        "Symlink output",
        "--theme",
        "light",
    )

    assert result.returncode == 2
    assert "output asset path must not contain symbolic links" in result.stderr
    assert sentinel.read_text(encoding="utf-8") == "keep"


def test_finalize_rejects_symlinked_builtin_media_source(tmp_path: Path) -> None:
    copied_skill = tmp_path / "harmony-html-generator"
    shutil.copytree(SKILL_DIR, copied_skill)
    media_root = copied_skill / "assets" / "media-library"
    external = tmp_path / "outside.jpg"
    external.write_bytes(b"outside")
    unsafe_dir = media_root / "unsafe"
    unsafe_dir.mkdir()
    (unsafe_dir / "linked-small.jpg").symlink_to(external)
    manifest = {
        "version": 1,
        "fallback_categories": ["unsafe"],
        "categories": {
            "unsafe": {
                "match_keywords": ["unsafe"],
                "photos": [{
                    "id": "unsafe-photo",
                    "files": {"small": "unsafe/linked-small.jpg"},
                    "orientation": "landscape",
                    "keywords": ["unsafe"],
                    "photographer": "",
                }],
            },
        },
    }
    (media_root / "manifest.json").write_text(
        json.dumps(manifest),
        encoding="utf-8",
    )
    source = tmp_path / "unsafe-source.html"
    source.write_text(
        """
<main data-component="column" data-node-id="page"
      class="min-h-screen bg-ui-canvas text-ui-fg font-ui flex flex-col">
  <img data-component="image" data-node-id="page.hero"
       data-media-query="unsafe" alt="不安全图片">
</main>
""".strip(),
        encoding="utf-8",
    )

    result = _run_node(
        copied_skill / "scripts" / "finalize-html.mjs",
        "--input",
        str(source),
        "--out",
        str(tmp_path / "unsafe-output"),
        "--title",
        "Unsafe media",
        "--theme",
        "light",
    )

    assert result.returncode == 2
    assert "built-in media source must be a regular file" in result.stderr


def test_finalize_generates_stable_unique_ids_for_unlabelled_symbol_icons(
    tmp_path: Path,
) -> None:
    source = """
<main data-component="column" data-node-id="page"
      class="min-h-screen bg-ui-canvas text-ui-fg font-ui flex flex-col">
  <button type="button" data-component="button" data-node-id="page.action"
          aria-label="收藏操作">
    <div data-component="row" data-node-id="page.action.content"
         class="flex flex-row">
      <i data-lucide="heart" data-component="symbol" aria-hidden="true"></i>
      <i data-lucide="heart" data-component="symbol" aria-hidden="true"></i>
      <i data-lucide="x" data-component="symbol" aria-hidden="true"></i>
      <i data-lucide="x" data-component="symbol"
         data-node-id="page.action.content.icon-x" aria-hidden="true"></i>
    </div>
  </button>
</main>
""".strip()

    _, first_output, first_payload = _finalize_source(
        tmp_path,
        source,
        name="generated-symbol-node-ids",
    )
    first_html = (first_output / "index.html").read_text(encoding="utf-8")

    assert 'data-node-id="page.action.content.icon-heart"' in first_html
    assert 'data-node-id="page.action.content.icon-heart-2"' in first_html
    assert 'data-node-id="page.action.content.icon-x-2"' in first_html
    assert first_html.count('data-node-id="page.action.content.icon-x"') == 1
    assert first_payload["normalizations"] == {
        "count": 3,
        "nodes": [
            {
                "nodeId": "page.action.content.icon-heart",
                "component": "symbol",
                "addedNodeId": "page.action.content.icon-heart",
                "ancestorNodeId": "page.action.content",
                "iconName": "heart",
            },
            {
                "nodeId": "page.action.content.icon-heart-2",
                "component": "symbol",
                "addedNodeId": "page.action.content.icon-heart-2",
                "ancestorNodeId": "page.action.content",
                "iconName": "heart",
            },
            {
                "nodeId": "page.action.content.icon-x-2",
                "component": "symbol",
                "addedNodeId": "page.action.content.icon-x-2",
                "ancestorNodeId": "page.action.content",
                "iconName": "x",
            },
        ],
    }

    validation = _run_node(
        SKILL_DIR / "scripts" / "validate-html.mjs",
        str(first_output / "index.html"),
    )
    assert validation.returncode == 0, validation.stdout + validation.stderr

    _, second_output, second_payload = _finalize_source(
        tmp_path,
        first_html,
        name="generated-symbol-node-ids-second-pass",
    )
    assert second_payload["normalizations"] == {"count": 0, "nodes": []}
    assert (second_output / "index.html").read_text(encoding="utf-8") == first_html


def test_finalize_does_not_guess_symbol_ids_without_the_safe_shape(
    tmp_path: Path,
) -> None:
    source = """
<i data-lucide="heart" data-component="symbol" aria-hidden="true"></i>
<main data-component="column" data-node-id="page"
      class="min-h-screen bg-ui-canvas text-ui-fg font-ui flex flex-col">
  <span data-lucide="heart" data-component="symbol" aria-hidden="true"></span>
  <i data-lucide="x" data-component="button" aria-hidden="true"></i>
  <i data-lucide="x" data-component="symbol"
     data-node-id="page.explicit-icon" aria-hidden="true"></i>
</main>
""".strip()

    _, output, payload = _finalize_source(
        tmp_path,
        source,
        name="unsafe-symbol-node-id-shapes",
    )
    html = (output / "index.html").read_text(encoding="utf-8")

    assert payload["normalizations"] == {"count": 0, "nodes": []}
    assert html.count('data-node-id="page.explicit-icon"') == 1
    assert "page.icon-heart" not in html
    assert "page.icon-x" not in html
