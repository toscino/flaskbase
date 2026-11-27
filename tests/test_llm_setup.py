"""Unit tests for optional Google Gen AI LLM integration (app_manager.llm)."""

from __future__ import annotations

import importlib
import logging
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from pydantic import BaseModel, ValidationError

from flask_base import FlaskApp

_flask_base_pkg = FlaskApp.__module__.rsplit(".", 1)[0]
llm_setup = importlib.import_module(f"{_flask_base_pkg}.llm_setup")


class SampleOutput(BaseModel):
    summary: str
    score: int


def _make_fake_genai():
    """Return a mock (genai, genai_types, mock_client) tuple."""
    mock_client = MagicMock()
    mock_genai = MagicMock()
    mock_genai.Client.return_value = mock_client

    mock_types = MagicMock()
    mock_types.GenerateContentConfig.side_effect = lambda **kwargs: SimpleNamespace(
        **kwargs
    )
    return mock_genai, mock_types, mock_client


def _make_response(
    text: str | None,
    prompt_tokens: int = 12,
    output_tokens: int = 8,
    total_tokens: int = 20,
):
    return SimpleNamespace(
        text=text,
        usage_metadata=SimpleNamespace(
            prompt_token_count=prompt_tokens,
            candidates_token_count=output_tokens,
            total_token_count=total_tokens,
        ),
    )


def test_llm_is_lazy_initialized():
    """Creating FlaskApp must not initialize genai.Client until .llm is accessed."""
    mock_genai, mock_types, mock_client = _make_fake_genai()

    with (
        patch.object(llm_setup, "genai", mock_genai),
        patch.object(llm_setup, "genai_types", mock_types),
    ):
        manager = FlaskApp("Lazy Test")
        mock_genai.Client.assert_not_called()

        first = manager.llm
        second = manager.llm

        assert first is second
        assert first.client is mock_client
        mock_genai.Client.assert_called_once_with(
            enterprise=True,
            project="test-project",
            location="global",
        )
        assert first.default_model == "gemini-3.1-flash-lite"


def test_llm_missing_dependency_raises_clear_import_error():
    """Accessing app_manager.llm without google-genai raises a clear ImportError."""
    with (
        patch.object(llm_setup, "genai", None),
        patch.object(llm_setup, "genai_types", None),
    ):
        manager = FlaskApp("Missing Dep Test")
        with pytest.raises(ImportError, match=r"flask-base\[llm\]"):
            _ = manager.llm


def test_llm_env_overrides(monkeypatch):
    """LLM_LOCATION, LLM_MODEL, and GOOGLE_CLOUD_PROJECT override defaults."""
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "custom-proj")
    monkeypatch.setenv("LLM_LOCATION", "us-central1")
    monkeypatch.setenv("LLM_MODEL", "gemini-2.5-pro")

    mock_genai, mock_types, _ = _make_fake_genai()
    with (
        patch.object(llm_setup, "genai", mock_genai),
        patch.object(llm_setup, "genai_types", mock_types),
    ):
        manager = FlaskApp("Env Override Test")
        llm = manager.llm

        mock_genai.Client.assert_called_once_with(
            enterprise=True,
            project="custom-proj",
            location="us-central1",
        )
        assert llm.location == "us-central1"
        assert llm.default_model == "gemini-2.5-pro"


def test_generate_text_success_and_logging(caplog):
    """generate_text forwards config, returns text, and logs model/latency/tokens."""
    mock_genai, mock_types, mock_client = _make_fake_genai()
    mock_client.models.generate_content.return_value = _make_response(
        "Hello world", prompt_tokens=15, output_tokens=5, total_tokens=20
    )

    with (
        patch.object(llm_setup, "genai", mock_genai),
        patch.object(llm_setup, "genai_types", mock_types),
    ):
        manager = FlaskApp("Text Test")
        with caplog.at_level(logging.INFO, logger=manager.logger.name):
            result = manager.llm.generate_text(
                "Say hello",
                system_instruction="Be brief.",
                model="gemini-custom",
                temperature=0.3,
                max_output_tokens=256,
                top_p=0.9,
            )

        assert result == "Hello world"
        mock_client.models.generate_content.assert_called_once()
        call_kwargs = mock_client.models.generate_content.call_args.kwargs
        assert call_kwargs["model"] == "gemini-custom"
        assert call_kwargs["contents"] == "Say hello"
        assert call_kwargs["config"].system_instruction == "Be brief."
        assert call_kwargs["config"].temperature == 0.3
        assert call_kwargs["config"].max_output_tokens == 256
        assert call_kwargs["config"].top_p == 0.9

        log_text = "\n".join(caplog.messages)
        assert "gemini-custom" in log_text
        assert "latency_ms=" in log_text
        assert "prompt_tokens=15" in log_text
        assert "output_tokens=5" in log_text
        assert "total_tokens=20" in log_text


def test_generate_text_uses_default_max_output_tokens():
    """generate_text applies default max_output_tokens when omitted."""
    mock_genai, mock_types, mock_client = _make_fake_genai()
    mock_client.models.generate_content.return_value = _make_response("ok")

    with (
        patch.object(llm_setup, "genai", mock_genai),
        patch.object(llm_setup, "genai_types", mock_types),
    ):
        manager = FlaskApp("Default Tokens Test")
        assert manager.llm.generate_text("ping") == "ok"
        call_kwargs = mock_client.models.generate_content.call_args.kwargs
        assert call_kwargs["model"] == "gemini-3.1-flash-lite"
        assert call_kwargs["config"].max_output_tokens == llm_setup.DEFAULT_MAX_OUTPUT_TOKENS


def test_generate_json_returns_validated_pydantic_model(caplog):
    """generate_json returns a validated Pydantic instance of schema."""
    mock_genai, mock_types, mock_client = _make_fake_genai()
    mock_client.models.generate_content.return_value = _make_response(
        '{"summary": "Great progress", "score": 9}',
        prompt_tokens=30,
        output_tokens=10,
        total_tokens=40,
    )

    with (
        patch.object(llm_setup, "genai", mock_genai),
        patch.object(llm_setup, "genai_types", mock_types),
    ):
        manager = FlaskApp("JSON Test")
        with caplog.at_level(logging.INFO, logger=manager.logger.name):
            result = manager.llm.generate_json(
                "Evaluate progress",
                SampleOutput,
                system_instruction="Return JSON",
                temperature=0.1,
            )

        assert isinstance(result, SampleOutput)
        assert result.summary == "Great progress"
        assert result.score == 9

        call_kwargs = mock_client.models.generate_content.call_args.kwargs
        assert call_kwargs["config"].response_mime_type == "application/json"
        assert call_kwargs["config"].response_schema is SampleOutput
        assert call_kwargs["config"].system_instruction == "Return JSON"
        assert call_kwargs["config"].temperature == 0.1

        log_text = "\n".join(caplog.messages)
        assert "generate_json completed" in log_text
        assert "total_tokens=40" in log_text


def test_generate_json_invalid_payload_fails_fast(caplog):
    """Invalid JSON or schema mismatch logs and re-raises immediately with no retries."""
    mock_genai, mock_types, mock_client = _make_fake_genai()
    mock_client.models.generate_content.return_value = _make_response(
        '{"summary": "missing score"}'
    )

    with (
        patch.object(llm_setup, "genai", mock_genai),
        patch.object(llm_setup, "genai_types", mock_types),
    ):
        manager = FlaskApp("Invalid JSON Test")
        with caplog.at_level(logging.ERROR, logger=manager.logger.name):
            with pytest.raises(ValidationError):
                manager.llm.generate_json("Evaluate", SampleOutput)

        assert mock_client.models.generate_content.call_count == 1
        assert any("LLM generate_json failed" in m for m in caplog.messages)


def test_generate_json_empty_response_fails_fast():
    """Empty response text raises ValueError without retrying."""
    mock_genai, mock_types, mock_client = _make_fake_genai()
    mock_client.models.generate_content.return_value = _make_response("")

    with (
        patch.object(llm_setup, "genai", mock_genai),
        patch.object(llm_setup, "genai_types", mock_types),
    ):
        manager = FlaskApp("Empty JSON Test")
        with pytest.raises(ValueError, match="empty response"):
            manager.llm.generate_json("Evaluate", SampleOutput)

        assert mock_client.models.generate_content.call_count == 1


def test_generate_json_rejects_non_pydantic_schema():
    """Passing a non-Pydantic schema raises TypeError before calling the API."""
    mock_genai, mock_types, mock_client = _make_fake_genai()

    with (
        patch.object(llm_setup, "genai", mock_genai),
        patch.object(llm_setup, "genai_types", mock_types),
    ):
        manager = FlaskApp("Bad Schema Test")
        with pytest.raises(TypeError, match="Pydantic"):
            manager.llm.generate_json("Evaluate", dict)  # type: ignore[arg-type]

        mock_client.models.generate_content.assert_not_called()


def test_generate_text_api_error_fails_fast_and_logs(caplog):
    """SDK errors are logged and re-raised immediately with no hidden retries."""
    mock_genai, mock_types, mock_client = _make_fake_genai()
    mock_client.models.generate_content.side_effect = RuntimeError("quota exceeded")

    with (
        patch.object(llm_setup, "genai", mock_genai),
        patch.object(llm_setup, "genai_types", mock_types),
    ):
        manager = FlaskApp("Error Test")
        with caplog.at_level(logging.ERROR, logger=manager.logger.name):
            with pytest.raises(RuntimeError, match="quota exceeded"):
                manager.llm.generate_text("Hello")

        assert mock_client.models.generate_content.call_count == 1
        assert any("LLM generate_text failed" in m for m in caplog.messages)
