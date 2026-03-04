import shutil
from pathlib import Path

from fastapi import APIRouter, File, Request, UploadFile

from core.engine import GenerationEngine

router = APIRouter(prefix="/templates", tags=["templates"])


@router.post("/analyze")
async def analyze_template(request: Request, file: UploadFile = File()) -> dict:
    settings = request.app.state.settings
    upload_path = settings.upload_dir / file.filename
    with open(upload_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    engine = GenerationEngine()
    analysis = engine.analyze(Path(upload_path))
    return analysis.model_dump(mode="json")
