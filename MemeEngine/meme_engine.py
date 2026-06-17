"""Meme image generation using Pillow."""

import random
import textwrap
import uuid
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps, UnidentifiedImageError


class MemeEngine:
    """Create captioned image files for the CLI and Flask app."""

    supported_extensions = {".jpg", ".jpeg", ".png"}

    def __init__(self, output_dir):
        """Create a meme engine that writes images to output_dir."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def make_meme(self, img_path, text, author, width=500):
        """Create a meme image and return the generated file path."""
        image_path = Path(img_path)
        if not image_path.exists():
            raise FileNotFoundError(f"Image file does not exist: {img_path}")
        if image_path.suffix.lower() not in self.supported_extensions:
            raise ValueError(
                "MemeEngine supports JPEG and PNG input files only."
            )
        if not str(text).strip() or not str(author).strip():
            raise ValueError("Both meme text and author are required.")
        if width <= 0:
            raise ValueError("Meme width must be greater than zero.")

        try:
            image = Image.open(image_path)
            image = ImageOps.exif_transpose(image).convert("RGB")
        except UnidentifiedImageError as exc:
            raise ValueError(f"Could not open image file: {img_path}") from exc

        image = self._resize_image(image, min(width, 500))
        image = self._draw_caption(image, str(text).strip(), str(author).strip())

        output_path = self.output_dir / f"meme_{uuid.uuid4().hex}.jpg"
        image.save(output_path, "JPEG", quality=92, optimize=True)
        return str(output_path)

    @staticmethod
    def _resize_image(image, max_width):
        """Resize an image while preserving the aspect ratio."""
        if image.width <= max_width:
            return image.copy()

        ratio = max_width / float(image.width)
        height = int(image.height * ratio)
        return image.resize((max_width, height), Image.Resampling.LANCZOS)

    @classmethod
    def _draw_caption(cls, image, body, author):
        """Draw a readable caption at a random location on an image."""
        caption = f'"{body}"\n- {author}'
        canvas = image.convert("RGBA")
        overlay = Image.new("RGBA", canvas.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(overlay)

        font = cls._best_font(canvas.width, caption)
        max_text_width = int(canvas.width * 0.86)
        lines = cls._wrap_text(caption, font, max_text_width)
        text_block = "\n".join(lines)
        bbox = draw.multiline_textbbox(
            (0, 0),
            text_block,
            font=font,
            spacing=6,
            stroke_width=2,
        )
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        margin = max(18, canvas.width // 22)
        x = cls._random_position(margin, canvas.width - text_width - margin)
        y = cls._random_position(margin, canvas.height - text_height - margin)

        padding = 10
        draw.rounded_rectangle(
            (
                x - padding,
                y - padding,
                x + text_width + padding,
                y + text_height + padding,
            ),
            radius=8,
            fill=(20, 24, 28, 165),
        )
        draw.multiline_text(
            (x, y),
            text_block,
            font=font,
            fill=(255, 255, 255, 255),
            spacing=6,
            stroke_width=2,
            stroke_fill=(0, 0, 0, 200),
        )
        return Image.alpha_composite(canvas, overlay).convert("RGB")

    @staticmethod
    def _best_font(width, caption):
        """Load a TrueType font when available, falling back gracefully."""
        base_size = max(20, min(34, width // 14))
        if len(caption) > 120:
            base_size = max(18, base_size - 6)

        candidates = [
            "C:/Windows/Fonts/arialbd.ttf",
            "C:/Windows/Fonts/arial.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/Library/Fonts/Arial.ttf",
        ]
        for font_path in candidates:
            if Path(font_path).exists():
                return ImageFont.truetype(font_path, base_size)
        return ImageFont.load_default()

    @staticmethod
    def _wrap_text(text, font, max_width):
        """Wrap text into lines that fit the meme image."""
        draw = ImageDraw.Draw(Image.new("RGB", (1, 1)))
        wrapped_lines = []
        for paragraph in text.splitlines():
            max_chars = max(12, int(max_width / max(font.size * 0.48, 1)))
            for line in textwrap.wrap(paragraph, width=max_chars):
                while draw.textlength(line, font=font) > max_width and max_chars > 8:
                    max_chars -= 2
                    pieces = textwrap.wrap(line, width=max_chars)
                    line = pieces[0]
                    wrapped_lines.extend(pieces[:-1])
                wrapped_lines.append(line)
        return wrapped_lines

    @staticmethod
    def _random_position(min_value, max_value):
        """Return a random coordinate without allowing negative bounds."""
        if max_value <= min_value:
            return min_value
        return random.randint(min_value, max_value)
