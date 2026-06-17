"""Tests for image caption generation."""

from pathlib import Path

from PIL import Image

from MemeEngine import MemeEngine


def test_make_meme_creates_resized_captioned_image(tmp_path):
    """MemeEngine writes a generated JPEG no wider than 500px."""
    source = tmp_path / "source.png"
    Image.new("RGB", (900, 600), color=(42, 118, 142)).save(source)

    engine = MemeEngine(tmp_path / "out")
    generated_path = Path(
        engine.make_meme(source, "Readable code matters", "Devin")
    )

    assert generated_path.exists()
    assert generated_path.suffix == ".jpg"
    with Image.open(generated_path) as generated:
        assert generated.width == 500
        assert generated.height == 333
