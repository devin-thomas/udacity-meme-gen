"""Tests for command-line meme generation helpers."""

from pathlib import Path

import pytest
from PIL import Image

import meme as meme_module
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


@pytest.mark.parametrize(
    ("body", "author"),
    [
        ("Missing author", None),
        (None, "Missing body"),
    ],
)
def test_generate_meme_requires_body_and_author_together(
    tmp_path,
    body,
    author,
):
    """Partial custom quote inputs are rejected clearly."""
    source = tmp_path / "custom.png"
    Image.new("RGB", (300, 300), color=(20, 30, 40)).save(source)

    with pytest.raises(ValueError, match="must be provided together"):
        generate_meme(path=str(source), body=body, author=author)


@pytest.mark.parametrize(
    "arguments",
    [
        ["--body", "Missing author"],
        ["--author", "Missing body"],
    ],
)
def test_main_prints_friendly_error_for_partial_quote(arguments, capsys):
    """Expected CLI mistakes produce parser errors instead of tracebacks."""
    with pytest.raises(SystemExit, match="2"):
        meme_module.main(arguments)

    captured = capsys.readouterr()
    assert "Body and author must be provided together" in captured.err
    assert "Traceback" not in captured.err


def test_main_converts_generation_value_error_to_parser_error(
    monkeypatch,
    capsys,
):
    """Image and caption validation errors stay concise at the CLI."""
    def reject_generation(*_args):
        raise ValueError("That image cannot be used.")

    monkeypatch.setattr(meme_module, "generate_meme", reject_generation)

    with pytest.raises(SystemExit, match="2"):
        meme_module.main([])

    captured = capsys.readouterr()
    assert "That image cannot be used" in captured.err
    assert "Traceback" not in captured.err
