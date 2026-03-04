"""Generation history API endpoints."""

from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import FileResponse

from api.errors import catalog_error
from api.schemas import GenerationRunResponse
from db.models import GenerationRun, Project

router = APIRouter(tags=["generation-history"])


@router.get("/projects/{project_id}/generations")
async def list_generations(project_id: int, request: Request) -> list[GenerationRunResponse]:
    session_factory = request.app.state.db

    with session_factory() as session:
        project = session.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise catalog_error("project_not_found", status_code=404, project_id=project_id)

        runs = (
            session.query(GenerationRun)
            .filter(GenerationRun.project_id == project_id)
            .order_by(GenerationRun.created_at.desc())
            .all()
        )
        return [
            GenerationRunResponse(
                id=r.id,
                project_id=r.project_id,
                status=r.status,
                report=r.report,
                created_at=r.created_at.isoformat(),
            )
            for r in runs
        ]


@router.get("/projects/{project_id}/generations/{run_id}")
async def get_generation(project_id: int, run_id: int, request: Request) -> GenerationRunResponse:
    session_factory = request.app.state.db

    with session_factory() as session:
        run = (
            session.query(GenerationRun)
            .filter(
                GenerationRun.id == run_id,
                GenerationRun.project_id == project_id,
            )
            .first()
        )
        if not run:
            raise catalog_error("generation_not_found", status_code=404, run_id=run_id)
        return GenerationRunResponse(
            id=run.id,
            project_id=run.project_id,
            status=run.status,
            report=run.report,
            created_at=run.created_at.isoformat(),
        )


@router.get("/projects/{project_id}/generations/{run_id}/download")
async def download_generation(project_id: int, run_id: int, request: Request) -> FileResponse:
    session_factory = request.app.state.db

    with session_factory() as session:
        run = (
            session.query(GenerationRun)
            .filter(
                GenerationRun.id == run_id,
                GenerationRun.project_id == project_id,
            )
            .first()
        )
        if not run:
            raise catalog_error("generation_not_found", status_code=404, run_id=run_id)
        output_path = run.output_path

    if not output_path or not Path(output_path).exists():
        raise catalog_error(
            "export_failed",
            status_code=404,
            reason="Generated document file not found on disk",
        )

    return FileResponse(
        path=output_path,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=Path(output_path).name,
    )
