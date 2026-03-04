"""Project export/import API endpoints."""

import json
import shutil
import tempfile
import zipfile
from pathlib import Path

from fastapi import APIRouter, File, Request, UploadFile
from fastapi.responses import FileResponse

from api.errors import DocForgeError
from api.schemas import ProjectResponse
from db.models import Project

router = APIRouter(tags=["project-export"])


@router.get("/projects/{project_id}/export")
async def export_project(project_id: int, request: Request) -> FileResponse:
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
        project_data = {
            "name": project.name,
            "description": project.description,
            "mapping_config": project.mapping_config,
        }
        template_path = project.template_path

    # Create zip archive
    tmp_dir = Path(tempfile.mkdtemp())
    zip_path = tmp_dir / f"project_{project_id}.zip"

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        # Project metadata
        zf.writestr("project.json", json.dumps(project_data, indent=2))

        # Template
        if template_path and Path(template_path).exists():
            zf.write(template_path, f"template/{Path(template_path).name}")

        # Data sources
        data_dir = settings.upload_dir / str(project_id) / "data"
        if data_dir.exists():
            for f in data_dir.iterdir():
                if f.is_file():
                    zf.write(f, f"data/{f.name}")

    return FileResponse(
        path=str(zip_path),
        media_type="application/zip",
        filename=f"project_{project_id}.zip",
    )


@router.post("/projects/import")
async def import_project(
    request: Request,
    file: UploadFile = File(),
) -> ProjectResponse:
    settings = request.app.state.settings
    session_factory = request.app.state.db

    # Save uploaded zip to temp location
    tmp_dir = Path(tempfile.mkdtemp())
    zip_path = tmp_dir / file.filename
    with open(zip_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            # Read project metadata
            if "project.json" not in zf.namelist():
                raise DocForgeError(
                    error="invalid_archive",
                    message="Archive missing project.json",
                    status_code=400,
                )

            project_data = json.loads(zf.read("project.json"))

            # Create project in DB
            with session_factory() as session:
                project = Project(
                    name=project_data.get("name", "Imported Project"),
                    description=project_data.get("description", ""),
                    mapping_config=project_data.get("mapping_config", {}),
                )
                session.add(project)
                session.commit()
                session.refresh(project)
                project_id = project.id

            # Extract template
            template_files = [n for n in zf.namelist() if n.startswith("template/")]
            if template_files:
                template_name = Path(template_files[0]).name
                template_dest = settings.upload_dir / template_name
                template_dest.parent.mkdir(parents=True, exist_ok=True)
                with zf.open(template_files[0]) as src, open(template_dest, "wb") as dst:
                    shutil.copyfileobj(src, dst)

                with session_factory() as session:
                    p = session.query(Project).filter(Project.id == project_id).first()
                    p.template_path = str(template_dest)
                    session.commit()

            # Extract data sources
            data_files = [n for n in zf.namelist() if n.startswith("data/")]
            if data_files:
                data_dir = settings.upload_dir / str(project_id) / "data"
                data_dir.mkdir(parents=True, exist_ok=True)
                for data_file in data_files:
                    dest = data_dir / Path(data_file).name
                    with zf.open(data_file) as src, open(dest, "wb") as dst:
                        shutil.copyfileobj(src, dst)

            # Return the created project
            with session_factory() as session:
                p = session.query(Project).filter(Project.id == project_id).first()
                return ProjectResponse(
                    id=p.id,
                    name=p.name,
                    description=p.description,
                    template_path=p.template_path,
                    created_at=p.created_at.isoformat(),
                    updated_at=p.updated_at.isoformat(),
                )
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)
