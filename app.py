import random
import tempfile
from pathlib import Path
from urllib.parse import urlparse

import requests
from flask import Flask, abort, render_template, request, url_for
from werkzeug.exceptions import HTTPException

from MemeEngine import MemeEngine
from meme_resources import BASE_DIR, load_images, load_quotes

app = Flask(__name__)

STATIC_DIR = BASE_DIR / "static"
TEMP_DIR = BASE_DIR / "tmp"
meme = MemeEngine(STATIC_DIR / "generated")


def setup():
    """Load quote and image resources for the Flask app."""
    return load_quotes(), load_images()


quotes, imgs = setup()


@app.route('/')
def meme_rand():
    """Generate a random meme."""
    img = random.choice(imgs)
    quote = random.choice(quotes)
    path = meme.make_meme(img, quote.body, quote.author)
    return render_template("meme.html", path=_static_url(path))


@app.route('/create', methods=['GET'])
def meme_form():
    """Render the custom meme form."""
    return render_template("meme_form.html")


@app.route('/create', methods=['POST'])
def meme_post():
    """Create a user-defined meme from a submitted image URL."""
    image_url = request.form.get("image_url", "").strip()
    body = request.form.get("body", "").strip()
    author = request.form.get("author", "").strip()
    if not image_url or not body or not author:
        abort(
            400,
            description="Image URL, quote body, and author are required.",
        )

    temp_path = None
    try:
        temp_path = _download_image(image_url)
        path = meme.make_meme(temp_path, body, author)
    except HTTPException:
        raise
    except requests.RequestException as exc:
        abort(400, description=f"Unable to download image: {exc}")
    except (OSError, ValueError) as exc:
        abort(400, description=str(exc))
    finally:
        if temp_path:
            Path(temp_path).unlink(missing_ok=True)

    return render_template("meme.html", path=_static_url(path))


@app.route("/health")
def health():
    """Return a lightweight health response for deployment checks."""
    return {"status": "ok", "quotes": len(quotes), "images": len(imgs)}


def _download_image(image_url):
    """Download a user image URL to a temporary local file."""
    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    suffix = Path(urlparse(image_url).path).suffix.lower()
    if suffix not in {".jpg", ".jpeg", ".png"}:
        suffix = ".jpg"

    response = requests.get(image_url, stream=True, timeout=10)
    response.raise_for_status()
    content_type = response.headers.get("content-type", "").lower()
    if content_type and not content_type.startswith("image/"):
        abort(400, description="The submitted URL did not return an image.")

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=suffix,
        dir=TEMP_DIR,
    ) as outfile:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                outfile.write(chunk)
        return outfile.name


def _static_url(path):
    """Convert a generated static file path into a Flask static URL."""
    generated = Path(path).resolve()
    try:
        relative = generated.relative_to(STATIC_DIR.resolve())
    except ValueError:
        return str(path)
    return url_for("static", filename=relative.as_posix())


if __name__ == "__main__":
    app.run()
