import uuid
from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import FileResponse

from api.errors import DocForgeError
from api.schemas import GenerateRequest
from core.engine import GenerationEngine
from core.models import MappingEntry
from db.models import Project

router = APIRouter(tags=["generation"])


@router.post("/projects/{project_id}/generate")
async def generate_document(
    project_id: int,
    body: GenerateRequest,
    request: Request,
) -> FileResponse:
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
        )
        for m in body.mappings
    ]

    # Generate
    output_dir = settings.output_dir / str(project_id)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"output_{uuid.uuid4().hex[:8]}.docx"

    engine = GenerationEngine()
    engine.generate(template_path, data_paths, mappings, output_path)

    return FileResponse(
        path=str(output_path),
        filename=output_path.name,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )
