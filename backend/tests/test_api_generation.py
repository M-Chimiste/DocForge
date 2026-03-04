"""Tests for data source upload and document generation API endpoints."""

import pytest


@pytest.fixture
async def project_with_template(api_client, templates_dir):
    """Create a project and associate a template with it."""
    resp = await api_client.post("/api/v1/projects", json={"name": "Gen Test"})
    project = resp.json()

    # Upload template via analyze endpoint so it's in the upload dir
    template_path = templates_dir / "simple_placeholder.docx"
    with open(template_path, "rb") as f:
        await api_client.post(
            "/api/v1/templates/analyze",
            files={"file": ("simple_placeholder.docx", f, "application/octet-stream")},
        )

    # Manually set template_path on the project (since analyze doesn't do this)
    from db.models import Project

    session_factory = api_client._transport.app.state.db
    settings = api_client._transport.app.state.settings
    with session_factory() as session:
        p = session.query(Project).filter(Project.id == project["id"]).first()
        p.template_path = str(settings.upload_dir / "simple_placeholder.docx")
        session.commit()

    return project


@pytest.mark.asyncio
async def test_upload_data_source(api_client, data_dir):
    # Create a project first
    resp = await api_client.post("/api/v1/projects", json={"name": "Data Test"})
    project_id = resp.json()["id"]

    with open(data_dir / "config.json", "rb") as f:
        resp = await api_client.post(
            f"/api/v1/projects/{project_id}/data-sources",
            files={"file": ("config.json", f, "application/octet-stream")},
        )
    assert resp.status_code == 200
    data = resp.json()
    assert data["filename"] == "config.json"
    assert data["size"] > 0


@pytest.mark.asyncio
async def test_list_data_sources(api_client, data_dir):
    resp = await api_client.post("/api/v1/projects", json={"name": "List DS"})
    project_id = resp.json()["id"]

    # Upload two files
    for fname in ["config.json", "project_status.csv"]:
        with open(data_dir / fname, "rb") as f:
            await api_client.post(
                f"/api/v1/projects/{project_id}/data-sources",
                files={"file": (fname, f, "application/octet-stream")},
            )

    resp = await api_client.get(f"/api/v1/projects/{project_id}/data-sources")
    assert resp.status_code == 200
    assert len(resp.json()) == 2


@pytest.mark.asyncio
async def test_generate_document(api_client, project_with_template, data_dir):
    project_id = project_with_template["id"]

    # Upload data source
    with open(data_dir / "config.json", "rb") as f:
        await api_client.post(
            f"/api/v1/projects/{project_id}/data-sources",
            files={"file": ("config.json", f, "application/octet-stream")},
        )

    # Generate
    resp = await api_client.post(
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
    assert resp.status_code == 200
    data = resp.json()
    assert "runId" in data
    assert "downloadUrl" in data
    assert "report" in data
    assert data["report"]["rendered"] >= 1
    assert isinstance(data["report"]["totalMarkers"], int)


@pytest.mark.asyncio
async def test_generate_project_not_found(api_client):
    resp = await api_client.post(
        "/api/v1/projects/9999/generate",
        json={"mappings": []},
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_upload_data_source_project_not_found(api_client, data_dir):
    with open(data_dir / "config.json", "rb") as f:
        resp = await api_client.post(
            "/api/v1/projects/9999/data-sources",
            files={"file": ("config.json", f, "application/octet-stream")},
        )
    assert resp.status_code == 404
