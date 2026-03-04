"""Tests for template analysis API endpoint."""

import pytest


@pytest.mark.asyncio
async def test_analyze_template(api_client, templates_dir):
    template_path = templates_dir / "simple_placeholder.docx"
    with open(template_path, "rb") as f:
        resp = await api_client.post(
            "/api/v1/templates/analyze",
            files={"file": ("simple_placeholder.docx", f, "application/octet-stream")},
        )
    assert resp.status_code == 200
    data = resp.json()
    assert "sections" in data
    assert "markers" in data
    assert "tables" in data
    assert len(data["markers"]) >= 1


@pytest.mark.asyncio
async def test_analyze_mixed_template(api_client, templates_dir):
    template_path = templates_dir / "mixed_markers.docx"
    with open(template_path, "rb") as f:
        resp = await api_client.post(
            "/api/v1/templates/analyze",
            files={"file": ("mixed_markers.docx", f, "application/octet-stream")},
        )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["sections"]) >= 3
    assert len(data["markers"]) >= 3
    assert len(data["tables"]) >= 1
