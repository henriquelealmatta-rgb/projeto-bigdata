"""Pipeline custom exceptions."""


class PipelineError(Exception):
    """Base exception for pipeline errors."""

    pass


class DataIngestionError(PipelineError):
    """Exception raised when data ingestion fails."""

    pass


class DataTransformationError(PipelineError):
    """Exception raised when data transformation fails."""

    pass


class DataLoadingError(PipelineError):
    """Exception raised when data loading fails."""

    pass


class DataValidationError(PipelineError):
    """Exception raised when data validation fails."""

    pass

