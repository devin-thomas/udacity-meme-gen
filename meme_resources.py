"""Shared resource discovery for the CLI and Flask app."""

from pathlib import Path

from QuoteEngine import Ingestor

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "_data"
QUOTE_DIRECTORIES = [
    DATA_DIR / "DogQuotes",
    DATA_DIR / "PortfolioQuotes",
]
IMAGE_ROOT = DATA_DIR / "photos" / "dog"
SUPPORTED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png"}


def load_quotes(quote_directories=None):
    """Load all discoverable quote files from the configured directories."""
    directories = quote_directories or QUOTE_DIRECTORIES
    quotes = []
    seen = set()
    for directory in directories:
        if Path(directory).exists():
            for quote in Ingestor.parse_directory(directory):
                identity = (quote.body, quote.author)
                if identity not in seen:
                    quotes.append(quote)
                    seen.add(identity)

    if not quotes:
        raise RuntimeError("No quotes were found in the configured data folders.")
    return quotes


def load_images(image_root=None):
    """Return every supported image under the configured image root."""
    root = Path(image_root or IMAGE_ROOT)
    if not root.exists():
        raise FileNotFoundError(f"Image directory does not exist: {root}")

    images = [
        str(path)
        for path in sorted(root.rglob("*"))
        if path.suffix.lower() in SUPPORTED_IMAGE_EXTENSIONS
    ]
    if not images:
        raise RuntimeError("No JPEG or PNG source images were found.")
    return images
