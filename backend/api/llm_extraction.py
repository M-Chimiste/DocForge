"""API endpoint for LLM-based schema-driven data extraction."""

from fastapi import APIRouter, Request

from api.errors import DocForgeError
from api.schemas import LLMExtractionRequest, LLMExtractionResponse
from core.llm_client import LLMClient, resolve_llm_config
from db.models import Project
from extractors.llm_extractor import FieldSchema, LLMExtractionSchema, LLMExtractor

router = APIRouter(tags=["llm-extraction"])


@router.post("/projects/{project_id}/data-sources/{filename}/extract-llm")
async def extract_with_llm(
    project_id: int,
    filename: str,
    body: LLMExtractionRequest,
    request: Request,
) -> LLMExtractionResponse:
    """Extract structured data from an unstructured source using LLM."""
    settings = request.app.state.settings
    session_factory = request.app.state.db

    # Validate project and resolve LLM config
    with session_factory() as session:
        project = session.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise DocForgeError(
                error="not_found",
                message=f"Project {project_id} not found",
                status_code=404,
            )
        project_llm = project.llm_config or {}

    llm_config = resolve_llm_config(settings, project_llm or None)
    if not llm_config.is_configured:
        raise DocForgeError(
            error="llm_not_configured",
            message="LLM is not configured. Set LLM provider and model to use extraction.",
            status_code=400,
        )

    # Find the data source file
    data_file = settings.upload_dir / str(project_id) / "data" / filename
    if not data_file.exists():
        raise DocForgeError(
            error="source_not_found",
            message=f"Data source '{filename}' not found",
            status_code=404,
        )

    # Read text content from file
    try:
        text = data_file.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        # For binary files, try extractors
        from core.data_loader import create_default_registry

        registry = create_default_registry()
        extractor = registry.get_extractor(data_file)
        extracted = extractor.extract(data_file)
        text = extracted.text_content or ""
        if not text:
            # Try to get text from dataframes
            for df in extracted.dataframes.values():
                text += df.to_string() + "\n"

    if not text.strip():
        raise DocForgeError(
            error="no_text_content",
            message=f"No text content could be extracted from '{filename}'",
            status_code=400,
        )

    # Build schema and extract
    schema = LLMExtractionSchema(
        fields=[
            FieldSchema(name=f.name, type=f.type, description=f.description) for f in body.fields
        ]
    )

    client = LLMClient(llm_config)
    llm_extractor = LLMExtractor(client)

    try:
        result = llm_extractor.extract(text, schema, filename)
    except Exception as e:
        raise DocForgeError(
            error="extraction_failed",
            message=f"LLM extraction failed: {e}",
            status_code=500,
        ) from e

    df = result.dataframes["extracted"]
    return LLMExtractionResponse(
        columns=list(df.columns),
        rows=df.to_dict(orient="records"),
        validation_errors=result.metadata.get("validation_errors", []),
        llm_model=result.metadata.get("llm_model", ""),
        tokens_used=result.metadata.get("tokens_used", 0),
    )
