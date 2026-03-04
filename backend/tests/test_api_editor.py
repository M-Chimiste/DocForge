"""Integration tests for the editor API endpoints."""

from __future__ import annotations

from pathlib import Path

import pytest
from httpx import AsyncClient

FIXTURES_DIR = Path(__file__).parent / "fixtures"
TEMPLATES_DIR = FIXTURES_DIR / "templates"
DATA_DIR = FIXTURES_DIR / "data"


async def _create_project_with_generation(api_client: AsyncClient, tmp_path: Path) -> dict:
    """Helper: create project, upload template and data, generate document."""
    from db.models import Project

    session_factory = api_client._transport.app.state.db
    settings = api_client._transport.app.state.settings

    # Create project
    resp = await api_client.post("/api/v1/projects", json={"name": "Editor Test"})
    assert resp.status_code == 200
    project = resp.json()
    project_id = project["id"]

    # Upload template via analyze endpoint
    template_path = TEMPLATES_DIR / "simple_placeholder.docx"
    with open(template_path, "rb") as f:
        resp = await api_client.post(
            "/api/v1/templates/analyze",
            files={"file": ("simple_placeholder.docx", f, "application/octet-stream")},
        )
    assert resp.status_code == 200
    analysis = resp.json()

    # Manually associate template with project (analyze doesn't do this)
    with session_factory() as session:
        p = session.query(Project).filter(Project.id == project_id).first()
        p.template_path = str(settings.upload_dir / "simple_placeholder.docx")
        session.commit()

    # Upload data source
    data_path = DATA_DIR / "config.json"
    with open(data_path, "rb") as f:
        resp = await api_client.post(
            f"/api/v1/projects/{project_id}/data-sources",
            files={"file": ("config.json", f, "application/octet-stream")},
        )
    assert resp.status_code == 200

    # Generate document with marker-0 mapped to config.json project.name
    mappings = [
        {
            "markerId": "marker-0",
            "dataSource": "config.json",
            "field": "name",
            "path": "project",
        }
    ]

    resp = await api_client.post(
        f"/api/v1/projects/{project_id}/generate",
        json={"mappings": mappings},
    )
    assert resp.status_code == 200
    gen_result = resp.json()

    return {
        "projectId": project_id,
        "runId": gen_result["runId"],
        "analysis": analysis,
        "mappings": mappings,
    }


class TestGetEditorDocument:
    @pytest.mark.asyncio
    async def test_get_document_converts_on_first_call(self, api_client):
        result = await _create_project_with_generation(api_client, None)
        run_id = result["runId"]

        resp = await api_client.get(f"/api/v1/generations/{run_id}/document")
        assert resp.status_code == 200
        doc = resp.json()

        # Should have content and meta
        assert "content" in doc
        assert "meta" in doc
        assert doc["content"]["type"] == "doc"
        assert doc["meta"]["generation_run_id"] == run_id

    @pytest.mark.asyncio
    async def test_get_document_returns_cached_on_second_call(self, api_client):
        result = await _create_project_with_generation(api_client, None)
        run_id = result["runId"]

        # First call converts
        resp1 = await api_client.get(f"/api/v1/generations/{run_id}/document")
        assert resp1.status_code == 200
        doc1 = resp1.json()

        # Second call returns cached
        resp2 = await api_client.get(f"/api/v1/generations/{run_id}/document")
        assert resp2.status_code == 200
        doc2 = resp2.json()

        assert doc1 == doc2

    @pytest.mark.asyncio
    async def test_get_document_not_found(self, api_client):
        resp = await api_client.get("/api/v1/generations/9999/document")
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_document_has_marker_metadata(self, api_client):
        result = await _create_project_with_generation(api_client, None)
        run_id = result["runId"]

        resp = await api_client.get(f"/api/v1/generations/{run_id}/document")
        doc = resp.json()

        meta = doc["meta"]
        assert "marker_metadata" in meta
        # Should have metadata for the placeholder marker
        if meta["marker_metadata"]:
            first_key = next(iter(meta["marker_metadata"]))
            marker_meta = meta["marker_metadata"][first_key]
            assert "marker_id" in marker_meta
            assert "original_text" in marker_meta
            assert "rendered_by" in marker_meta

    @pytest.mark.asyncio
    async def test_document_has_template_analysis(self, api_client):
        result = await _create_project_with_generation(api_client, None)
        run_id = result["runId"]

        resp = await api_client.get(f"/api/v1/generations/{run_id}/document")
        doc = resp.json()

        assert doc["meta"]["template_analysis"] is not None
        assert "sections" in doc["meta"]["template_analysis"]
        assert "markers" in doc["meta"]["template_analysis"]


class TestSaveEditorDocument:
    @pytest.mark.asyncio
    async def test_save_and_retrieve(self, api_client):
        result = await _create_project_with_generation(api_client, None)
        run_id = result["runId"]

        # Get original
        resp = await api_client.get(f"/api/v1/generations/{run_id}/document")
        original = resp.json()

        # Modify and save
        modified = original.copy()
        modified["content"]["content"] = [
            {"type": "paragraph", "content": [{"type": "text", "text": "Edited text"}]}
        ]
        resp = await api_client.put(
            f"/api/v1/generations/{run_id}/document",
            json=modified,
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "saved"

        # Retrieve and verify
        resp = await api_client.get(f"/api/v1/generations/{run_id}/document")
        saved = resp.json()
        assert saved["content"]["content"][0]["content"][0]["text"] == "Edited text"

    @pytest.mark.asyncio
    async def test_save_not_found(self, api_client):
        resp = await api_client.put(
            "/api/v1/generations/9999/document",
            json={"content": {}, "meta": {}},
        )
        assert resp.status_code == 404


class TestExportDocument:
    @pytest.mark.asyncio
    async def test_export_original_when_no_edits(self, api_client):
        result = await _create_project_with_generation(api_client, None)
        run_id = result["runId"]

        resp = await api_client.post(f"/api/v1/generations/{run_id}/export")
        assert resp.status_code == 200
        assert "wordprocessingml" in resp.headers.get("content-type", "")

    @pytest.mark.asyncio
    async def test_export_after_edits(self, api_client):
        result = await _create_project_with_generation(api_client, None)
        run_id = result["runId"]

        # Get and save edited state
        resp = await api_client.get(f"/api/v1/generations/{run_id}/document")
        doc = resp.json()
        await api_client.put(f"/api/v1/generations/{run_id}/document", json=doc)

        # Export
        resp = await api_client.post(f"/api/v1/generations/{run_id}/export")
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_export_not_found(self, api_client):
        resp = await api_client.post("/api/v1/generations/9999/export")
        assert resp.status_code == 404
