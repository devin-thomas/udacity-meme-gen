"""Tests for command-line meme generation helpers."""

from pathlib import Path

import pytest
from PIL import Image

from meme import generate_meme


def test_generate_meme_uses_custom_inputs(tmp_path, monkeypatch):
    """The CLI helper accepts caller-provided image, body, and author."""
    source = tmp_path / "custom.png"
    Image.new("RGB", (520, 360), color=(180, 210, 190)).save(source)
    monkeypatch.chdir(Path(__file__).resolve().parents[1])

    generated = Path(
        generate_meme(
            path=str(source),
            body="Tests keep the story honest",
            author="Devin",
        )
    )

    assert generated.exists()


def test_generate_meme_requires_author_with_body(tmp_path):
    """A custom body without an author is rejected clearly."""
    source = tmp_path / "custom.png"
    Image.new("RGB", (300, 300), color=(20, 30, 40)).save(source)

    with pytest.raises(ValueError, match="Author is required"):
        generate_meme(path=str(source), body="Missing author")
