"""Tests for quote ingestion behavior."""

from pathlib import Path

import pytest

from QuoteEngine import (
    Ingestor,
    InvalidQuoteFormatError,
    QuoteModel,
    TextIngestor,
    UnsupportedFileTypeError,
)


BASE_DIR = Path(__file__).resolve().parents[1]


def test_quote_model_string_representation():
    """QuoteModel prints in the Udacity-required format."""
    quote = QuoteModel("Readable code matters", "Devin")

    assert str(quote) == '"Readable code matters" - Devin'


def test_text_ingestor_parses_standard_lines(tmp_path):
    """TextIngestor turns valid text lines into QuoteModel objects."""
    quote_file = tmp_path / "quotes.txt"
    quote_file.write_text('"Line one" - Author One\n', encoding="utf-8")

    quotes = TextIngestor.parse(quote_file)

    assert len(quotes) == 1
    assert quotes[0].body == "Line one"
    assert quotes[0].author == "Author One"


def test_text_ingestor_rejects_bad_quote_format(tmp_path):
    """Invalid text lines fail with a human-readable custom exception."""
    quote_file = tmp_path / "quotes.txt"
    quote_file.write_text("missing author separator\n", encoding="utf-8")

    with pytest.raises(InvalidQuoteFormatError, match="Expected the format"):
        TextIngestor.parse(quote_file)


@pytest.mark.parametrize(
    "fixture_path,expected_count",
    [
        ("_data/SimpleLines/SimpleLines.csv", 5),
        ("_data/SimpleLines/SimpleLines.docx", 5),
        ("_data/SimpleLines/SimpleLines.pdf", 5),
        ("_data/DogQuotes/DogQuotesTXT.txt", 2),
    ],
)
def test_ingestor_parses_supported_fixture_types(fixture_path, expected_count):
    """The facade parses the CSV, DOCX, PDF, and TXT fixture formats."""
    quotes = Ingestor.parse(BASE_DIR / fixture_path)

    assert len(quotes) >= expected_count
    assert all(isinstance(quote, QuoteModel) for quote in quotes)


def test_ingestor_discovers_supported_files_in_directory(tmp_path):
    """Directory parsing uses os.walk to collect supported quote files."""
    nested = tmp_path / "nested"
    nested.mkdir()
    (tmp_path / "first.txt").write_text('"One" - A\n', encoding="utf-8")
    (nested / "second.txt").write_text('"Two" - B\n', encoding="utf-8")
    (nested / "ignore.md").write_text('"Nope" - C\n', encoding="utf-8")

    quotes = Ingestor.parse_directory(tmp_path)

    assert [quote.body for quote in quotes] == ["One", "Two"]


def test_ingestor_rejects_unsupported_file_type(tmp_path):
    """Unsupported files raise a custom exception."""
    unsupported = tmp_path / "quotes.md"
    unsupported.write_text('"Nope" - C\n', encoding="utf-8")

    with pytest.raises(UnsupportedFileTypeError):
        Ingestor.parse(unsupported)
