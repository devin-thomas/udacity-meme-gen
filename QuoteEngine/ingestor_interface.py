"""Abstract base class shared by file ingestors."""

from abc import ABC, abstractmethod
from pathlib import Path

from .exceptions import InvalidQuoteFormatError
from .quote_model import QuoteModel


class IngestorInterface(ABC):
    """Define the interface and shared parsing helpers for ingestors."""

    allowed_extensions = []

    @classmethod
    def can_ingest(cls, path):
        """Return True when this ingestor supports the file extension."""
        extension = Path(path).suffix.lower().lstrip(".")
        return extension in cls.allowed_extensions

    @classmethod
    def _parse_quote_line(cls, line):
        """Parse one line in the standard '"body" - author format."""
        cleaned = str(line).strip().strip("\ufeff").strip("\x0c").strip()
        if not cleaned:
            return None

        if " - " not in cleaned:
            raise InvalidQuoteFormatError(
                f'Could not parse quote line "{cleaned}". '
                'Expected the format "body" - author.'
            )

        body, author = cleaned.rsplit(" - ", 1)
        body = body.strip().strip('"').strip("'")
        author = author.strip()
        return QuoteModel(body, author)

    @classmethod
    def _quotes_from_lines(cls, lines):
        """Convert text lines into QuoteModel instances."""
        quotes = []
        for line in lines:
            quote = cls._parse_quote_line(line)
            if quote is not None:
                quotes.append(quote)
        return quotes

    @classmethod
    @abstractmethod
    def parse(cls, path):
        """Parse a file and return a list of QuoteModel objects."""
        raise NotImplementedError
