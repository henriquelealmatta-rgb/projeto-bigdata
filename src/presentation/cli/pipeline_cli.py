"""Command-line interface for pipeline execution."""

import logging
import sys
import time
from typing import Optional

from src.application.ingestion import IngestMoviesUseCase
from src.application.loading import LoadAnalyticsUseCase
from src.application.transformation import TransformMoviesUseCase
from src.infrastructure.config import Settings

logger = logging.getLogger(__name__)


class PipelineCLI:
    """CLI for pipeline execution."""

    def __init__(self, settings: Settings):
        """Initialize CLI.

        Args:
            settings: Application settings
        """
        self.settings = settings
        self._setup_logging()

    def _setup_logging(self) -> None:
        """Setup logging configuration."""
        logging.basicConfig(
            level=getattr(logging, self.settings.log_level.upper()),
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler("pipeline.log"),
            ],
        )

    def run_full_pipeline(self) -> bool:
        """Run the complete pipeline.

        Returns:
            True if successful, False otherwise
        """
        logger.info("=" * 80)
        logger.info("Starting Movies Big Data Pipeline")
        logger.info("=" * 80)

        start_time = time.time()

        try:
            # Ensure directories exist
            self.settings.ensure_directories()

            # Stage 1: Ingestion
            if not self.run_ingestion():
                return False

            # Stage 2: Transformation
            if not self.run_transformation():
                return False

            # Stage 3: Loading
            if not self.run_loading():
                return False

            elapsed_time = time.time() - start_time
            logger.info("=" * 80)
            logger.info(f"Pipeline completed successfully in {elapsed_time:.2f} seconds")
            logger.info("=" * 80)

            return True

        except Exception as e:
            logger.error(f"Pipeline failed: {e}", exc_info=True)
            return False

    def run_ingestion(self) -> bool:
        """Run ingestion stage.

        Returns:
            True if successful, False otherwise
        """
        logger.info("-" * 80)
        logger.info("STAGE 1: Data Ingestion (Bronze Layer)")
        logger.info("-" * 80)

        try:
            use_case = IngestMoviesUseCase(self.settings)
            use_case.execute()
            logger.info("✓ Ingestion completed")
            return True

        except Exception as e:
            logger.error(f"✗ Ingestion failed: {e}")
            return False

    def run_transformation(self) -> bool:
        """Run transformation stage.

        Returns:
            True if successful, False otherwise
        """
        logger.info("-" * 80)
        logger.info("STAGE 2: Data Transformation (Silver Layer)")
        logger.info("-" * 80)

        try:
            use_case = TransformMoviesUseCase(self.settings)
            stats = use_case.execute()
            logger.info(f"✓ Transformation completed: {stats}")
            return True

        except Exception as e:
            logger.error(f"✗ Transformation failed: {e}")
            return False

    def run_loading(self) -> bool:
        """Run loading stage.

        Returns:
            True if successful, False otherwise
        """
        logger.info("-" * 80)
        logger.info("STAGE 3: Analytics Loading (Gold Layer)")
        logger.info("-" * 80)

        try:
            use_case = LoadAnalyticsUseCase(self.settings)
            stats = use_case.execute()
            logger.info(f"✓ Loading completed: {stats}")
            return True

        except Exception as e:
            logger.error(f"✗ Loading failed: {e}")
            return False

    def run_stage(self, stage: str) -> bool:
        """Run a specific pipeline stage.

        Args:
            stage: Stage name ('ingestion', 'transformation', 'loading')

        Returns:
            True if successful, False otherwise
        """
        stage_map = {
            "ingestion": self.run_ingestion,
            "transformation": self.run_transformation,
            "loading": self.run_loading,
        }

        if stage not in stage_map:
            logger.error(f"Unknown stage: {stage}")
            logger.error(f"Available stages: {', '.join(stage_map.keys())}")
            return False

        return stage_map[stage]()

