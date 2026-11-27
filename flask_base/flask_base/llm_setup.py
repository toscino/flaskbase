"""Optional Google Gen AI (Vertex AI Enterprise) client wrapper."""

from __future__ import annotations

import logging
import os
import time
from typing import TYPE_CHECKING, Any, Optional, TypeVar

if TYPE_CHECKING:
    from pydantic import BaseModel

T = TypeVar("T", bound="BaseModel")

DEFAULT_LLM_LOCATION = "global"
DEFAULT_LLM_MODEL = "gemini-3.1-flash-lite"
DEFAULT_MAX_OUTPUT_TOKENS = 2048

try:
    from google import genai
    from google.genai import types as genai_types
except ImportError:
    genai = None  # type: ignore[assignment]
    genai_types = None  # type: ignore[assignment]


class LLMClient:
    """Thin wrapper around the Google Gen AI SDK (Vertex AI Enterprise).

    Provides two ergonomic helpers (``generate_text`` and ``generate_json``)
    plus direct access to the underlying ``genai.Client`` via ``.client``.
    Fails fast on errors without hidden retry loops and logs model name,
    latency, and token usage on every call.
    """

    def __init__(
        self,
        project_id: Optional[str] = None,
        location: Optional[str] = None,
        default_model: Optional[str] = None,
        logger: Optional[logging.Logger] = None,
        default_max_output_tokens: int = DEFAULT_MAX_OUTPUT_TOKENS,
    ) -> None:
        if genai is None or genai_types is None:
            raise ImportError(
                "google-genai is not installed. "
                "Install optional LLM support with: pip install 'flask-base[llm]' "
                "(or pip install google-genai pydantic)"
            )

        self.project_id = project_id or os.environ.get("GOOGLE_CLOUD_PROJECT")
        self.location = location or os.environ.get("LLM_LOCATION") or DEFAULT_LLM_LOCATION
        self.default_model = (
            default_model or os.environ.get("LLM_MODEL") or DEFAULT_LLM_MODEL
        )
        self.default_max_output_tokens = default_max_output_tokens
        self.logger = logger or logging.getLogger(__name__)

        self.logger.info(
            "Initializing LLMClient (project=%s, location=%s, default_model=%s)",
            self.project_id,
            self.location,
            self.default_model,
        )
        self._client = genai.Client(
            enterprise=True,
            project=self.project_id,
            location=self.location,
        )

    @property
    def client(self) -> Any:
        """Direct access to the underlying ``google.genai.Client``."""
        return self._client

    def _build_config(
        self,
        *,
        system_instruction: Optional[str] = None,
        temperature: Optional[float] = None,
        max_output_tokens: Optional[int] = None,
        response_mime_type: Optional[str] = None,
        response_schema: Any = None,
        **config_kwargs: Any,
    ) -> Any:
        params: dict[str, Any] = dict(config_kwargs)
        params["max_output_tokens"] = (
            max_output_tokens
            if max_output_tokens is not None
            else self.default_max_output_tokens
        )
        if system_instruction is not None:
            params["system_instruction"] = system_instruction
        if temperature is not None:
            params["temperature"] = temperature
        if response_mime_type is not None:
            params["response_mime_type"] = response_mime_type
        if response_schema is not None:
            params["response_schema"] = response_schema
        return genai_types.GenerateContentConfig(**params)

    def _log_usage(
        self,
        method: str,
        model: str,
        elapsed_ms: float,
        response: Any,
    ) -> None:
        usage = getattr(response, "usage_metadata", None)
        prompt_tokens = getattr(usage, "prompt_token_count", None) if usage else None
        output_tokens = (
            getattr(usage, "candidates_token_count", None) if usage else None
        )
        total_tokens = getattr(usage, "total_token_count", None) if usage else None
        self.logger.info(
            "LLM %s completed (model=%s, latency_ms=%.1f, prompt_tokens=%s, output_tokens=%s, total_tokens=%s)",
            method,
            model,
            elapsed_ms,
            prompt_tokens,
            output_tokens,
            total_tokens,
        )

    def generate_text(
        self,
        prompt: str,
        *,
        system_instruction: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_output_tokens: Optional[int] = None,
        **config_kwargs: Any,
    ) -> str:
        """Generate unstructured text from a prompt.

        Fails fast (no hidden retries) and logs model, latency, and token usage.
        """
        resolved_model = model or self.default_model
        config = self._build_config(
            system_instruction=system_instruction,
            temperature=temperature,
            max_output_tokens=max_output_tokens,
            **config_kwargs,
        )
        start = time.perf_counter()
        try:
            response = self._client.models.generate_content(
                model=resolved_model,
                contents=prompt,
                config=config,
            )
            elapsed_ms = (time.perf_counter() - start) * 1000.0
            self._log_usage("generate_text", resolved_model, elapsed_ms, response)
            return response.text or ""
        except Exception as exc:
            elapsed_ms = (time.perf_counter() - start) * 1000.0
            self.logger.exception(
                "LLM generate_text failed (model=%s, latency_ms=%.1f): %s",
                resolved_model,
                elapsed_ms,
                exc,
            )
            raise

    def generate_json(
        self,
        prompt: str,
        schema: type[T],
        *,
        system_instruction: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_output_tokens: Optional[int] = None,
        **config_kwargs: Any,
    ) -> T:
        """Generate structured JSON validated against a Pydantic ``BaseModel`` schema.

        Returns a validated instance of ``schema``. Call ``.model_dump()`` if a
        plain dict is needed. Fails fast on API, JSON, or validation errors.
        """
        if not hasattr(schema, "model_validate_json"):
            raise TypeError(
                f"schema must be a Pydantic v2 BaseModel subclass, got {schema!r}"
            )

        resolved_model = model or self.default_model
        config = self._build_config(
            system_instruction=system_instruction,
            temperature=temperature,
            max_output_tokens=max_output_tokens,
            response_mime_type="application/json",
            response_schema=schema,
            **config_kwargs,
        )
        start = time.perf_counter()
        try:
            response = self._client.models.generate_content(
                model=resolved_model,
                contents=prompt,
                config=config,
            )
            elapsed_ms = (time.perf_counter() - start) * 1000.0
            self._log_usage("generate_json", resolved_model, elapsed_ms, response)

            raw_text = response.text
            if not raw_text:
                raise ValueError("LLM returned empty response for generate_json")

            return schema.model_validate_json(raw_text)
        except Exception as exc:
            elapsed_ms = (time.perf_counter() - start) * 1000.0
            self.logger.exception(
                "LLM generate_json failed (model=%s, schema=%s, latency_ms=%.1f): %s",
                resolved_model,
                getattr(schema, "__name__", repr(schema)),
                elapsed_ms,
                exc,
            )
            raise


def get_llm(
    project_id: Optional[str] = None,
    location: Optional[str] = None,
    default_model: Optional[str] = None,
    logger: Optional[logging.Logger] = None,
) -> LLMClient:
    """Create an ``LLMClient`` (lazy initialization helper mirroring ``get_db``)."""
    return LLMClient(
        project_id=project_id,
        location=location,
        default_model=default_model,
        logger=logger,
    )
