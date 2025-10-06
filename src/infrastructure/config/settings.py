"""Application settings and configuration."""

import os
from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Kaggle API
    kaggle_username: Optional[str] = None
    kaggle_key: Optional[str] = None

    # Google Gemini API
    google_api_key: Optional[str] = Field(default=None, alias="GOOGLE_API_KEY")

    # Pipeline configuration
    environment: str = "development"
    log_level: str = "INFO"
    data_dir: Path = Path("./data")

    # AWS Configuration
    aws_region: str = "us-east-1"
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    aws_s3_bucket: Optional[str] = None

    # Azure Configuration
    azure_subscription_id: Optional[str] = None
    azure_resource_group: Optional[str] = None
    azure_storage_account: Optional[str] = None

    # GCP Configuration
    gcp_project_id: Optional[str] = None
    gcp_region: str = "us-central1"
    gcp_bucket: Optional[str] = None

    # Dataset configuration
    kaggle_dataset: str = "rounakbanik/the-movies-dataset"

    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
        "extra": "ignore",
    }

    @property
    def bronze_dir(self) -> Path:
        """Get bronze layer directory path."""
        return self.data_dir / "raw"

    @property
    def silver_dir(self) -> Path:
        """Get silver layer directory path."""
        return self.data_dir / "processed"

    @property
    def gold_dir(self) -> Path:
        """Get gold layer directory path."""
        return self.data_dir / "refined"

    def ensure_directories(self) -> None:
        """Ensure all data directories exist."""
        self.bronze_dir.mkdir(parents=True, exist_ok=True)
        self.silver_dir.mkdir(parents=True, exist_ok=True)
        self.gold_dir.mkdir(parents=True, exist_ok=True)


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
