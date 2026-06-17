"""Tests for the curated runtime quote and image pools."""

from pathlib import Path

from meme_resources import load_images, load_quotes


def test_runtime_images_only_use_starter_dog_photos():
    """Random generation never selects abstract portfolio backgrounds."""
    images = [Path(path) for path in load_images()]

    assert len(images) == 4
    assert {path.name for path in images} == {
        "xander_1.jpg",
        "xander_2.jpg",
        "xander_3.jpg",
        "xander_4.jpg",
    }
    assert all(path.parent.name == "dog" for path in images)


def test_runtime_quotes_are_unique_and_exclude_placeholders():
    """Sample SimpleLines remain fixtures rather than production content."""
    quotes = load_quotes()
    identities = [(quote.body, quote.author) for quote in quotes]

    assert len(identities) == len(set(identities))
    assert all(not body.startswith("Line ") for body, _ in identities)
    assert any(author == "Devin" for _, author in identities)
