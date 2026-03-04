from fastapi import APIRouter, Request

from api.schemas import ProjectCreate, ProjectResponse
from db.models import Project

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("", response_model=ProjectResponse)
async def create_project(body: ProjectCreate, request: Request) -> ProjectResponse:
    session_factory = request.app.state.db
    with session_factory() as session:
        project = Project(name=body.name, description=body.description)
        session.add(project)
        session.commit()
        session.refresh(project)
        return ProjectResponse(
            id=project.id,
            name=project.name,
            description=project.description,
            template_path=project.template_path,
            created_at=project.created_at.isoformat(),
            updated_at=project.updated_at.isoformat(),
        )


@router.get("", response_model=list[ProjectResponse])
async def list_projects(request: Request) -> list[ProjectResponse]:
    session_factory = request.app.state.db
    with session_factory() as session:
        projects = session.query(Project).order_by(Project.updated_at.desc()).all()
        return [
            ProjectResponse(
                id=p.id,
                name=p.name,
                description=p.description,
                template_path=p.template_path,
                created_at=p.created_at.isoformat(),
                updated_at=p.updated_at.isoformat(),
            )
            for p in projects
        ]


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: int, request: Request) -> ProjectResponse:
    session_factory = request.app.state.db
    with session_factory() as session:
        project = session.query(Project).filter(Project.id == project_id).first()
        if not project:
            from api.errors import DocForgeError

            raise DocForgeError(
                error="not_found",
                message=f"Project {project_id} not found",
                status_code=404,
            )
        return ProjectResponse(
            id=project.id,
            name=project.name,
            description=project.description,
            template_path=project.template_path,
            created_at=project.created_at.isoformat(),
            updated_at=project.updated_at.isoformat(),
        )
