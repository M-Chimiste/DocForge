"""SSE streaming endpoint for document generation with real-time progress."""

from __future__ import annotations

import asyncio
import json
import queue
import uuid
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Request
from sse_starlette.sse import EventSourceResponse

from api.errors import DocForgeError
from api.schemas import GenerateRequest
from core.engine import GenerationEngine
from core.llm_client import resolve_llm_config
from core.models import ConditionalConfig, MappingEntry, TransformConfig, TransformType
from db.models import GenerationRun, Project

router = APIRouter(tags=["generation-stream"])


def _convert_mappings(body: GenerateRequest) -> list[MappingEntry]:
    return [
        MappingEntry(
            marker_id=m.marker_id,
            data_source=m.data_source,
            field=m.field,
            sheet=m.sheet,
            path=m.path,
            transforms=[
                TransformConfig(type=TransformType(t.type), params=t.params) for t in m.transforms
            ],
        )
        for m in body.mappings
    ]


def _convert_conditionals(body: GenerateRequest) -> list[ConditionalConfig] | None:
    if not body.conditionals:
        return None
    return [
        ConditionalConfig(
            section_id=c.section_id,
            condition_type=c.condition_type,
            data_source=c.data_source,
            field=c.field,
            operator=c.operator,
            value=c.value,
            include=c.include,
        )
        for c in body.conditionals
    ]


@router.post("/projects/{project_id}/generate-stream")
async def generate_stream(
    project_id: int,
    body: GenerateRequest,
    request: Request,
) -> EventSourceResponse:
    settings = request.app.state.settings
    session_factory = request.app.state.db

    # Validate project
    with session_factory() as session:
        project = session.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise DocForgeError(
                error="not_found",
                message=f"Project {project_id} not found",
                status_code=404,
            )
        if not project.template_path:
            raise DocForgeError(
                error="no_template",
                message="No template associated with this project",
                status_code=400,
            )
        template_path = Path(project.template_path)
        project_llm = project.llm_config or {}

    if not template_path.exists():
        raise DocForgeError(
            error="template_missing",
            message="Template file not found on disk",
            status_code=400,
        )

    # Collect data source paths
    project_data_dir = settings.upload_dir / str(project_id) / "data"
    data_paths = list(project_data_dir.iterdir()) if project_data_dir.exists() else []

    mappings = _convert_mappings(body)
    conditionals = _convert_conditionals(body)
    llm_config = resolve_llm_config(settings, project_llm or None)

    output_dir = settings.output_dir / str(project_id)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"output_{uuid.uuid4().hex[:8]}.docx"

    progress_queue: queue.Queue[dict[str, Any]] = queue.Queue()

    def progress_callback(event: dict[str, Any]) -> None:
        progress_queue.put(event)

    async def event_generator():
        loop = asyncio.get_event_loop()

        def run_generation():
            engine = GenerationEngine(llm_config=llm_config)
            return engine.generate(
                template_path,
                data_paths,
                mappings,
                output_path,
                conditionals,
                progress_callback=progress_callback,
            )

        future = loop.run_in_executor(None, run_generation)

        # Yield progress events while generation runs
        while not future.done():
            try:
                event = progress_queue.get(timeout=0.1)
                yield {"event": "progress", "data": json.dumps(event)}
            except queue.Empty:
                pass
            await asyncio.sleep(0)

        # Drain remaining events
        while not progress_queue.empty():
            try:
                event = progress_queue.get_nowait()
                yield {"event": "progress", "data": json.dumps(event)}
            except queue.Empty:
                break

        # Get the result (may raise if generation failed)
        report = future.result()

        # Record in database
        with session_factory() as session:
            run = GenerationRun(
                project_id=project_id,
                mapping_snapshot=[m.model_dump(mode="json") for m in body.mappings],
                output_path=str(output_path),
                report=report.model_dump(mode="json"),
                status="completed",
            )
            session.add(run)
            session.commit()
            session.refresh(run)
            run_id = run.id

        # Yield final complete event
        yield {
            "event": "complete",
            "data": json.dumps(
                {
                    "runId": run_id,
                    "downloadUrl": f"/api/v1/projects/{project_id}/generations/{run_id}/download",
                    "report": {
                        "totalMarkers": report.total_markers,
                        "rendered": report.rendered,
                        "skipped": report.skipped,
                        "warnings": [
                            {"level": w.level, "markerId": w.marker_id, "message": w.message}
                            for w in report.warnings
                        ],
                        "errors": [
                            {"level": e.level, "markerId": e.marker_id, "message": e.message}
                            for e in report.errors
                        ],
                    },
                }
            ),
        }

    return EventSourceResponse(event_generator())
