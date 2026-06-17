"""Tests for image caption generation."""

from pathlib import Path

import pytest
from PIL import Image, ImageDraw

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


@pytest.mark.parametrize(
    ("size", "body", "author"),
    [
        ((500, 500), "Short and readable", "Devin"),
        (
            (500, 500),
            "Readable output matters " * 10,
            "A careful author with a longer name",
        ),
        ((220, 160), "A narrow image still works", "Devin"),
    ],
)
def test_caption_layout_stays_inside_image(size, body, author):
    """Measured caption boxes remain fully inside varied image sizes."""
    image = Image.new("RGB", size, color=(210, 220, 225))

    layout = MemeEngine._build_caption_layout(image, body.strip(), author)

    left, top, right, bottom = layout.background_box
    assert 0 <= left < right <= image.width
    assert 0 <= top < bottom <= image.height


def test_caption_prefers_quiet_region_over_busy_center():
    """The placement scorer avoids a visually noisy central subject area."""
    image = Image.new("RGB", (500, 500), color=(230, 235, 238))
    draw = ImageDraw.Draw(image)
    for coordinate in range(100, 401, 10):
        draw.line((100, coordinate, 400, coordinate), fill=(20, 30, 40), width=5)
        draw.line((coordinate, 100, coordinate, 400), fill=(170, 30, 40), width=5)

    layout = MemeEngine._build_caption_layout(
        image,
        "Use the quiet space",
        "Devin",
    )

    left, top, right, bottom = layout.background_box
    center_x = (left + right) / 2
    center_y = (top + bottom) / 2
    assert not (125 <= center_x <= 375 and 100 <= center_y <= 400)


def test_make_meme_rejects_excessively_long_text(tmp_path):
    """Unrenderable custom text fails with a useful validation message."""
    source = tmp_path / "source.png"
    Image.new("RGB", (500, 500), color=(42, 118, 142)).save(source)
    engine = MemeEngine(tmp_path / "out")

    with pytest.raises(ValueError, match="cannot exceed 280 characters"):
        engine.make_meme(source, "x" * 281, "Devin")
