from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from api.errors import DocForgeError, docforge_exception_handler, generic_exception_handler
from api.router import api_router
from config import Settings
from db.database import init_db

settings = Settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    settings.output_dir.mkdir(parents=True, exist_ok=True)
    session_factory = init_db(str(settings.db_path))
    app.state.db = session_factory
    app.state.settings = settings
    yield


app = FastAPI(title="DocForge", version="1.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_exception_handler(DocForgeError, docforge_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)
app.include_router(api_router, prefix="/api/v1")

# Serve bundled frontend if available (PyPI/Docker installs)
_static_dir = Path(__file__).parent / "static"
if _static_dir.exists():
    app.mount("/", StaticFiles(directory=str(_static_dir), html=True), name="static")
