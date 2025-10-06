"""Movie domain entities."""

from datetime import date
from typing import List, Optional

from pydantic import BaseModel, Field, validator


class MovieGenre(BaseModel):
    """Movie genre entity."""

    id: int
    name: str


class ProductionCompany(BaseModel):
    """Production company entity."""

    id: int
    name: str


class Movie(BaseModel):
    """Movie entity representing core business data."""

    id: int
    title: str
    original_title: Optional[str] = None
    overview: Optional[str] = None
    tagline: Optional[str] = None
    release_date: Optional[date] = None
    budget: float = 0.0
    revenue: float = 0.0
    runtime: Optional[int] = None
    status: Optional[str] = None
    original_language: Optional[str] = None
    genres: List[MovieGenre] = Field(default_factory=list)
    production_companies: List[ProductionCompany] = Field(default_factory=list)
    popularity: float = 0.0
    vote_average: float = 0.0
    vote_count: int = 0

    @validator("budget", "revenue")
    def validate_positive_money(cls, v: float) -> float:
        """Validate that money values are non-negative."""
        if v < 0:
            return 0.0
        return v

    @validator("vote_average")
    def validate_vote_range(cls, v: float) -> float:
        """Validate vote average is in valid range."""
        if v < 0:
            return 0.0
        if v > 10:
            return 10.0
        return v

    @property
    def profit(self) -> float:
        """Calculate movie profit."""
        return self.revenue - self.budget

    @property
    def roi(self) -> Optional[float]:
        """Calculate return on investment percentage."""
        if self.budget > 0:
            return (self.profit / self.budget) * 100
        return None

    @property
    def has_financial_data(self) -> bool:
        """Check if movie has valid financial data."""
        return self.budget > 0 and self.revenue > 0


class MovieMetadata(BaseModel):
    """Movie metadata with extended information."""

    movie_id: int
    keywords: List[str] = Field(default_factory=list)
    cast: List[str] = Field(default_factory=list)
    crew: List[str] = Field(default_factory=list)
    homepage: Optional[str] = None
    imdb_id: Optional[str] = None


class MovieRating(BaseModel):
    """Movie rating entity."""

    movie_id: int
    user_id: int
    rating: float
    timestamp: int

    @validator("rating")
    def validate_rating(cls, v: float) -> float:
        """Validate rating is in valid range."""
        if v < 0.5:
            return 0.5
        if v > 5.0:
            return 5.0
        return v

