"""Editor API: document retrieval, persistence, regeneration, and export."""

from __future__ import annotations

import uuid
from pathlib import Path

from docx import Document
from fastapi import APIRouter, Request
from fastapi.responses import FileResponse

from api.errors import DocForgeError
from api.schemas import RegenerateSectionRequest, RegenerateSectionResponse
from core.docx_to_editor import DocxToEditorConverter
from core.editor_models import EditorDocument
from core.editor_to_docx import EditorToDocxConverter
from core.llm_client import LLMClient, resolve_llm_config
from core.llm_context import ContextAssembler
from core.models import (
    AutoResolutionReport,
    GenerationReport,
    MappingEntry,
    TemplateAnalysis,
)
from db.models import GenerationRun, Project

router = APIRouter(tags=["editor"])

SYSTEM_PROMPT = (
    "You are a document writing assistant. Generate clear, professional text "
    "that directly addresses the instruction. Do not include meta-commentary "
    "about the task. Output only the text to be inserted into the document."
)


def _get_run(session, run_id: int) -> GenerationRun:
    run = session.query(GenerationRun).filter(GenerationRun.id == run_id).first()
    if not run:
        raise DocForgeError(
            error="not_found",
            message=f"Generation run {run_id} not found",
            status_code=404,
        )
    return run


@router.get("/generations/{run_id}/document")
async def get_editor_document(run_id: int, request: Request) -> dict:
    """Return the generated document in TipTap-compatible JSON format.

    If editor_state exists, returns it (preserving user edits).
    Otherwise, converts the output .docx on-the-fly and caches the result.
    """
    session_factory = request.app.state.db

    with session_factory() as session:
        run = _get_run(session, run_id)

        if run.editor_state:
            return run.editor_state

        # Convert .docx to editor format
        if not run.output_path or not Path(run.output_path).exists():
            raise DocForgeError(
                error="output_missing",
                message="Generated document file not found",
                status_code=404,
            )

        doc = Document(run.output_path)
        report = (
            GenerationReport(**run.report)
            if run.report
            else GenerationReport(
                total_markers=0, rendered=0, skipped=0, warnings=[], errors=[], results=[]
            )
        )
        analysis = (
            TemplateAnalysis(**run.analysis_snapshot)
            if run.analysis_snapshot
            else TemplateAnalysis(sections=[], markers=[], tables=[])
        )
        mappings = [MappingEntry(**m) for m in run.mapping_snapshot] if run.mapping_snapshot else []
        auto_report = (
            AutoResolutionReport(**run.auto_resolution_snapshot)
            if run.auto_resolution_snapshot
            else None
        )

        converter = DocxToEditorConverter(
            doc,
            report,
            analysis,
            mappings,
            auto_resolution_report=auto_report,
            project_id=run.project_id,
            run_id=run.id,
        )
        editor_doc = converter.convert()
        state = editor_doc.model_dump(mode="json")

        # Cache for future requests
        run.editor_state = state
        session.commit()

        return state


@router.put("/generations/{run_id}/document")
async def save_editor_document(run_id: int, request: Request) -> dict:
    """Persist the current editor state (TipTap JSON) to the database."""
    session_factory = request.app.state.db
    body = await request.json()

    with session_factory() as session:
        run = _get_run(session, run_id)
        run.editor_state = body
        session.commit()

    return {"status": "saved"}


@router.post("/generations/{run_id}/regenerate-section")
async def regenerate_section(
    run_id: int,
    body: RegenerateSectionRequest,
    request: Request,
) -> RegenerateSectionResponse:
    """Re-run LLM for a specific marker with optional prompt modification.

    Returns new text content; the frontend patches it into the editor state.
    """
    settings = request.app.state.settings
    session_factory = request.app.state.db

    with session_factory() as session:
        run = _get_run(session, run_id)
        project = session.query(Project).filter(Project.id == run.project_id).first()
        if not project:
            raise DocForgeError(
                error="not_found",
                message="Project not found",
                status_code=404,
            )

        # Resolve LLM config
        project_llm = project.llm_config or {}
        llm_config = resolve_llm_config(settings, project_llm or None)

        if not llm_config.is_configured:
            raise DocForgeError(
                error="llm_not_configured",
                message="No LLM configured for this project",
                status_code=400,
            )

        # Find the marker in analysis
        analysis = TemplateAnalysis(**run.analysis_snapshot) if run.analysis_snapshot else None
        if not analysis:
            raise DocForgeError(
                error="no_analysis",
                message="No template analysis available for this run",
                status_code=400,
            )

        target_marker = None
        for marker in analysis.markers:
            if marker.id == body.marker_id:
                target_marker = marker
                break
        if not target_marker:
            raise DocForgeError(
                error="marker_not_found",
                message=f"Marker {body.marker_id} not found in analysis",
                status_code=404,
            )

        # Load data sources for context
        from core.data_loader import load_data_sources

        project_data_dir = settings.upload_dir / str(run.project_id) / "data"
        data_paths = list(project_data_dir.iterdir()) if project_data_dir.exists() else []
        data_store = load_data_sources(data_paths)

        # Assemble context
        mappings = [MappingEntry(**m) for m in run.mapping_snapshot] if run.mapping_snapshot else []
        assembler = ContextAssembler()
        resolved_context = assembler.assemble(target_marker, analysis, data_store, mappings)

        # Build prompt
        prompt_text = body.modified_prompt or target_marker.text
        parts: list[str] = []
        if resolved_context.context_text:
            parts.append("CONTEXT DATA:\n" + resolved_context.context_text)
        parts.append("INSTRUCTION:\n" + prompt_text)
        full_prompt = "\n\n".join(parts)

        # Call LLM
        llm_client = LLMClient(llm_config)
        response = llm_client.complete(full_prompt, system=SYSTEM_PROMPT)

        return RegenerateSectionResponse(
            content=response.content,
            llm_usage={
                "model": response.model,
                "prompt_tokens": response.prompt_tokens,
                "completion_tokens": response.completion_tokens,
            },
        )


@router.post("/generations/{run_id}/export")
async def export_document(run_id: int, request: Request) -> FileResponse:
    """Convert the current editor state back to .docx and return as download.

    If no editor state exists, returns the original generated .docx.
    """
    settings = request.app.state.settings
    session_factory = request.app.state.db

    with session_factory() as session:
        run = _get_run(session, run_id)
        project = session.query(Project).filter(Project.id == run.project_id).first()

        if not run.editor_state:
            # No edits — return original output
            if not run.output_path or not Path(run.output_path).exists():
                raise DocForgeError(
                    error="output_missing",
                    message="Generated document file not found",
                    status_code=404,
                )
            return FileResponse(
                run.output_path,
                media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                filename=f"docforge_export_{run.id}.docx",
            )

        # Convert editor state to .docx
        editor_doc = EditorDocument(**run.editor_state)

        template_path = project.template_path if project else None
        if not template_path or not Path(template_path).exists():
            raise DocForgeError(
                error="template_missing",
                message="Original template not found for export",
                status_code=400,
            )

        converter = EditorToDocxConverter(editor_doc, Path(template_path))
        doc = converter.convert()

        # Save exported file
        export_dir = settings.output_dir / str(run.project_id)
        export_dir.mkdir(parents=True, exist_ok=True)
        export_path = export_dir / f"export_{run.id}_{uuid.uuid4().hex[:6]}.docx"
        doc.save(str(export_path))

        return FileResponse(
            str(export_path),
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            filename=f"docforge_export_{run.id}.docx",
        )
