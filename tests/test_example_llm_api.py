"""Tests for the example_llm app API (LLM client mocked)."""

import importlib.util
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

EXAMPLE_LLM_DIR = Path(__file__).resolve().parent.parent / "example_llm"


@pytest.fixture
def example_llm_client(monkeypatch):
    """Load example_llm app with mocked LLMClient."""
    monkeypatch.setenv("FLASK_BASE_KEY_PREFIX", "LLM_EXAMPLE_KEY_")
    monkeypatch.setenv("LLM_EXAMPLE_KEY_ALICE", "alice-test-key:view")

    mock_llm = MagicMock()

    from flask_base import FlaskApp

    patch_target = f"{FlaskApp.__module__.rsplit('.', 1)[0]}.llm_setup.get_llm"

    # Isolate example_llm's services package from example/services
    saved_services = {
        k: sys.modules.pop(k)
        for k in list(sys.modules)
        if k == "services" or k.startswith("services.")
    }
    sys.path.insert(0, str(EXAMPLE_LLM_DIR))
    try:
        spec = importlib.util.spec_from_file_location(
            "example_llm_app", EXAMPLE_LLM_DIR / "app.py"
        )
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        with patch(patch_target, return_value=mock_llm):
            spec.loader.exec_module(module)
            module.app.config["TESTING"] = True
            client = module.app.test_client()
            yield client, mock_llm, module
    finally:
        if str(EXAMPLE_LLM_DIR) in sys.path:
            sys.path.remove(str(EXAMPLE_LLM_DIR))
        for k in list(sys.modules):
            if k == "services" or k.startswith("services."):
                sys.modules.pop(k, None)
        sys.modules.update(saved_services)


def test_ask_requires_auth(example_llm_client):
    client, _, _ = example_llm_client
    response = client.post("/api/ask", json={"prompt": "hi"})
    assert response.status_code == 404


def test_ask_generates_text(example_llm_client):
    client, mock_llm, _ = example_llm_client
    mock_llm.generate_text.return_value = "Hello from Gemini!"

    response = client.post(
        "/api/ask?key=alice-test-key",
        json={"prompt": "Say hello", "system_instruction": "Be brief."},
    )
    assert response.status_code == 200
    assert response.get_json() == {"text": "Hello from Gemini!"}
    mock_llm.generate_text.assert_called_once()


def test_summarize_generates_structured_json(example_llm_client):
    client, mock_llm, _ = example_llm_client
    from services.llm_service import TextSummary

    mock_llm.generate_json.return_value = TextSummary(
        headline="FlaskBase v0.4.0 Ships",
        sentiment="positive",
        tags=["flask", "llm"],
        summary="Optional Google Gen AI support is now built into flask-base.",
    )

    response = client.post(
        "/api/summarize?key=alice-test-key",
        json={"text": "We shipped flask-base v0.4.0 with LLM support!"},
    )
    assert response.status_code == 200
    data = response.get_json()["result"]
    assert data["headline"] == "FlaskBase v0.4.0 Ships"
    assert data["sentiment"] == "positive"
    assert data["tags"] == ["flask", "llm"]
    mock_llm.generate_json.assert_called_once()


def test_ask_rejects_empty_prompt(example_llm_client):
    client, mock_llm, _ = example_llm_client
    response = client.post("/api/ask?key=alice-test-key", json={"prompt": "   "})
    assert response.status_code == 400
    mock_llm.generate_text.assert_not_called()
