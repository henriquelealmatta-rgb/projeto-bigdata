"""Use case for transforming movies dataset."""

import ast
import logging
from typing import Any, Dict, List

import pandas as pd

from src.domain.exceptions import DataTransformationError
from src.infrastructure.config import Settings
from src.infrastructure.repositories import DataRepository

logger = logging.getLogger(__name__)


class TransformMoviesUseCase:
    """Use case for transforming movies data (Silver Layer)."""

    def __init__(self, settings: Settings):
        """Initialize use case.

        Args:
            settings: Application settings
        """
        self.settings = settings
        self.bronze_repo = DataRepository(settings.bronze_dir)
        self.silver_repo = DataRepository(settings.silver_dir)

    def execute(self) -> Dict[str, Any]:
        """Execute data transformation.

        Transforms raw data from bronze layer to cleaned data in silver layer.

        Returns:
            Dictionary with transformation statistics

        Raises:
            DataTransformationError: If transformation fails
        """
        try:
            logger.info("Starting data transformation (Bronze → Silver)")

            stats = {}

            # Transform movies metadata
            logger.info("Transforming movies_metadata.csv...")
            movies_df = self._transform_movies()
            self.silver_repo.save_parquet(movies_df, "movies")
            stats["movies"] = {"rows": len(movies_df), "columns": len(movies_df.columns)}

            # Transform credits
            logger.info("Transforming credits.csv...")
            credits_df = self._transform_credits()
            self.silver_repo.save_parquet(credits_df, "credits")
            stats["credits"] = {"rows": len(credits_df), "columns": len(credits_df.columns)}

            # Transform keywords
            logger.info("Transforming keywords.csv...")
            keywords_df = self._transform_keywords()
            self.silver_repo.save_parquet(keywords_df, "keywords")
            stats["keywords"] = {"rows": len(keywords_df), "columns": len(keywords_df.columns)}

            # Transform ratings (if exists)
            try:
                logger.info("Transforming ratings_small.csv...")
                ratings_df = self._transform_ratings()
                self.silver_repo.save_parquet(ratings_df, "ratings")
                stats["ratings"] = {
                    "rows": len(ratings_df),
                    "columns": len(ratings_df.columns),
                }
            except FileNotFoundError:
                logger.warning("ratings_small.csv not found, skipping...")

            logger.info("Data transformation completed successfully")
            logger.info(f"Transformation statistics: {stats}")

            return stats

        except Exception as e:
            logger.error(f"Data transformation failed: {e}")
            raise DataTransformationError(f"Failed to transform data: {e}")

    def _transform_movies(self) -> pd.DataFrame:
        """Transform movies metadata."""
        df = self.bronze_repo.read_csv("movies_metadata")

        # Remove rows with invalid IDs
        df = df[df["id"].notna()]
        df["id"] = pd.to_numeric(df["id"], errors="coerce")
        df = df.dropna(subset=["id"])
        df["id"] = df["id"].astype(int)

        # Parse JSON columns
        df["genres"] = df["genres"].apply(self._safe_parse_json)
        df["production_companies"] = df["production_companies"].apply(self._safe_parse_json)
        df["production_countries"] = df["production_countries"].apply(self._safe_parse_json)
        df["spoken_languages"] = df["spoken_languages"].apply(self._safe_parse_json)

        # Extract genre names
        df["genre_names"] = df["genres"].apply(
            lambda x: [g["name"] for g in x if isinstance(g, dict) and "name" in g]
            if isinstance(x, list)
            else []
        )

        # Clean financial data
        df["budget"] = pd.to_numeric(df["budget"], errors="coerce").fillna(0)
        df["revenue"] = pd.to_numeric(df["revenue"], errors="coerce").fillna(0)

        # Clean dates
        df["release_date"] = pd.to_datetime(df["release_date"], errors="coerce")
        df["release_year"] = df["release_date"].dt.year

        # Clean numeric columns
        df["runtime"] = pd.to_numeric(df["runtime"], errors="coerce")
        df["popularity"] = pd.to_numeric(df["popularity"], errors="coerce").fillna(0)
        df["vote_average"] = pd.to_numeric(df["vote_average"], errors="coerce").fillna(0)
        df["vote_count"] = pd.to_numeric(df["vote_count"], errors="coerce").fillna(0)

        # Calculate derived columns
        df["profit"] = df["revenue"] - df["budget"]
        df["has_budget"] = df["budget"] > 0
        df["has_revenue"] = df["revenue"] > 0
        df["roi"] = df.apply(
            lambda row: (row["profit"] / row["budget"] * 100) if row["budget"] > 0 else None,
            axis=1,
        )

        # Filter valid movies
        df = df[df["title"].notna()]
        df = df[df["status"].notna()]

        logger.info(f"Transformed {len(df)} movies")

        return df

    def _transform_credits(self) -> pd.DataFrame:
        """Transform credits data."""
        df = self.bronze_repo.read_csv("credits")

        # Clean IDs
        df["id"] = pd.to_numeric(df["id"], errors="coerce")
        df = df.dropna(subset=["id"])
        df["id"] = df["id"].astype(int)

        # Parse JSON columns
        df["cast"] = df["cast"].apply(self._safe_parse_json)
        df["crew"] = df["crew"].apply(self._safe_parse_json)

        # Extract cast names (top 10)
        df["cast_names"] = df["cast"].apply(
            lambda x: [c["name"] for c in x[:10] if isinstance(c, dict) and "name" in c]
            if isinstance(x, list)
            else []
        )

        # Extract director
        df["director"] = df["crew"].apply(
            lambda x: next(
                (c["name"] for c in x if isinstance(c, dict) and c.get("job") == "Director"),
                None,
            )
            if isinstance(x, list)
            else None
        )

        logger.info(f"Transformed {len(df)} credit records")

        return df

    def _transform_keywords(self) -> pd.DataFrame:
        """Transform keywords data."""
        df = self.bronze_repo.read_csv("keywords")

        # Clean IDs
        df["id"] = pd.to_numeric(df["id"], errors="coerce")
        df = df.dropna(subset=["id"])
        df["id"] = df["id"].astype(int)

        # Parse keywords
        df["keywords"] = df["keywords"].apply(self._safe_parse_json)
        df["keyword_names"] = df["keywords"].apply(
            lambda x: [k["name"] for k in x if isinstance(k, dict) and "name" in k]
            if isinstance(x, list)
            else []
        )

        logger.info(f"Transformed {len(df)} keyword records")

        return df

    def _transform_ratings(self) -> pd.DataFrame:
        """Transform ratings data."""
        df = self.bronze_repo.read_csv("ratings_small")

        # Clean and validate
        df = df.dropna()
        df["userId"] = df["userId"].astype(int)
        df["movieId"] = df["movieId"].astype(int)
        df["rating"] = df["rating"].astype(float)
        df["timestamp"] = df["timestamp"].astype(int)

        # Validate rating range
        df = df[(df["rating"] >= 0.5) & (df["rating"] <= 5.0)]

        logger.info(f"Transformed {len(df)} rating records")

        return df

    @staticmethod
    def _safe_parse_json(value: Any) -> Any:
        """Safely parse JSON string.

        Args:
            value: Value to parse

        Returns:
            Parsed value or empty list
        """
        if pd.isna(value):
            return []

        if isinstance(value, str):
            try:
                return ast.literal_eval(value)
            except (ValueError, SyntaxError):
                return []

        return value

