"""LLM provider for JIM-mini's own (standalone) guidance.

Mirrors QRME's provider pattern but is independent — JIM ships its own so the
two projects share no code. Without Anthropic credentials (or with
``JIM_LLM=stub``) a deterministic stub keeps standalone guidance working
offline.
"""

from __future__ import annotations

import os
from typing import Protocol

MODEL = os.environ.get("JIM_MODEL", "claude-opus-4-8")


class Provider(Protocol):
    def generate(self, system: str, user: str) -> str: ...


class AnthropicProvider:
    def __init__(self) -> None:
        import anthropic

        self._client = anthropic.Anthropic()

    def generate(self, system: str, user: str) -> str:
        response = self._client.messages.create(
            model=MODEL,
            max_tokens=1024,
            thinking={"type": "adaptive"},
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        return "".join(b.text for b in response.content if b.type == "text").strip()


class StubProvider:
    def generate(self, system: str, user: str) -> str:
        label = _extract(system, "condition: ") or "distress"
        return (
            f"I'm here with you. [stub guidance for {label}] "
            "Let's take one slow breath together, and tell me what feels most urgent."
        )


def _extract(text: str, marker: str) -> str | None:
    for line in text.splitlines():
        if marker in line:
            return line.split(marker, 1)[1].strip().rstrip(".")
    return None


def get_provider() -> Provider:
    choice = os.environ.get("JIM_LLM")
    if choice == "stub":
        return StubProvider()
    if choice == "anthropic" or os.environ.get("ANTHROPIC_API_KEY") or os.environ.get(
        "ANTHROPIC_AUTH_TOKEN"
    ):
        return AnthropicProvider()
    return StubProvider()
