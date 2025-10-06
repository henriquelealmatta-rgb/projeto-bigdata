"""Use case for loading analytics data."""

import logging
from typing import Any, Dict

import pandas as pd

from src.domain.exceptions import DataLoadingError
from src.infrastructure.config import Settings
from src.infrastructure.repositories import DataRepository

logger = logging.getLogger(__name__)


class LoadAnalyticsUseCase:
    """Use case for loading analytics data (Gold Layer)."""

    def __init__(self, settings: Settings):
        """Initialize use case.

        Args:
            settings: Application settings
        """
        self.settings = settings
        self.silver_repo = DataRepository(settings.silver_dir)
        self.gold_repo = DataRepository(settings.gold_dir)

    def execute(self) -> Dict[str, Any]:
        """Execute analytics loading.

        Creates aggregated analytics from silver layer and stores in gold layer.

        Returns:
            Dictionary with loading statistics

        Raises:
            DataLoadingError: If loading fails
        """
        try:
            logger.info("Starting analytics loading (Silver → Gold)")

            stats = {}

            # Load source data
            movies_df = self.silver_repo.read_parquet("movies")
            credits_df = self.silver_repo.read_parquet("credits")
            keywords_df = self.silver_repo.read_parquet("keywords")

            # Merge data
            logger.info("Merging datasets...")
            full_df = movies_df.merge(credits_df[["id", "cast_names", "director"]], on="id", how="left")
            full_df = full_df.merge(keywords_df[["id", "keyword_names"]], on="id", how="left")

            # Generate analytics
            logger.info("Generating yearly analytics...")
            yearly_stats = self._generate_yearly_stats(full_df)
            self.gold_repo.save_parquet(yearly_stats, "yearly_analytics")
            stats["yearly_analytics"] = {
                "rows": len(yearly_stats),
                "columns": len(yearly_stats.columns),
            }

            logger.info("Generating genre analytics...")
            genre_stats = self._generate_genre_stats(full_df)
            self.gold_repo.save_parquet(genre_stats, "genre_analytics")
            stats["genre_analytics"] = {
                "rows": len(genre_stats),
                "columns": len(genre_stats.columns),
            }

            logger.info("Generating top movies...")
            top_movies = self._generate_top_movies(full_df)
            self.gold_repo.save_parquet(top_movies, "top_movies")
            stats["top_movies"] = {"rows": len(top_movies), "columns": len(top_movies.columns)}

            logger.info("Generating director analytics...")
            director_stats = self._generate_director_stats(full_df)
            self.gold_repo.save_parquet(director_stats, "director_analytics")
            stats["director_analytics"] = {
                "rows": len(director_stats),
                "columns": len(director_stats.columns),
            }

            # Save full enriched dataset
            logger.info("Saving full enriched dataset...")
            self.gold_repo.save_parquet(full_df, "movies_enriched")
            stats["movies_enriched"] = {"rows": len(full_df), "columns": len(full_df.columns)}

            logger.info("Analytics loading completed successfully")
            logger.info(f"Loading statistics: {stats}")

            return stats

        except Exception as e:
            logger.error(f"Analytics loading failed: {e}")
            raise DataLoadingError(f"Failed to load analytics: {e}")

    def _generate_yearly_stats(self, df: pd.DataFrame) -> pd.DataFrame:
        """Generate yearly statistics.

        Args:
            df: Full movies dataframe

        Returns:
            Yearly statistics dataframe
        """
        yearly = (
            df[df["release_year"].notna()]
            .groupby("release_year")
            .agg(
                movie_count=("id", "count"),
                avg_budget=("budget", "mean"),
                total_budget=("budget", "sum"),
                avg_revenue=("revenue", "mean"),
                total_revenue=("revenue", "sum"),
                avg_profit=("profit", "mean"),
                total_profit=("profit", "sum"),
                avg_rating=("vote_average", "mean"),
                avg_popularity=("popularity", "mean"),
                avg_runtime=("runtime", "mean"),
            )
            .reset_index()
        )

        yearly = yearly[yearly["release_year"] >= 1900]
        yearly = yearly.sort_values("release_year")

        return yearly

    def _generate_genre_stats(self, df: pd.DataFrame) -> pd.DataFrame:
        """Generate genre statistics.

        Args:
            df: Full movies dataframe

        Returns:
            Genre statistics dataframe
        """
        # Explode genres
        df_exploded = df.explode("genre_names")
        df_exploded = df_exploded[df_exploded["genre_names"].notna()]

        genre_stats = (
            df_exploded.groupby("genre_names")
            .agg(
                movie_count=("id", "count"),
                avg_budget=("budget", "mean"),
                total_revenue=("revenue", "sum"),
                avg_revenue=("revenue", "mean"),
                avg_profit=("profit", "mean"),
                avg_rating=("vote_average", "mean"),
                avg_popularity=("popularity", "mean"),
                avg_runtime=("runtime", "mean"),
            )
            .reset_index()
        )

        genre_stats = genre_stats.sort_values("movie_count", ascending=False)

        return genre_stats

    def _generate_top_movies(self, df: pd.DataFrame) -> pd.DataFrame:
        """Generate top movies list.

        Args:
            df: Full movies dataframe

        Returns:
            Top movies dataframe
        """
        # Top by revenue
        top_revenue = df.nlargest(100, "revenue")[
            [
                "id",
                "title",
                "release_year",
                "revenue",
                "budget",
                "profit",
                "roi",
                "vote_average",
                "vote_count",
                "genre_names",
                "director",
            ]
        ].copy()
        top_revenue["rank_type"] = "revenue"
        top_revenue["rank"] = range(1, len(top_revenue) + 1)

        # Top by profit
        top_profit = df.nlargest(100, "profit")[
            [
                "id",
                "title",
                "release_year",
                "revenue",
                "budget",
                "profit",
                "roi",
                "vote_average",
                "vote_count",
                "genre_names",
                "director",
            ]
        ].copy()
        top_profit["rank_type"] = "profit"
        top_profit["rank"] = range(1, len(top_profit) + 1)

        # Top by rating (with minimum vote threshold)
        top_rating = df[df["vote_count"] >= 100].nlargest(100, "vote_average")[
            [
                "id",
                "title",
                "release_year",
                "revenue",
                "budget",
                "profit",
                "roi",
                "vote_average",
                "vote_count",
                "genre_names",
                "director",
            ]
        ].copy()
        top_rating["rank_type"] = "rating"
        top_rating["rank"] = range(1, len(top_rating) + 1)

        # Combine all rankings
        top_movies = pd.concat([top_revenue, top_profit, top_rating], ignore_index=True)

        return top_movies

    def _generate_director_stats(self, df: pd.DataFrame) -> pd.DataFrame:
        """Generate director statistics.

        Args:
            df: Full movies dataframe

        Returns:
            Director statistics dataframe
        """
        director_stats = (
            df[df["director"].notna()]
            .groupby("director")
            .agg(
                movie_count=("id", "count"),
                avg_budget=("budget", "mean"),
                total_revenue=("revenue", "sum"),
                avg_revenue=("revenue", "mean"),
                total_profit=("profit", "sum"),
                avg_profit=("profit", "mean"),
                avg_rating=("vote_average", "mean"),
                avg_popularity=("popularity", "mean"),
            )
            .reset_index()
        )

        # Filter directors with at least 3 movies
        director_stats = director_stats[director_stats["movie_count"] >= 3]
        director_stats = director_stats.sort_values("total_revenue", ascending=False)

        return director_stats

