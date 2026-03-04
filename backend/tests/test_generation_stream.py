"""Tests for the SSE generation streaming endpoint."""

from __future__ import annotations

import json

import pytest

from db.models import Project


@pytest.fixture
async def project_with_data(api_client, templates_dir, data_dir):
    """Create a project with template and data uploaded."""
    resp = await api_client.post("/api/v1/projects", json={"name": "Stream Test"})
    project = resp.json()
    project_id = project["id"]

    # Set template path
    session_factory = api_client._transport.app.state.db
    settings = api_client._transport.app.state.settings
    with session_factory() as session:
        p = session.query(Project).filter(Project.id == project_id).first()
        p.template_path = str(settings.upload_dir / "simple_placeholder.docx")
        session.commit()

    # Copy template file
    template_dest = settings.upload_dir / "simple_placeholder.docx"
    template_dest.parent.mkdir(parents=True, exist_ok=True)
    import shutil

    shutil.copy(templates_dir / "simple_placeholder.docx", template_dest)

    # Upload data source
    with open(data_dir / "config.json", "rb") as f:
        await api_client.post(
            f"/api/v1/projects/{project_id}/data-sources",
            files={"file": ("config.json", f, "application/octet-stream")},
        )

    return project


def _parse_sse_events(raw: str) -> list[dict]:
    """Parse SSE formatted text into a list of events."""
    events = []
    current_event: dict = {}
    for line in raw.split("\n"):
        line = line.strip()
        if line.startswith("event:"):
            current_event["event"] = line.split(":", 1)[1].strip()
        elif line.startswith("data:"):
            data_str = line.split(":", 1)[1].strip()
            try:
                current_event["data"] = json.loads(data_str)
            except json.JSONDecodeError:
                current_event["data"] = data_str
        elif line == "" and current_event:
            if "event" in current_event:
                events.append(current_event)
            current_event = {}
    if current_event and "event" in current_event:
        events.append(current_event)
    return events


@pytest.mark.asyncio
async def test_stream_returns_sse_events(api_client, project_with_data):
    project_id = project_with_data["id"]

    resp = await api_client.post(
        f"/api/v1/projects/{project_id}/generate-stream",
        json={
            "mappings": [
                {
                    "markerId": "marker-0",
                    "dataSource": "config.json",
                    "field": "project_name",
                }
            ]
        },
    )
    assert resp.status_code == 200
    assert "text/event-stream" in resp.headers.get("content-type", "")

    events = _parse_sse_events(resp.text)

    # Should have progress events and a complete event
    event_types = [e.get("event") for e in events]
    assert "progress" in event_types
    assert "complete" in event_types

    # Complete event should have report
    complete_events = [e for e in events if e.get("event") == "complete"]
    assert len(complete_events) == 1
    complete_data = complete_events[0]["data"]
    assert "runId" in complete_data
    assert "downloadUrl" in complete_data
    assert "report" in complete_data


@pytest.mark.asyncio
async def test_stream_progress_events_ordered(api_client, project_with_data):
    project_id = project_with_data["id"]

    resp = await api_client.post(
        f"/api/v1/projects/{project_id}/generate-stream",
        json={
            "mappings": [
                {
                    "markerId": "marker-0",
                    "dataSource": "config.json",
                    "field": "project_name",
                }
            ]
        },
    )

    events = _parse_sse_events(resp.text)
    progress_events = [e for e in events if e.get("event") == "progress"]

    # Should have at least parsing, ingestion, rendering stages
    stages = [e["data"].get("stage") for e in progress_events if isinstance(e.get("data"), dict)]
    assert "parsing" in stages
    assert "ingestion" in stages
    assert "rendering" in stages


@pytest.mark.asyncio
async def test_stream_not_found(api_client):
    resp = await api_client.post(
        "/api/v1/projects/9999/generate-stream",
        json={"mappings": []},
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_stream_no_template(api_client):
    resp = await api_client.post("/api/v1/projects", json={"name": "No Template"})
    project_id = resp.json()["id"]

    resp = await api_client.post(
        f"/api/v1/projects/{project_id}/generate-stream",
        json={"mappings": []},
    )
    assert resp.status_code == 400
