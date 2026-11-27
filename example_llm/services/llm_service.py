"""Minimal LLM service demonstrating app_manager.llm.generate_text and generate_json."""

from typing import Any, Literal, Optional

from pydantic import BaseModel, Field


class TextSummary(BaseModel):
    """Structured summary returned by generate_json."""

    headline: str = Field(description="Short headline summarizing the text")
    sentiment: Literal["positive", "neutral", "negative"] = Field(
        description="Overall sentiment of the text"
    )
    tags: list[str] = Field(description="Up to 5 concise lowercase topic tags")
    summary: str = Field(description="One- to two-sentence summary")


class LLMService:
    """Wraps app_manager.llm for text generation and structured JSON extraction."""

    def __init__(self, app_manager: Any) -> None:
        self._app_manager = app_manager
        self.logger = app_manager.logger

    @property
    def llm(self) -> Any:
        return self._app_manager.llm

    def ask(
        self,
        prompt: str,
        *,
        system_instruction: Optional[str] = None,
    ) -> str:
        """Generate a plain-text response."""
        return self.llm.generate_text(
            prompt,
            system_instruction=system_instruction or "Be helpful and concise.",
            temperature=0.4,
        )

    def summarize(self, text: str) -> TextSummary:
        """Extract a validated TextSummary from arbitrary text."""
        return self.llm.generate_json(
            f"Analyze and summarize the following text:\n\n{text}",
            TextSummary,
            system_instruction="Return a concise, accurate JSON summary matching the schema.",
            temperature=0.2,
        )
