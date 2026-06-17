"""CSV quote ingestor backed by pandas."""

from .exceptions import MissingDependencyError, UnsupportedFileTypeError
from .ingestor_interface import IngestorInterface
from .quote_model import QuoteModel


class CSVIngestor(IngestorInterface):
    """Load quotes from CSV files with body and author columns."""

    allowed_extensions = ["csv"]

    @classmethod
    def parse(cls, path):
        """Parse a CSV file into QuoteModel objects."""
        if not cls.can_ingest(path):
            raise UnsupportedFileTypeError(f"CSVIngestor cannot parse {path}.")

        try:
            import pandas as pd
        except ImportError as exc:
            raise MissingDependencyError(
                "pandas is required to parse CSV quote files."
            ) from exc

        data = pd.read_csv(path)
        normalized_columns = {name.lower().strip(): name for name in data.columns}
        if "body" not in normalized_columns or "author" not in normalized_columns:
            raise ValueError(
                f"{path} must include 'body' and 'author' columns."
            )

        body_column = normalized_columns["body"]
        author_column = normalized_columns["author"]
        quotes = []
        for _, row in data.iterrows():
            body = row.get(body_column)
            author = row.get(author_column)
            if pd.isna(body) or pd.isna(author):
                continue
            quotes.append(QuoteModel(str(body), str(author)))
        return quotes
