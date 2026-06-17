import random
from argparse import ArgumentParser

from MemeEngine import MemeEngine
from QuoteEngine import QuoteModel
from meme_resources import BASE_DIR, load_images, load_quotes


def generate_meme(path=None, body=None, author=None):
    """Generate a meme from optional image and quote inputs."""
    if path is None:
        img = random.choice(load_images())
    else:
        img = path

    if body is None:
        quotes = load_quotes()
        quote = random.choice(quotes)
    else:
        if author is None:
            raise ValueError("Author is required when body is provided.")
        quote = QuoteModel(body, author)

    meme = MemeEngine(BASE_DIR / "tmp")
    return meme.make_meme(img, quote.body, quote.author)


def build_parser():
    """Build the command-line argument parser."""
    parser = ArgumentParser(
        description="Generate a captioned meme from an image and quote."
    )
    parser.add_argument("--path", help="Path to an image file.")
    parser.add_argument("--body", help="Quote body to place on the image.")
    parser.add_argument("--author", help="Quote author to place on the image.")
    return parser


def main():
    """Parse command-line arguments and print the generated meme path."""
    args = build_parser().parse_args()
    print(generate_meme(args.path, args.body, args.author))


if __name__ == "__main__":
    main()
