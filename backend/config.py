from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    data_dir: Path = Path("./data")
    db_path: Path = Path("./data/docforge.db")
    upload_dir: Path = Path("./data/uploads")
    output_dir: Path = Path("./data/outputs")
    max_upload_size_mb: int = 50

    model_config = {"env_prefix": "DOCFORGE_"}
