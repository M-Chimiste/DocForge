"""LLM client wrapper using LiteLLM for provider-agnostic LLM calls."""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class LLMConfig:
    """LLM provider configuration."""

    provider: str = ""
    model: str = ""
    endpoint: str | None = None
    api_key_env: str = ""
    temperature: float = 0.7
    max_tokens: int = 2048

    @property
    def api_key(self) -> str | None:
        if self.api_key_env:
            return os.environ.get(self.api_key_env)
        return None

    @property
    def is_configured(self) -> bool:
        return bool(self.provider and self.model)


@dataclass
class LLMResponse:
    """Response from an LLM call."""

    content: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class LLMClient:
    """Synchronous LLM client wrapping litellm.completion()."""

    def __init__(self, config: LLMConfig):
        self._config = config

    def complete(self, prompt: str, system: str | None = None) -> LLMResponse:
        """Make a synchronous LLM completion call."""
        import litellm

        messages: list[dict[str, str]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        kwargs: dict[str, Any] = {
            "model": self._config.model,
            "messages": messages,
            "temperature": self._config.temperature,
            "max_tokens": self._config.max_tokens,
        }
        if self._config.api_key:
            kwargs["api_key"] = self._config.api_key
        if self._config.endpoint:
            kwargs["api_base"] = self._config.endpoint

        response = litellm.completion(**kwargs)
        usage = response.usage
        return LLMResponse(
            content=response.choices[0].message.content,
            model=response.model or self._config.model,
            prompt_tokens=usage.prompt_tokens if usage else 0,
            completion_tokens=usage.completion_tokens if usage else 0,
            total_tokens=usage.total_tokens if usage else 0,
        )

    def test_connection(self) -> tuple[bool, str]:
        """Test that the LLM provider is reachable."""
        try:
            resp = self.complete("Say 'hello' in one word.")
            return True, f"Connected to {resp.model}"
        except Exception as e:
            return False, str(e)


def resolve_llm_config(
    settings: Any, project_llm_config: dict[str, Any] | None = None
) -> LLMConfig:
    """Merge global Settings defaults with per-project overrides."""
    config = LLMConfig(
        provider=settings.llm_provider,
        model=settings.llm_model,
        endpoint=settings.llm_endpoint,
        api_key_env=settings.llm_api_key_env,
        temperature=settings.llm_temperature,
        max_tokens=settings.llm_max_tokens,
    )
    if project_llm_config:
        for key in ("provider", "model", "endpoint", "api_key_env", "temperature", "max_tokens"):
            val = project_llm_config.get(key)
            if val is not None:
                setattr(config, key, val)
    return config
