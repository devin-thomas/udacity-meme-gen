"""Data model for a parsed quote."""

from dataclasses import dataclass

from .exceptions import InvalidQuoteFormatError


@dataclass(frozen=True, repr=False)
class QuoteModel:
    """Represent a quote body and its author."""

    body: str
    author: str

    def __post_init__(self):
        """Normalize and validate quote fields after initialization."""
        body = str(self.body).strip()
        author = str(self.author).strip()

        if not body:
            raise InvalidQuoteFormatError("Quote body cannot be empty.")
        if not author:
            raise InvalidQuoteFormatError("Quote author cannot be empty.")

        object.__setattr__(self, "body", body)
        object.__setattr__(self, "author", author)

    def __repr__(self):
        """Return the required printable quote representation."""
        return f'"{self.body}" - {self.author}'

    def __str__(self):
        """Match the repr output for human-friendly printing."""
        return f'"{self.body}" - {self.author}'
