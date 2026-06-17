"""Smoke tests for the Flask web interface."""

from pathlib import Path

import app as app_module


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
