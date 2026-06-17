"""PDF quote ingestor using the pdftotext CLI with a safe fallback."""

import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from .exceptions import MissingDependencyError, QuoteEngineError, UnsupportedFileTypeError
from .ingestor_interface import IngestorInterface
from .text_ingestor import TextIngestor


class PDFIngestor(IngestorInterface):
    """Load quotes from PDF files."""

    allowed_extensions = ["pdf"]

    @classmethod
    def parse(cls, path):
        """Parse a PDF file into QuoteModel objects."""
        if not cls.can_ingest(path):
            raise UnsupportedFileTypeError(f"PDFIngestor cannot parse {path}.")

        pdftotext = os.environ.get("PDFTOTEXT_PATH") or shutil.which("pdftotext")
        if pdftotext:
            return cls._parse_with_pdftotext(path, pdftotext)
        return cls._parse_with_pypdf(path)

    @classmethod
    def _parse_with_pdftotext(cls, path, executable):
        """Convert a PDF to text through a subprocess and parse the result."""
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".txt")
        temp_file_path = temp_file.name
        temp_file.close()

        try:
            subprocess.run(
                [executable, str(path), temp_file_path],
                check=True,
                capture_output=True,
                text=True,
            )
            return TextIngestor.parse(temp_file_path)
        except subprocess.CalledProcessError as exc:
            message = exc.stderr.strip() or exc.stdout.strip()
            raise QuoteEngineError(
                f"pdftotext failed while parsing {path}: {message}"
            ) from exc
        finally:
            Path(temp_file_path).unlink(missing_ok=True)

    @classmethod
    def _parse_with_pypdf(cls, path):
        """Parse PDFs when pdftotext is not installed locally."""
        try:
            from pypdf import PdfReader
        except ImportError as exc:
            raise MissingDependencyError(
                "PDF parsing needs the pdftotext CLI or the pypdf fallback. "
                "Install Xpdf or add pypdf to the virtual environment."
            ) from exc

        reader = PdfReader(str(path))
        lines = []
        for page in reader.pages:
            text = page.extract_text() or ""
            lines.extend(text.splitlines())
        return cls._quotes_from_lines(lines)
