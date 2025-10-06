"""Unit tests for domain entities."""

import pytest
from datetime import date

from src.domain.entities import Movie, MovieGenre, MovieRating


class TestMovieGenre:
    """Tests for MovieGenre entity."""

    def test_create_genre(self) -> None:
        """Test genre creation."""
        genre = MovieGenre(id=1, name="Action")
        assert genre.id == 1
        assert genre.name == "Action"


class TestMovie:
    """Tests for Movie entity."""

    def test_create_movie(self) -> None:
        """Test movie creation with required fields."""
        movie = Movie(
            id=1,
            title="Test Movie",
            budget=1000000,
            revenue=2000000,
        )
        assert movie.id == 1
        assert movie.title == "Test Movie"
        assert movie.budget == 1000000
        assert movie.revenue == 2000000

    def test_movie_profit_calculation(self) -> None:
        """Test profit calculation."""
        movie = Movie(
            id=1,
            title="Test Movie",
            budget=1000000,
            revenue=2000000,
        )
        assert movie.profit == 1000000

    def test_movie_roi_calculation(self) -> None:
        """Test ROI calculation."""
        movie = Movie(
            id=1,
            title="Test Movie",
            budget=1000000,
            revenue=2000000,
        )
        assert movie.roi == 100.0

    def test_movie_roi_zero_budget(self) -> None:
        """Test ROI calculation with zero budget."""
        movie = Movie(
            id=1,
            title="Test Movie",
            budget=0,
            revenue=2000000,
        )
        assert movie.roi is None

    def test_movie_has_financial_data(self) -> None:
        """Test financial data presence check."""
        movie_with_data = Movie(
            id=1,
            title="Test Movie",
            budget=1000000,
            revenue=2000000,
        )
        assert movie_with_data.has_financial_data is True

        movie_without_data = Movie(
            id=2,
            title="Test Movie 2",
            budget=0,
            revenue=0,
        )
        assert movie_without_data.has_financial_data is False

    def test_negative_budget_validation(self) -> None:
        """Test negative budget is converted to zero."""
        movie = Movie(
            id=1,
            title="Test Movie",
            budget=-1000,
            revenue=2000000,
        )
        assert movie.budget == 0

    def test_vote_average_range_validation(self) -> None:
        """Test vote average range validation."""
        movie = Movie(
            id=1,
            title="Test Movie",
            vote_average=15.0,  # Should be capped at 10
        )
        assert movie.vote_average == 10.0

        movie2 = Movie(
            id=2,
            title="Test Movie 2",
            vote_average=-5.0,  # Should be set to 0
        )
        assert movie2.vote_average == 0.0


class TestMovieRating:
    """Tests for MovieRating entity."""

    def test_create_rating(self) -> None:
        """Test rating creation."""
        rating = MovieRating(
            movie_id=1,
            user_id=100,
            rating=4.5,
            timestamp=1234567890,
        )
        assert rating.movie_id == 1
        assert rating.user_id == 100
        assert rating.rating == 4.5
        assert rating.timestamp == 1234567890

    def test_rating_validation(self) -> None:
        """Test rating range validation."""
        rating_high = MovieRating(
            movie_id=1,
            user_id=100,
            rating=10.0,  # Should be capped at 5.0
            timestamp=1234567890,
        )
        assert rating_high.rating == 5.0

        rating_low = MovieRating(
            movie_id=1,
            user_id=100,
            rating=0.0,  # Should be set to 0.5
            timestamp=1234567890,
        )
        assert rating_low.rating == 0.5

