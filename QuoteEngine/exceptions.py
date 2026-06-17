"""Custom exceptions for quote ingestion."""


class QuoteEngineError(Exception):
    """Base exception for quote ingestion failures."""


class UnsupportedFileTypeError(QuoteEngineError):
    """Raised when no ingestor supports the requested file type."""


class InvalidQuoteFormatError(QuoteEngineError):
    """Raised when a quote line cannot be split into body and author."""


class MissingDependencyError(QuoteEngineError):
    """Raised when an optional parser dependency is not available."""
