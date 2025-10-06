"""Data repository for file operations."""

import logging
from pathlib import Path
from typing import List, Optional

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from src.domain.exceptions import DataLoadingError

logger = logging.getLogger(__name__)


class DataRepository:
    """Repository for data storage operations."""

    def __init__(self, base_path: Path):
        """Initialize data repository.

        Args:
            base_path: Base directory for data storage
        """
        self.base_path = base_path
        self.base_path.mkdir(parents=True, exist_ok=True)

    def save_parquet(
        self, df: pd.DataFrame, filename: str, partition_cols: Optional[List[str]] = None
    ) -> Path:
        """Save DataFrame as Parquet file.

        Args:
            df: DataFrame to save
            filename: Name of the file (without extension)
            partition_cols: Columns to use for partitioning

        Returns:
            Path to saved file

        Raises:
            DataLoadingError: If save fails
        """
        try:
            filepath = self.base_path / f"{filename}.parquet"

            logger.info(f"Saving Parquet file to {filepath}")
            logger.info(f"DataFrame shape: {df.shape}")

            table = pa.Table.from_pandas(df)

            if partition_cols:
                pq.write_to_dataset(
                    table,
                    root_path=str(self.base_path / filename),
                    partition_cols=partition_cols,
                )
            else:
                pq.write_table(table, str(filepath), compression="snappy")

            logger.info(f"Successfully saved Parquet file: {filepath}")

            return filepath

        except Exception as e:
            raise DataLoadingError(f"Failed to save Parquet file: {e}")

    def read_parquet(self, filename: str) -> pd.DataFrame:
        """Read Parquet file into DataFrame.

        Args:
            filename: Name of the file (with or without extension)

        Returns:
            Loaded DataFrame

        Raises:
            DataLoadingError: If read fails
        """
        try:
            if not filename.endswith(".parquet"):
                filename = f"{filename}.parquet"

            filepath = self.base_path / filename

            logger.info(f"Reading Parquet file from {filepath}")

            df = pd.read_parquet(filepath)

            logger.info(f"Successfully loaded DataFrame with shape: {df.shape}")

            return df

        except Exception as e:
            raise DataLoadingError(f"Failed to read Parquet file: {e}")

    def save_csv(self, df: pd.DataFrame, filename: str) -> Path:
        """Save DataFrame as CSV file.

        Args:
            df: DataFrame to save
            filename: Name of the file (without extension)

        Returns:
            Path to saved file

        Raises:
            DataLoadingError: If save fails
        """
        try:
            filepath = self.base_path / f"{filename}.csv"

            logger.info(f"Saving CSV file to {filepath}")

            df.to_csv(filepath, index=False)

            logger.info(f"Successfully saved CSV file: {filepath}")

            return filepath

        except Exception as e:
            raise DataLoadingError(f"Failed to save CSV file: {e}")

    def read_csv(self, filename: str) -> pd.DataFrame:
        """Read CSV file into DataFrame.

        Args:
            filename: Name of the file (with or without extension)

        Returns:
            Loaded DataFrame

        Raises:
            DataLoadingError: If read fails
        """
        try:
            if not filename.endswith(".csv"):
                filename = f"{filename}.csv"

            filepath = self.base_path / filename

            logger.info(f"Reading CSV file from {filepath}")

            df = pd.read_csv(filepath)

            logger.info(f"Successfully loaded DataFrame with shape: {df.shape}")

            return df

        except Exception as e:
            raise DataLoadingError(f"Failed to read CSV file: {e}")

    def list_files(self, pattern: str = "*") -> List[Path]:
        """List files in the repository.

        Args:
            pattern: Glob pattern for file matching

        Returns:
            List of file paths
        """
        return list(self.base_path.glob(pattern))

