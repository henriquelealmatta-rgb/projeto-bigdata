"""Use case for ingesting movies dataset from Kaggle."""

import logging
from pathlib import Path

from src.domain.exceptions import DataIngestionError
from src.infrastructure.config import Settings
from src.infrastructure.external import KaggleDatasetClient
from src.infrastructure.repositories import DataRepository

logger = logging.getLogger(__name__)


class IngestMoviesUseCase:
    """Use case for ingesting movies data from Kaggle (Bronze Layer)."""

    def __init__(self, settings: Settings):
        """Initialize use case.

        Args:
            settings: Application settings
        """
        self.settings = settings
        self.kaggle_client = KaggleDatasetClient(
            username=settings.kaggle_username, key=settings.kaggle_key
        )
        self.repository = DataRepository(settings.bronze_dir)

    def execute(self) -> Path:
        """Execute data ingestion.

        Downloads the dataset from Kaggle and stores it in the bronze layer.

        Returns:
            Path to the ingested data directory

        Raises:
            DataIngestionError: If ingestion fails
        """
        try:
            logger.info("Starting data ingestion from Kaggle")
            logger.info(f"Dataset: {self.settings.kaggle_dataset}")
            logger.info(f"Destination: {self.settings.bronze_dir}")

            # Ensure bronze directory exists
            self.settings.bronze_dir.mkdir(parents=True, exist_ok=True)

            # List available files
            logger.info("Listing dataset files...")
            files = self.kaggle_client.list_dataset_files(self.settings.kaggle_dataset)
            logger.info(f"Found {len(files)} files in dataset:")
            for file in files:
                logger.info(f"  - {file}")

            # Download dataset
            dataset_path = self.kaggle_client.download_dataset(
                dataset=self.settings.kaggle_dataset,
                destination_path=self.settings.bronze_dir,
                unzip=True,
            )

            # Verify downloaded files
            downloaded_files = list(dataset_path.glob("*.csv"))
            logger.info(f"Downloaded {len(downloaded_files)} CSV files:")
            for file in downloaded_files:
                logger.info(f"  - {file.name} ({file.stat().st_size / 1024 / 1024:.2f} MB)")

            logger.info("Data ingestion completed successfully")

            return dataset_path

        except Exception as e:
            logger.error(f"Data ingestion failed: {e}")
            raise DataIngestionError(f"Failed to ingest data: {e}")

