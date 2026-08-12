"""Tests for the pydantic schemas."""
import pytest
from pydantic import ValidationError

from uibench.schemas import (
    ArkUiExportRequest,
    GenerateRequest,
    GenerationResult,
    ModelConfig,
)


def test_model_config_defaults():
    m = ModelConfig(id="gpt-4o-mini", provider="openai")
    assert m.enabled is True
    assert m.name == ""


def test_generation_result_ok():
    r = GenerationResult(model_id="x", name="X", provider="openai",
                         html="<html></html>", elapsed_seconds=1.23)
    assert r.error is None
    assert r.elapsed_seconds == 1.23
    assert r.arkui_manifest == {}


def test_generate_request_requires_prompt():
    with pytest.raises(ValidationError):
        GenerateRequest(prompt="")


def test_arkui_generation_is_opt_in():
    request = GenerateRequest(prompt="登录页")
    assert request.arkui_export_enabled is False


def test_arkui_export_request_is_bounded():
    request = ArkUiExportRequest(html="<html></html>")
    assert request.mode == "annotated"
    assert request.viewport_width == 390
    assert request.viewport_height == 844

    with pytest.raises(ValidationError):
        ArkUiExportRequest(html="x" * 2_000_001)
