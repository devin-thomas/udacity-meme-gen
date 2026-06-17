"""Facade that selects the right quote ingestor for a file."""

import os
from pathlib import Path

from .csv_ingestor import CSVIngestor
from .docx_ingestor import DocxIngestor
from .exceptions import UnsupportedFileTypeError
from .ingestor_interface import IngestorInterface
from .pdf_ingestor import PDFIngestor
from .text_ingestor import TextIngestor


class Ingestor(IngestorInterface):
    """Parse quotes from every supported source format."""

    ingestors = [CSVIngestor, DocxIngestor, PDFIngestor, TextIngestor]

    @classmethod
    def parse(cls, path):
        """Parse a supported file using the matching strategy object."""
        for ingestor in cls.ingestors:
            if ingestor.can_ingest(path):
                return ingestor.parse(path)
        raise UnsupportedFileTypeError(
            f"No quote ingestor supports {Path(path).suffix or path}."
        )

    @classmethod
    def parse_directory(cls, directory):
        """Discover and parse every supported quote file in a directory."""
        root_path = Path(directory)
        if not root_path.exists():
            raise FileNotFoundError(f"Quote directory does not exist: {directory}")

        quotes = []
        for root, _, files in os.walk(root_path):
            for name in sorted(files):
                path = Path(root) / name
                if any(ingestor.can_ingest(path) for ingestor in cls.ingestors):
                    quotes.extend(cls.parse(path))
        return quotes
