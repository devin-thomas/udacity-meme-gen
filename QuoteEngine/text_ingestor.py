"""Text file quote ingestor."""

from .exceptions import UnsupportedFileTypeError
from .ingestor_interface import IngestorInterface


class TextIngestor(IngestorInterface):
    """Load quotes from plain text files."""

    allowed_extensions = ["txt"]

    @classmethod
    def parse(cls, path):
        """Parse a text file into QuoteModel objects."""
        if not cls.can_ingest(path):
            raise UnsupportedFileTypeError(
                f"TextIngestor cannot parse {path}."
            )

        with open(path, "r", encoding="utf-8-sig") as infile:
            return cls._quotes_from_lines(infile.readlines())
