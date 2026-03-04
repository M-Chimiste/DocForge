from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    data_dir: Path = Path("./data")
    db_path: Path = Path("./data/docforge.db")
    upload_dir: Path = Path("./data/uploads")
    output_dir: Path = Path("./data/outputs")
    max_upload_size_mb: int = 50

    # LLM configuration (global defaults)
    llm_provider: str = ""
    llm_model: str = ""
    llm_endpoint: str | None = None
    llm_api_key_env: str = ""
    llm_temperature: float = 0.7
    llm_max_tokens: int = 2048

    model_config = {"env_prefix": "DOCFORGE_"}
