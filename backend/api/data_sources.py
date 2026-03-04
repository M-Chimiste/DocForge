import shutil

from fastapi import APIRouter, File, Request, UploadFile

from api.errors import DocForgeError
from db.models import Project

router = APIRouter(prefix="/projects/{project_id}/data-sources", tags=["data-sources"])


@router.post("")
async def upload_data_source(
    project_id: int,
    request: Request,
    file: UploadFile = File(),
) -> dict:
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

    # Save to project-scoped directory
    project_upload_dir = settings.upload_dir / str(project_id) / "data"
    project_upload_dir.mkdir(parents=True, exist_ok=True)
    upload_path = project_upload_dir / file.filename

    with open(upload_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    return {
        "filename": file.filename,
        "path": str(upload_path),
        "size": upload_path.stat().st_size,
    }


@router.get("")
async def list_data_sources(project_id: int, request: Request) -> list[dict]:
    settings = request.app.state.settings
    project_data_dir = settings.upload_dir / str(project_id) / "data"
    if not project_data_dir.exists():
        return []
    return [
        {"filename": f.name, "path": str(f), "size": f.stat().st_size}
        for f in project_data_dir.iterdir()
        if f.is_file()
    ]
