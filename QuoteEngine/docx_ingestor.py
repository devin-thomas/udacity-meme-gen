"""DOCX quote ingestor backed by python-docx."""

from .exceptions import (
    MissingDependencyError,
    UnsupportedFileTypeError,
)
from .ingestor_interface import IngestorInterface
from .quote_model import QuoteModel


class DocxIngestor(IngestorInterface):
    """Parse .docx quote files with python-docx."""

    allowed_extensions = ["docx"]

    @classmethod
    def parse(cls, path) -> list[QuoteModel]:
        """Parse a DOCX file into QuoteModel objects."""
        if not cls.can_ingest(path):
            raise UnsupportedFileTypeError(
                f"DocxIngestor cannot parse {path}."
            )

        try:
            from docx import Document
        except ImportError as exc:
            raise MissingDependencyError(
                "python-docx is required to parse DOCX quote files."
            ) from exc

        document = Document(path)
        lines = [
            paragraph.text
            for paragraph in document.paragraphs
            if paragraph.text.strip()
        ]
        return cls._quotes_from_lines(lines)
