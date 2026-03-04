import uuid
from pathlib import Path

from fastapi import APIRouter, Request

from api.errors import DocForgeError
from api.schemas import (
    GenerateRequest,
    GenerateResponse,
    GenerationReportResponse,
    ValidationIssueResponse,
)
from core.engine import GenerationEngine
from core.llm_client import resolve_llm_config
from core.models import ConditionalConfig, MappingEntry, TransformConfig, TransformType
from db.models import GenerationRun, Project

router = APIRouter(tags=["generation"])


@router.post("/projects/{project_id}/generate")
async def generate_document(
    project_id: int,
    body: GenerateRequest,
    request: Request,
) -> GenerateResponse:
    settings = request.app.state.settings
    session_factory = request.app.state.db

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

    if not template_path.exists():
        raise DocForgeError(
            error="template_missing",
            message="Template file not found on disk",
            status_code=400,
        )

    # Collect data source paths
    project_data_dir = settings.upload_dir / str(project_id) / "data"
    data_paths = list(project_data_dir.iterdir()) if project_data_dir.exists() else []

    # Convert request mappings to domain model
    mappings = [
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

    # Convert conditionals
    conditionals = (
        [
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
        if body.conditionals
        else None
    )

    # Resolve LLM config
    with session_factory() as session:
        project = session.query(Project).filter(Project.id == project_id).first()
        project_llm = project.llm_config if project else {}
    llm_config = resolve_llm_config(settings, project_llm or None)

    # Generate
    output_dir = settings.output_dir / str(project_id)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"output_{uuid.uuid4().hex[:8]}.docx"

    engine = GenerationEngine(llm_config=llm_config)
    analysis = engine.analyze(template_path)
    report = engine.generate(template_path, data_paths, mappings, output_path, conditionals)

    # Record generation run in database
    with session_factory() as session:
        run = GenerationRun(
            project_id=project_id,
            mapping_snapshot=[m.model_dump(mode="json") for m in body.mappings],
            output_path=str(output_path),
            report=report.model_dump(mode="json"),
            analysis_snapshot=analysis.model_dump(mode="json"),
            auto_resolution_snapshot=(
                report.auto_resolution_report.model_dump(mode="json")
                if report.auto_resolution_report
                else None
            ),
            status="completed",
        )
        session.add(run)
        session.commit()
        session.refresh(run)
        run_id = run.id

    return GenerateResponse(
        run_id=run_id,
        download_url=f"/api/v1/projects/{project_id}/generations/{run_id}/download",
        report=GenerationReportResponse(
            total_markers=report.total_markers,
            rendered=report.rendered,
            skipped=report.skipped,
            warnings=[
                ValidationIssueResponse(level=w.level, marker_id=w.marker_id, message=w.message)
                for w in report.warnings
            ],
            errors=[
                ValidationIssueResponse(level=e.level, marker_id=e.marker_id, message=e.message)
                for e in report.errors
            ],
        ),
    )
