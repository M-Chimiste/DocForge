"""Tests for project CRUD API endpoints."""

import pytest


@pytest.mark.asyncio
async def test_create_project(api_client):
    resp = await api_client.post(
        "/api/v1/projects", json={"name": "Test Project", "description": "A test"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "Test Project"
    assert data["description"] == "A test"
    assert "id" in data


@pytest.mark.asyncio
async def test_list_projects(api_client):
    await api_client.post("/api/v1/projects", json={"name": "Project A"})
    await api_client.post("/api/v1/projects", json={"name": "Project B"})
    resp = await api_client.get("/api/v1/projects")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2


@pytest.mark.asyncio
async def test_get_project(api_client):
    create_resp = await api_client.post("/api/v1/projects", json={"name": "Single"})
    project_id = create_resp.json()["id"]
    resp = await api_client.get(f"/api/v1/projects/{project_id}")
    assert resp.status_code == 200
    assert resp.json()["name"] == "Single"


@pytest.mark.asyncio
async def test_get_project_not_found(api_client):
    resp = await api_client.get("/api/v1/projects/9999")
    assert resp.status_code == 404
    assert resp.json()["error"] == "not_found"
