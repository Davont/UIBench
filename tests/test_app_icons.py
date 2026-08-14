from __future__ import annotations

import hashlib
import json
import struct

from fastapi.testclient import TestClient

import app as app_mod
from uibench.app_icons import (
    APP_ICONS,
    APP_ICON_DIR,
    app_icon_catalog_instruction,
    app_icons_for_prompt,
    repair_builtin_app_icon_bindings,
    repair_builtin_app_icon_layout,
)


def test_catalog_is_local_complete_and_request_scoped() -> None:
    assert [icon.slug for icon in app_icons_for_prompt("微信和支付宝")] == [
        "wechat", "alipay",
    ]
    assert app_icons_for_prompt("普通登录页") == ()
    assert app_icons_for_prompt("展示常用应用图标横排") == APP_ICONS
    assert app_icon_catalog_instruction("普通登录页") == ""
    instruction = app_icon_catalog_instruction("展示常用应用图标")
    assert 'data-component="grid"' in instruction
    assert "grid grid-cols-4" in instruction
    assert "不要把图标集合的父节点写成 flex-col" in instruction

    for icon in APP_ICONS:
        path = APP_ICON_DIR / f"{icon.slug}.png"
        payload = path.read_bytes()
        assert payload.startswith(b"\x89PNG\r\n\x1a\n"), icon.slug
        width, height = struct.unpack(">II", payload[16:24])
        assert (width, height) == (256, 256)


def test_brand_assets_have_pinned_provenance() -> None:
    provenance = json.loads((APP_ICON_DIR / "sources.json").read_text())

    brand_slugs = {icon.slug for icon in APP_ICONS if not icon.generic_only}
    assert set(provenance["icons"]) == brand_slugs
    for slug, source in provenance["icons"].items():
        assert source["source"].startswith("https://"), slug
        assert source["assetKind"] == "apple-app-store-artwork"
        assert source["version"]
        assert source["releaseDate"]
        assert source["checkedAt"] == "2026-08-14"
        digest = hashlib.sha256(
            (APP_ICON_DIR / f"{slug}.png").read_bytes()
        ).hexdigest()
        assert digest == source["localPngSha256"]
        assert not (APP_ICON_DIR / f"{slug}.svg").exists()


def test_reused_generic_photo_is_rebound_by_adjacent_app_label() -> None:
    html = """<div data-component="list">
      <div data-component="list-item">
        <img data-node-id="privacy.apps_icons.item1.img"
             src="/gallery/tech/generic.jpg" alt="应用图标" />
        <span data-component="text">微信</span>
      </div>
      <div data-component="list-item">
        <img data-node-id="privacy.apps_icons.item2.img"
             src="/gallery/tech/generic.jpg" alt="应用图标">
        <span data-component="text">支付宝</span>
      </div>
    </div>"""

    repaired = repair_builtin_app_icon_bindings(html)

    assert repaired.count("/gallery/tech/generic.jpg") == 0
    assert 'src="/assets/app-icons/wechat.png"' in repaired
    assert 'alt="微信图标"' in repaired
    assert 'src="/assets/app-icons/alipay.png"' in repaired
    assert 'alt="支付宝图标"' in repaired
    assert repair_builtin_app_icon_bindings(repaired) == repaired


def test_unrelated_content_image_is_not_rewritten() -> None:
    html = """<article>
      <img data-node-id="news.hero" src="/gallery/people/person.jpg" alt="人物">
      <p>微信发布了一项更新</p>
      <img data-node-id="privacy.location.map" src="/gallery/travel/map.jpg" alt="地图预览">
    </article>"""

    assert repair_builtin_app_icon_bindings(html) == html


def test_vertical_app_icon_tiles_are_repaired_to_four_column_grid() -> None:
    items = "".join(
        f'''<div data-node-id="apps.{slug}" data-component="list-item"
                   class="flex flex-col items-center gap-ui-compact">
              <img data-component="image" src="/assets/app-icons/{slug}.png"
                   alt="{name}">
              <span data-component="text">{name}</span>
            </div>'''
        for slug, name in (
            ("wechat", "微信"),
            ("alipay", "支付宝"),
            ("douyin", "抖音"),
            ("taobao", "淘宝"),
        )
    )
    html = (
        '<div data-node-id="common-apps.list" data-component="list" '
        'class="flex flex-col gap-ui-item">'
        f"{items}</div>"
    )

    repaired = repair_builtin_app_icon_layout(html)

    assert 'data-component="grid"' in repaired
    assert 'class="grid grid-cols-4 gap-ui-item"' in repaired
    assert repaired.count('data-component="grid-item"') == 4
    assert 'data-component="list-item"' not in repaired
    assert repair_builtin_app_icon_layout(repaired) == repaired


def test_horizontal_app_setting_rows_remain_a_list() -> None:
    items = "".join(
        f'''<div data-component="list-item" class="flex flex-row items-center">
              <img src="/assets/app-icons/{slug}.png" alt="{name}">
              <span data-component="text">{name}权限</span>
            </div>'''
        for slug, name in (
            ("wechat", "微信"),
            ("alipay", "支付宝"),
            ("douyin", "抖音"),
        )
    )
    html = f'<div data-component="list" class="flex flex-col">{items}</div>'

    assert repair_builtin_app_icon_layout(html) == html


def test_app_icons_are_served_with_capture_cors() -> None:
    with TestClient(app_mod.app) as client:
        response = client.get("/assets/app-icons/wechat.png")

    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"
    assert response.headers["access-control-allow-origin"] == "*"
    assert response.content.startswith(b"\x89PNG")
