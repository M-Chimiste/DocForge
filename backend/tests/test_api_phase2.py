"""Tests for Phase 2 API endpoints."""

import pytest

from db.models import Project


@pytest.fixture
async def project_with_template_and_data(api_client, templates_dir, data_dir):
    """Create a project with template and data source uploaded."""
    resp = await api_client.post("/api/v1/projects", json={"name": "Phase2 Test"})
    project = resp.json()
    project_id = project["id"]

    # Upload template via analyze
    with open(templates_dir / "simple_placeholder.docx", "rb") as f:
        await api_client.post(
            "/api/v1/templates/analyze",
            files={"file": ("simple_placeholder.docx", f, "application/octet-stream")},
        )

    # Set template path on project
    session_factory = api_client._transport.app.state.db
    settings = api_client._transport.app.state.settings
    with session_factory() as session:
        p = session.query(Project).filter(Project.id == project_id).first()
        p.template_path = str(settings.upload_dir / "simple_placeholder.docx")
        session.commit()

    # Upload data source
    with open(data_dir / "config.json", "rb") as f:
        await api_client.post(
            f"/api/v1/projects/{project_id}/data-sources",
            files={"file": ("config.json", f, "application/octet-stream")},
        )

    return project


# --- Project Update & Delete ---


@pytest.mark.asyncio
async def test_update_project(api_client):
    resp = await api_client.post("/api/v1/projects", json={"name": "Original"})
    project_id = resp.json()["id"]

    resp = await api_client.put(
        f"/api/v1/projects/{project_id}",
        json={"name": "Updated", "description": "New desc"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "Updated"
    assert data["description"] == "New desc"


@pytest.mark.asyncio
async def test_update_project_not_found(api_client):
    resp = await api_client.put("/api/v1/projects/9999", json={"name": "X"})
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_project(api_client):
    resp = await api_client.post("/api/v1/projects", json={"name": "ToDelete"})
    project_id = resp.json()["id"]

    resp = await api_client.delete(f"/api/v1/projects/{project_id}")
    assert resp.status_code == 200
    assert resp.json()["ok"] is True

    # Verify deleted
    resp = await api_client.get(f"/api/v1/projects/{project_id}")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_project_not_found(api_client):
    resp = await api_client.delete("/api/v1/projects/9999")
    assert resp.status_code == 404


# --- Auto-Resolution ---


@pytest.mark.asyncio
async def test_auto_resolve(api_client, project_with_template_and_data):
    project_id = project_with_template_and_data["id"]
    resp = await api_client.post(f"/api/v1/projects/{project_id}/auto-resolve")
    assert resp.status_code == 200
    data = resp.json()
    assert "matches" in data
    assert "unresolved" in data


@pytest.mark.asyncio
async def test_auto_resolve_no_template(api_client):
    resp = await api_client.post("/api/v1/projects", json={"name": "NoTemplate"})
    project_id = resp.json()["id"]
    resp = await api_client.post(f"/api/v1/projects/{project_id}/auto-resolve")
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_auto_resolve_project_not_found(api_client):
    resp = await api_client.post("/api/v1/projects/9999/auto-resolve")
    assert resp.status_code == 404


# --- Validation ---


@pytest.mark.asyncio
async def test_validate_mappings(api_client, project_with_template_and_data):
    project_id = project_with_template_and_data["id"]
    resp = await api_client.post(
        f"/api/v1/projects/{project_id}/validate",
        json={
            "mappings": [
                {
                    "markerId": "marker-0",
                    "dataSource": "config.json",
                    "field": "name",
                    "path": "project",
                }
            ]
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_validate_missing_source(api_client, project_with_template_and_data):
    project_id = project_with_template_and_data["id"]
    resp = await api_client.post(
        f"/api/v1/projects/{project_id}/validate",
        json={
            "mappings": [
                {
                    "markerId": "marker-0",
                    "dataSource": "nonexistent.csv",
                    "field": "x",
                }
            ]
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    errors = [i for i in data if i["level"] == "error"]
    assert len(errors) >= 1


# --- Generation History ---


@pytest.mark.asyncio
async def test_generation_history(api_client, project_with_template_and_data):
    project_id = project_with_template_and_data["id"]

    # Generate a document first
    gen_resp = await api_client.post(
        f"/api/v1/projects/{project_id}/generate",
        json={
            "mappings": [
                {
                    "markerId": "marker-0",
                    "dataSource": "config.json",
                    "field": "name",
                    "path": "project",
                }
            ]
        },
    )
    assert gen_resp.status_code == 200
    run_id = gen_resp.json()["runId"]

    # List generations
    resp = await api_client.get(f"/api/v1/projects/{project_id}/generations")
    assert resp.status_code == 200
    runs = resp.json()
    assert len(runs) >= 1
    assert runs[0]["id"] == run_id

    # Get single generation
    resp = await api_client.get(f"/api/v1/projects/{project_id}/generations/{run_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == run_id

    # Download
    resp = await api_client.get(f"/api/v1/projects/{project_id}/generations/{run_id}/download")
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("application/vnd.openxmlformats-officedocument")


@pytest.mark.asyncio
async def test_generation_not_found(api_client):
    resp = await api_client.post("/api/v1/projects", json={"name": "HistTest"})
    project_id = resp.json()["id"]
    resp = await api_client.get(f"/api/v1/projects/{project_id}/generations/999")
    assert resp.status_code == 404


# --- Data Preview ---


@pytest.mark.asyncio
async def test_data_preview(api_client, project_with_template_and_data):
    project_id = project_with_template_and_data["id"]
    resp = await api_client.get(f"/api/v1/projects/{project_id}/data-sources/config.json/preview")
    assert resp.status_code == 200
    data = resp.json()
    assert data["source"] == "config.json"
    assert "sheets" in data
    assert "preview" in data


@pytest.mark.asyncio
async def test_data_preview_not_found(api_client):
    resp = await api_client.post("/api/v1/projects", json={"name": "PrevTest"})
    project_id = resp.json()["id"]
    resp = await api_client.get(f"/api/v1/projects/{project_id}/data-sources/missing.csv/preview")
    assert resp.status_code == 404


# --- Project Export/Import ---


@pytest.mark.asyncio
async def test_export_import_roundtrip(api_client, project_with_template_and_data):
    project_id = project_with_template_and_data["id"]

    # Export
    resp = await api_client.get(f"/api/v1/projects/{project_id}/export")
    assert resp.status_code == 200
    zip_bytes = resp.content
    assert len(zip_bytes) > 0

    # Import
    resp = await api_client.post(
        "/api/v1/projects/import",
        files={"file": ("project.zip", zip_bytes, "application/zip")},
    )
    assert resp.status_code == 200
    imported = resp.json()
    assert imported["name"] == "Phase2 Test"
    assert imported["id"] != project_id  # New ID


@pytest.mark.asyncio
async def test_export_project_not_found(api_client):
    resp = await api_client.get("/api/v1/projects/9999/export")
    assert resp.status_code == 404
