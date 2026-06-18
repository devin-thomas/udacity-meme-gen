"""Smoke tests for the Flask web interface."""

from pathlib import Path

import pytest
from werkzeug.exceptions import RequestEntityTooLarge

import app as app_module


class StubImageResponse:
    """Provide the requests.Response behavior used by image downloads."""

    def __init__(self, chunks, headers=None):
        self.chunks = chunks
        self.headers = headers or {"content-type": "image/png"}
        self.closed = False

    def raise_for_status(self):
        """Represent a successful remote response."""

    def iter_content(self, chunk_size):
        """Yield configured bytes as a streamed response body."""
        assert chunk_size == 8192
        yield from self.chunks

    def close(self):
        """Record that the download response was released."""
        self.closed = True


def test_random_route_uses_curated_content(monkeypatch):
    """The home page generates from dog photos and non-placeholder quotes."""
    generated_inputs = {}

    def capture_meme(image_path, body, author):
        generated_inputs.update(
            image_path=image_path,
            body=body,
            author=author,
        )
        return app_module.STATIC_DIR / "generated" / "test-meme.jpg"

    monkeypatch.setattr(app_module.meme, "make_meme", capture_meme)

    response = app_module.app.test_client().get("/")

    assert response.status_code == 200
    assert b"Generated meme" in response.data
    assert Path(generated_inputs["image_path"]).parent.name == "dog"
    assert not generated_inputs["body"].startswith("Line ")


def test_creator_form_renders():
    """The custom meme form remains available after the quality repair."""
    response = app_module.app.test_client().get("/create")

    assert response.status_code == 200
    assert b"Image URL" in response.data
    assert b"Quote Body" in response.data
    assert b"Quote Author" in response.data


def test_creator_post_downloads_remote_image_without_live_network(
    monkeypatch,
):
    """The POST route streams, uses, and removes a mocked remote image."""
    response = StubImageResponse([b"fake-image-bytes"])
    generated_inputs = {}

    monkeypatch.setattr(
        app_module.requests,
        "get",
        lambda *args, **kwargs: response,
    )

    def capture_meme(image_path, body, author):
        generated_inputs.update(
            image_path=image_path,
            image_bytes=Path(image_path).read_bytes(),
            body=body,
            author=author,
        )
        return app_module.STATIC_DIR / "generated" / "posted-meme.jpg"

    monkeypatch.setattr(app_module.meme, "make_meme", capture_meme)

    result = app_module.app.test_client().post(
        "/create",
        data={
            "image_url": "https://example.test/photo.png",
            "body": "Mock the network",
            "author": "Devin",
        },
    )

    assert result.status_code == 200
    assert generated_inputs["image_bytes"] == b"fake-image-bytes"
    assert generated_inputs["body"] == "Mock the network"
    assert generated_inputs["author"] == "Devin"
    assert not Path(generated_inputs["image_path"]).exists()
    assert response.closed


def test_download_rejects_stream_over_size_limit(monkeypatch):
    """Remote streams are stopped and cleaned up at the configured limit."""
    response = StubImageResponse([b"1234", b"5678"])
    monkeypatch.setitem(app_module.app.config, "MAX_REMOTE_IMAGE_BYTES", 6)
    monkeypatch.setattr(
        app_module.requests,
        "get",
        lambda *args, **kwargs: response,
    )

    with pytest.raises(RequestEntityTooLarge, match="too large"):
        app_module._download_image("https://example.test/photo.png")

    assert response.closed
