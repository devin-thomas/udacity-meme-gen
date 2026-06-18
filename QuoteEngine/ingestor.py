"""Facade that selects the right quote ingestor for a file."""

import os
from pathlib import Path

from .csv_ingestor import CSVIngestor
from .docx_ingestor import DocxIngestor
from .exceptions import UnsupportedFileTypeError
from .ingestor_interface import IngestorInterface
from .pdf_ingestor import PDFIngestor
from .quote_model import QuoteModel
from .text_ingestor import TextIngestor


class Ingestor(IngestorInterface):
    """Parse quotes from every supported source format."""

    ingestors = [CSVIngestor, DocxIngestor, PDFIngestor, TextIngestor]
    _ingestors_by_extension = {
        extension: ingestor
        for ingestor in ingestors
        for extension in ingestor.allowed_extensions
    }

    @classmethod
    def parse(cls, path) -> list[QuoteModel]:
        """Parse a supported file using the matching strategy object."""
        extension = Path(path).suffix.lower().lstrip(".")
        ingestor = cls._ingestors_by_extension.get(extension)
        if ingestor is not None:
            return ingestor.parse(path)
        raise UnsupportedFileTypeError(
            f"No quote ingestor supports {Path(path).suffix or path}."
        )

    @classmethod
    def parse_directory(cls, directory) -> list[QuoteModel]:
        """Discover and parse every supported quote file in a directory."""
        root_path = Path(directory)
        if not root_path.exists():
            raise FileNotFoundError(
                f"Quote directory does not exist: {directory}"
            )

        quotes = []
        for root, _, files in os.walk(root_path):
            for name in sorted(files):
                path = Path(root) / name
                extension = path.suffix.lower().lstrip(".")
                if extension in cls._ingestors_by_extension:
                    quotes.extend(cls.parse(path))
        return quotes
