"""Data preview API endpoint."""

import math

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
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=500),
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
        total_rows = len(df)
        total_pages = max(1, math.ceil(total_rows / page_size))
        start = (page - 1) * page_size
        end = start + page_size
        paginated = df.iloc[start:end]
        preview[sheet_name] = {
            "columns": list(paginated.columns),
            "rows": paginated.fillna("").values.tolist(),
            "totalRows": total_rows,
            "page": page,
            "pageSize": page_size,
            "totalPages": total_pages,
        }

    return DataPreviewResponse(
        source=filename,
        sheets=sheets,
        preview=preview,
        text_snippet=source.text_content[:500] if source.text_content else None,
    )
