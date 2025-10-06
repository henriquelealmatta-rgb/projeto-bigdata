"""Kaggle API client for dataset download."""

import logging
import zipfile
from pathlib import Path
from typing import Optional

from kaggle.api.kaggle_api_extended import KaggleApi

from src.domain.exceptions import DataIngestionError

logger = logging.getLogger(__name__)


class KaggleDatasetClient:
    """Client for downloading datasets from Kaggle."""

    def __init__(self, username: Optional[str] = None, key: Optional[str] = None):
        """Initialize Kaggle client.

        Args:
            username: Kaggle username (optional, can be set via env)
            key: Kaggle API key (optional, can be set via env)
        """
        self.api = KaggleApi()
        try:
            self.api.authenticate()
            logger.info("Kaggle API authenticated successfully")
        except Exception as e:
            raise DataIngestionError(f"Failed to authenticate with Kaggle API: {e}")

    def download_dataset(
        self, dataset: str, destination_path: Path, unzip: bool = True
    ) -> Path:
        """Download dataset from Kaggle.

        Args:
            dataset: Dataset identifier (e.g., 'rounakbanik/the-movies-dataset')
            destination_path: Path to save the dataset
            unzip: Whether to unzip the downloaded files

        Returns:
            Path to the downloaded dataset directory

        Raises:
            DataIngestionError: If download fails
        """
        try:
            destination_path.mkdir(parents=True, exist_ok=True)

            logger.info(f"Downloading dataset '{dataset}' to {destination_path}")

            self.api.dataset_download_files(
                dataset, path=str(destination_path), unzip=unzip, quiet=False
            )

            logger.info(f"Dataset '{dataset}' downloaded successfully")

            return destination_path

        except Exception as e:
            raise DataIngestionError(f"Failed to download dataset: {e}")

    def list_dataset_files(self, dataset: str) -> list:
        """List files in a Kaggle dataset.

        Args:
            dataset: Dataset identifier

        Returns:
            List of file names in the dataset

        Raises:
            DataIngestionError: If listing fails
        """
        try:
            files = self.api.dataset_list_files(dataset).files
            return [f.name for f in files]
        except Exception as e:
            raise DataIngestionError(f"Failed to list dataset files: {e}")

