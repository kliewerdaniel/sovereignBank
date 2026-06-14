"""Configuration for Sovereign Memory Bank."""

from pathlib import Path
from typing import Optional
from pydantic import Field, model_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment or defaults."""

    project_root: Path = Field(default_factory=lambda: Path.cwd())
    memory_bank_dir: Optional[Path] = None
    kbmd_dir: Optional[Path] = None
    sqlite_db_path: Optional[Path] = None
    chroma_persist_dir: Optional[Path] = None

    # ChromaDB
    chroma_collection: str = "memory_objects"
    embedding_model: str = "nomic-embed-text"

    # Ollama
    ollama_host: str = "http://localhost:11434"
    ollama_model: str = "qwen2.5-coder:32b"

    # Evolution engine
    evolution_interval_seconds: int = 3600

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    model_config = {"env_prefix": "SMB_", "env_file": ".env"}

    @model_validator(mode="after")
    def resolve_defaults(self) -> "Settings":
        if self.memory_bank_dir is None:
            self.memory_bank_dir = self.project_root / "memory-bank"
        if self.kbmd_dir is None:
            self.kbmd_dir = self.project_root / "kbmd"
        if self.sqlite_db_path is None:
            self.sqlite_db_path = self.memory_bank_dir / "metadata.db"
        if self.chroma_persist_dir is None:
            self.chroma_persist_dir = self.memory_bank_dir / "vectors"
        return self


settings = Settings()
