"""Groq service wrapper for Command Center AI features."""
from __future__ import annotations

import os
from typing import Any
import importlib.util

HAS_GROQ = importlib.util.find_spec("groq") is not None

if HAS_GROQ:
    from groq import Groq
else:
    Groq = None


class GroqService:
    """Thin wrapper around Groq chat completions."""

    def __init__(self, api_key: str | None = None, model: str = "llama-3.1-70b-versatile") -> None:
        self.api_key = api_key or os.environ.get("GROQ_API_KEY", "")
        self.model = model

    def is_available(self) -> bool:
        return bool(HAS_GROQ and self.api_key)

    def _client(self) -> Groq:
        if not HAS_GROQ:
            raise RuntimeError("groq package is not installed")
        if not self.api_key:
            raise RuntimeError("Groq API key is not configured")
        return Groq(api_key=self.api_key)

    def chat(self, prompt: str, system_prompt: str | None = None) -> str:
        client = self._client()
        messages: list[dict[str, Any]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        response = client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.3,
        )
        return response.choices[0].message.content or "No response from Groq."

    def analyze_metrics(self, metrics: dict[str, Any]) -> str:
        prompt = (
            "You are a senior SRE. Analyze these system metrics and provide a concise diagnosis, "
            "probable root cause, and 3 remediation steps.\n\n"
            f"Metrics: {metrics}"
        )
        return self.chat(prompt, system_prompt="Be concise, practical, and operations-focused.")

    def generate_runbook(self, incident_title: str) -> str:
        prompt = (
            f"Generate a short incident runbook for: {incident_title}. "
            "Include detection, immediate mitigation, verification, and escalation guidance."
        )
        return self.chat(prompt, system_prompt="Write in markdown bullet points for an SRE team.")
