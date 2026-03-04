from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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


app = FastAPI(title="DocForge", version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_exception_handler(DocForgeError, docforge_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)
app.include_router(api_router, prefix="/api/v1")
