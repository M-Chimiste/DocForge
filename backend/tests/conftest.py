from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def fixtures_dir():
    return FIXTURES_DIR


@pytest.fixture
def templates_dir():
    return FIXTURES_DIR / "templates"


@pytest.fixture
def data_dir():
    return FIXTURES_DIR / "data"


@pytest.fixture
async def api_client(tmp_path):
    """Async test client with isolated temp DB and directories."""
    from config import Settings
    from db.database import init_db
    from main import app

    settings = Settings(
        data_dir=tmp_path / "data",
        db_path=tmp_path / "data" / "test.db",
        upload_dir=tmp_path / "data" / "uploads",
        output_dir=tmp_path / "data" / "outputs",
    )
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    settings.output_dir.mkdir(parents=True, exist_ok=True)
    session_factory = init_db(str(settings.db_path))
    app.state.db = session_factory
    app.state.settings = settings

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
