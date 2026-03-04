"""Tests for core.llm_client — LLMConfig, LLMClient, resolve_llm_config."""

from __future__ import annotations

import os
from unittest.mock import MagicMock, patch

from core.llm_client import LLMClient, LLMConfig, resolve_llm_config

# ---------------------------------------------------------------------------
# LLMConfig
# ---------------------------------------------------------------------------


class TestLLMConfigIsConfigured:
    def test_configured_when_provider_and_model_set(self):
        config = LLMConfig(provider="openai", model="gpt-4o-mini")
        assert config.is_configured is True

    def test_not_configured_when_empty(self):
        config = LLMConfig()
        assert config.is_configured is False

    def test_not_configured_when_only_provider(self):
        config = LLMConfig(provider="openai")
        assert config.is_configured is False

    def test_not_configured_when_only_model(self):
        config = LLMConfig(model="gpt-4o-mini")
        assert config.is_configured is False


class TestLLMConfigApiKey:
    def test_api_key_from_env(self, monkeypatch):
        monkeypatch.setenv("TEST_API_KEY", "sk-test-123")
        config = LLMConfig(api_key_env="TEST_API_KEY")
        assert config.api_key == "sk-test-123"

    def test_api_key_none_when_env_missing(self):
        config = LLMConfig(api_key_env="NONEXISTENT_KEY_12345")
        # Ensure it's not set
        os.environ.pop("NONEXISTENT_KEY_12345", None)
        assert config.api_key is None

    def test_api_key_none_when_no_env_name(self):
        config = LLMConfig()
        assert config.api_key is None


# ---------------------------------------------------------------------------
# resolve_llm_config
# ---------------------------------------------------------------------------


class _FakeSettings:
    """Mimics the relevant fields of config.Settings."""

    def __init__(self, **kwargs):
        self.llm_provider = kwargs.get("llm_provider", "")
        self.llm_model = kwargs.get("llm_model", "")
        self.llm_endpoint = kwargs.get("llm_endpoint", None)
        self.llm_api_key_env = kwargs.get("llm_api_key_env", "")
        self.llm_temperature = kwargs.get("llm_temperature", 0.7)
        self.llm_max_tokens = kwargs.get("llm_max_tokens", 2048)


class TestResolveLLMConfig:
    def test_global_only(self):
        settings = _FakeSettings(llm_provider="openai", llm_model="gpt-4o")
        config = resolve_llm_config(settings)
        assert config.provider == "openai"
        assert config.model == "gpt-4o"
        assert config.temperature == 0.7

    def test_project_overrides_provider_and_model(self):
        settings = _FakeSettings(llm_provider="openai", llm_model="gpt-4o")
        project = {"provider": "anthropic", "model": "claude-sonnet-4-20250514"}
        config = resolve_llm_config(settings, project)
        assert config.provider == "anthropic"
        assert config.model == "claude-sonnet-4-20250514"
        # temperature untouched
        assert config.temperature == 0.7

    def test_project_overrides_temperature(self):
        settings = _FakeSettings(llm_provider="openai", llm_model="gpt-4o")
        project = {"temperature": 0.2}
        config = resolve_llm_config(settings, project)
        assert config.provider == "openai"
        assert config.temperature == 0.2

    def test_project_none_values_ignored(self):
        settings = _FakeSettings(llm_provider="openai", llm_model="gpt-4o")
        project = {"provider": None, "model": None}
        config = resolve_llm_config(settings, project)
        assert config.provider == "openai"
        assert config.model == "gpt-4o"

    def test_no_project_config(self):
        settings = _FakeSettings(llm_provider="ollama", llm_model="llama3")
        config = resolve_llm_config(settings, None)
        assert config.provider == "ollama"
        assert config.model == "llama3"

    def test_endpoint_override(self):
        settings = _FakeSettings(llm_endpoint="http://localhost:11434")
        project = {"endpoint": "http://remote:8080"}
        config = resolve_llm_config(settings, project)
        assert config.endpoint == "http://remote:8080"


# ---------------------------------------------------------------------------
# LLMClient
# ---------------------------------------------------------------------------


def _make_litellm_response(
    content="Hello", model="gpt-4o-mini", prompt_tokens=10, completion_tokens=5
):
    """Create a mock litellm response object."""
    response = MagicMock()
    response.choices = [MagicMock()]
    response.choices[0].message.content = content
    response.model = model
    response.usage = MagicMock()
    response.usage.prompt_tokens = prompt_tokens
    response.usage.completion_tokens = completion_tokens
    response.usage.total_tokens = prompt_tokens + completion_tokens
    return response


class TestLLMClientComplete:
    @patch("litellm.completion")
    def test_basic_completion(self, mock_completion):
        mock_completion.return_value = _make_litellm_response(content="Generated text")
        config = LLMConfig(provider="openai", model="gpt-4o-mini")
        client = LLMClient(config)

        result = client.complete("Write something")

        assert result.content == "Generated text"
        assert result.model == "gpt-4o-mini"
        assert result.prompt_tokens == 10
        assert result.completion_tokens == 5
        assert result.total_tokens == 15
        mock_completion.assert_called_once()

    @patch("litellm.completion")
    def test_completion_with_system_prompt(self, mock_completion):
        mock_completion.return_value = _make_litellm_response()
        config = LLMConfig(provider="openai", model="gpt-4o-mini")
        client = LLMClient(config)

        client.complete("Write something", system="You are helpful")

        call_kwargs = mock_completion.call_args[1]
        messages = call_kwargs["messages"]
        assert len(messages) == 2
        assert messages[0]["role"] == "system"
        assert messages[0]["content"] == "You are helpful"
        assert messages[1]["role"] == "user"

    @patch("litellm.completion")
    def test_completion_passes_api_key(self, mock_completion, monkeypatch):
        monkeypatch.setenv("MY_KEY", "sk-secret")
        mock_completion.return_value = _make_litellm_response()
        config = LLMConfig(provider="openai", model="gpt-4o-mini", api_key_env="MY_KEY")
        client = LLMClient(config)

        client.complete("test")

        call_kwargs = mock_completion.call_args[1]
        assert call_kwargs["api_key"] == "sk-secret"

    @patch("litellm.completion")
    def test_completion_passes_endpoint(self, mock_completion):
        mock_completion.return_value = _make_litellm_response()
        config = LLMConfig(provider="ollama", model="llama3", endpoint="http://localhost:11434")
        client = LLMClient(config)

        client.complete("test")

        call_kwargs = mock_completion.call_args[1]
        assert call_kwargs["api_base"] == "http://localhost:11434"

    @patch("litellm.completion")
    def test_completion_passes_temperature_and_max_tokens(self, mock_completion):
        mock_completion.return_value = _make_litellm_response()
        config = LLMConfig(provider="openai", model="gpt-4o-mini", temperature=0.3, max_tokens=500)
        client = LLMClient(config)

        client.complete("test")

        call_kwargs = mock_completion.call_args[1]
        assert call_kwargs["temperature"] == 0.3
        assert call_kwargs["max_tokens"] == 500


class TestLLMClientTestConnection:
    @patch("litellm.completion")
    def test_success(self, mock_completion):
        mock_completion.return_value = _make_litellm_response(model="gpt-4o-mini")
        config = LLMConfig(provider="openai", model="gpt-4o-mini")
        client = LLMClient(config)

        success, message = client.test_connection()

        assert success is True
        assert "gpt-4o-mini" in message

    @patch("litellm.completion")
    def test_failure(self, mock_completion):
        mock_completion.side_effect = Exception("Connection refused")
        config = LLMConfig(provider="openai", model="gpt-4o-mini")
        client = LLMClient(config)

        success, message = client.test_connection()

        assert success is False
        assert "Connection refused" in message
