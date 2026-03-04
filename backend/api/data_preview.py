"""Data preview API endpoint."""

from fastapi import APIRouter, Query, Request

from api.errors import DocForgeError
from api.schemas import DataPreviewResponse
from core.data_loader import load_data_sources

router = APIRouter(tags=["data-preview"])


@router.get("/projects/{project_id}/data-sources/{filename}/preview")
async def preview_data_source(
    project_id: int,
    filename: str,
    request: Request,
    rows: int = Query(default=10, ge=1, le=100),
) -> DataPreviewResponse:
    settings = request.app.state.settings
    file_path = settings.upload_dir / str(project_id) / "data" / filename

    if not file_path.exists():
        raise DocForgeError(
            error="not_found",
            message=f"Data source '{filename}' not found",
            status_code=404,
        )

    data_store = load_data_sources([file_path])
    source = data_store.get(filename)

    if not source:
        raise DocForgeError(
            error="extraction_failed",
            message=f"Could not extract data from '{filename}'",
            status_code=400,
        )

    sheets = list(source.dataframes.keys())
    preview: dict = {}
    for sheet_name, df in source.dataframes.items():
        truncated = df.head(rows)
        preview[sheet_name] = {
            "columns": list(truncated.columns),
            "rows": truncated.fillna("").values.tolist(),
            "totalRows": len(df),
        }

    return DataPreviewResponse(
        source=filename,
        sheets=sheets,
        preview=preview,
        text_snippet=source.text_content[:500] if source.text_content else None,
    )
