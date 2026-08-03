"""Tests for the pydantic schemas."""
import pytest
from pydantic import ValidationError

from uibench.schemas import GenerateRequest, GenerationResult, ModelConfig


def test_model_config_defaults():
    m = ModelConfig(id="gpt-4o-mini", provider="openai")
    assert m.enabled is True
    assert m.name == ""


def test_generation_result_ok():
    r = GenerationResult(model_id="x", name="X", provider="openai",
                         html="<html></html>", elapsed_seconds=1.23)
    assert r.error is None
    assert r.elapsed_seconds == 1.23


def test_generate_request_requires_prompt():
    with pytest.raises(ValidationError):
        GenerateRequest(prompt="")
