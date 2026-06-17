"""Quote parsing strategies for the meme generator."""

from .exceptions import (
    InvalidQuoteFormatError,
    MissingDependencyError,
    QuoteEngineError,
    UnsupportedFileTypeError,
)
from .csv_ingestor import CSVIngestor
from .docx_ingestor import DocxIngestor
from .ingestor import Ingestor
from .ingestor_interface import IngestorInterface
from .pdf_ingestor import PDFIngestor
from .quote_model import QuoteModel
from .text_ingestor import TextIngestor

__all__ = [
    "CSVIngestor",
    "DocxIngestor",
    "Ingestor",
    "IngestorInterface",
    "InvalidQuoteFormatError",
    "MissingDependencyError",
    "PDFIngestor",
    "QuoteEngineError",
    "QuoteModel",
    "TextIngestor",
    "UnsupportedFileTypeError",
]
