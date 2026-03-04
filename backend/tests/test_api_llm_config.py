"""Tests for LLM configuration API endpoints."""

from unittest.mock import patch

import pytest


@pytest.mark.asyncio
async def test_get_global_llm_config_unconfigured(api_client):
    resp = await api_client.get("/api/v1/llm/config")
    assert resp.status_code == 200
    data = resp.json()
    assert data["provider"] == ""
    assert data["model"] == ""
    assert data["apiKeyConfigured"] is False
    assert data["temperature"] == 0.7
    assert data["maxTokens"] == 2048


@pytest.mark.asyncio
async def test_get_global_llm_config_configured(api_client, monkeypatch):
    monkeypatch.setenv("MY_KEY", "sk-test")
    settings = api_client._transport.app.state.settings
    settings.llm_provider = "openai"
    settings.llm_model = "gpt-4o-mini"
    settings.llm_api_key_env = "MY_KEY"

    resp = await api_client.get("/api/v1/llm/config")
    assert resp.status_code == 200
    data = resp.json()
    assert data["provider"] == "openai"
    assert data["model"] == "gpt-4o-mini"
    assert data["apiKeyConfigured"] is True


@pytest.mark.asyncio
async def test_test_global_llm_unconfigured(api_client):
    resp = await api_client.post("/api/v1/llm/test")
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is False
    assert "not configured" in data["message"].lower()


@pytest.mark.asyncio
@patch("core.llm_client.LLMClient.test_connection", return_value=(True, "Connected to gpt-4o-mini"))
async def test_test_global_llm_success(mock_test, api_client):
    settings = api_client._transport.app.state.settings
    settings.llm_provider = "openai"
    settings.llm_model = "gpt-4o-mini"

    resp = await api_client.post("/api/v1/llm/test")
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert "gpt-4o-mini" in data["message"]


@pytest.mark.asyncio
@patch("core.llm_client.LLMClient.test_connection", return_value=(False, "Auth failed"))
async def test_test_global_llm_failure(mock_test, api_client):
    settings = api_client._transport.app.state.settings
    settings.llm_provider = "openai"
    settings.llm_model = "gpt-4o-mini"

    resp = await api_client.post("/api/v1/llm/test")
    data = resp.json()
    assert data["success"] is False
    assert "Auth failed" in data["message"]


# --- Per-project LLM config ---


@pytest.fixture
async def project_id(api_client):
    resp = await api_client.post("/api/v1/projects", json={"name": "LLM Test"})
    return resp.json()["id"]


@pytest.mark.asyncio
async def test_get_project_llm_config_defaults(api_client, project_id):
    resp = await api_client.get(f"/api/v1/projects/{project_id}/llm-config")
    assert resp.status_code == 200
    data = resp.json()
    # Should return global defaults (empty)
    assert data["provider"] == ""
    assert data["model"] == ""


@pytest.mark.asyncio
async def test_get_project_llm_config_not_found(api_client):
    resp = await api_client.get("/api/v1/projects/9999/llm-config")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_update_project_llm_config(api_client, project_id):
    resp = await api_client.put(
        f"/api/v1/projects/{project_id}/llm-config",
        json={"provider": "anthropic", "model": "claude-sonnet-4-20250514", "temperature": 0.3},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["provider"] == "anthropic"
    assert data["model"] == "claude-sonnet-4-20250514"
    assert data["temperature"] == 0.3


@pytest.mark.asyncio
async def test_update_project_llm_config_partial(api_client, project_id):
    # First set full config
    await api_client.put(
        f"/api/v1/projects/{project_id}/llm-config",
        json={"provider": "openai", "model": "gpt-4o", "temperature": 0.5},
    )

    # Then update only temperature
    resp = await api_client.put(
        f"/api/v1/projects/{project_id}/llm-config",
        json={"temperature": 0.9},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["provider"] == "openai"
    assert data["model"] == "gpt-4o"
    assert data["temperature"] == 0.9


@pytest.mark.asyncio
async def test_project_overrides_global(api_client, project_id):
    settings = api_client._transport.app.state.settings
    settings.llm_provider = "openai"
    settings.llm_model = "gpt-4o"

    await api_client.put(
        f"/api/v1/projects/{project_id}/llm-config",
        json={"model": "gpt-4o-mini"},
    )

    resp = await api_client.get(f"/api/v1/projects/{project_id}/llm-config")
    data = resp.json()
    assert data["provider"] == "openai"  # from global
    assert data["model"] == "gpt-4o-mini"  # from project override


@pytest.mark.asyncio
async def test_update_project_llm_config_not_found(api_client):
    resp = await api_client.put(
        "/api/v1/projects/9999/llm-config",
        json={"provider": "openai"},
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_test_project_llm_not_found(api_client):
    resp = await api_client.post("/api/v1/projects/9999/llm-test")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_test_project_llm_unconfigured(api_client, project_id):
    resp = await api_client.post(f"/api/v1/projects/{project_id}/llm-test")
    data = resp.json()
    assert data["success"] is False


@pytest.mark.asyncio
@patch("core.llm_client.LLMClient.test_connection", return_value=(True, "Connected"))
async def test_test_project_llm_with_config(mock_test, api_client, project_id):
    await api_client.put(
        f"/api/v1/projects/{project_id}/llm-config",
        json={"provider": "openai", "model": "gpt-4o-mini"},
    )
    resp = await api_client.post(f"/api/v1/projects/{project_id}/llm-test")
    data = resp.json()
    assert data["success"] is True
