"""Meme image generation using Pillow."""

import random
import uuid
from dataclasses import dataclass
from pathlib import Path

from PIL import (
    Image,
    ImageDraw,
    ImageFilter,
    ImageFont,
    ImageOps,
    ImageStat,
    UnidentifiedImageError,
)


@dataclass(frozen=True)
class _CaptionLayout:
    """Store measured caption geometry before drawing it."""

    text: str
    font: object
    text_position: tuple[int, int]
    background_box: tuple[int, int, int, int]


class MemeEngine:
    """Create captioned image files for the CLI and Flask app."""

    supported_extensions = {".jpg", ".jpeg", ".png"}
    max_body_length = 280
    max_author_length = 80
    _padding = 10
    _stroke_width = 2
    _line_spacing = 6
    _minimum_font_size = 12

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
        body = str(text).strip()
        author_name = str(author).strip()
        if not body or not author_name:
            raise ValueError("Both meme text and author are required.")
        if len(body) > self.max_body_length:
            raise ValueError(
                f"Meme text cannot exceed {self.max_body_length} characters."
            )
        if len(author_name) > self.max_author_length:
            raise ValueError(
                f"Meme author cannot exceed {self.max_author_length} characters."
            )
        if width <= 0:
            raise ValueError("Meme width must be greater than zero.")

        try:
            image = Image.open(image_path)
            image = ImageOps.exif_transpose(image).convert("RGB")
        except UnidentifiedImageError as exc:
            raise ValueError(f"Could not open image file: {img_path}") from exc

        image = self._resize_image(image, min(width, 500))
        image = self._draw_caption(image, body, author_name)

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
        """Draw a fitted caption in a quiet, randomly selected image region."""
        canvas = image.convert("RGBA")
        overlay = Image.new("RGBA", canvas.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(overlay)
        layout = cls._build_caption_layout(image, body, author)

        draw.rounded_rectangle(
            layout.background_box,
            radius=8,
            fill=(20, 24, 28, 180),
        )
        draw.multiline_text(
            layout.text_position,
            layout.text,
            font=layout.font,
            fill=(255, 255, 255, 255),
            spacing=cls._line_spacing,
            stroke_width=cls._stroke_width,
            stroke_fill=(0, 0, 0, 200),
        )
        return Image.alpha_composite(canvas, overlay).convert("RGB")

    @classmethod
    def _build_caption_layout(cls, image, body, author):
        """Measure, fit, and position a caption without clipping."""
        caption = f'"{body}"\n- {author}'
        text_block, font, bbox = cls._fit_caption(image.size, caption)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        box_size = (
            text_width + (2 * cls._padding),
            text_height + (2 * cls._padding),
        )
        x, y = cls._choose_position(image, box_size)
        text_position = (
            x + cls._padding - bbox[0],
            y + cls._padding - bbox[1],
        )
        return _CaptionLayout(
            text=text_block,
            font=font,
            text_position=text_position,
            background_box=(x, y, x + box_size[0], y + box_size[1]),
        )

    @classmethod
    def _fit_caption(cls, image_size, caption):
        """Shrink and wrap a caption until it fits the target image."""
        width, height = image_size
        max_box_width = int(width * 0.86)
        max_box_height = int(height * 0.46)
        max_text_width = max_box_width - (2 * cls._padding)
        starting_size = max(
            cls._minimum_font_size,
            min(34, width // 14, height // 9),
        )
        measurement_draw = ImageDraw.Draw(Image.new("RGB", (1, 1)))

        for font_size in range(
            starting_size,
            cls._minimum_font_size - 1,
            -1,
        ):
            font = cls._load_font(font_size)
            lines = cls._wrap_text(caption, font, max_text_width)
            text_block = "\n".join(lines)
            bbox = measurement_draw.multiline_textbbox(
                (0, 0),
                text_block,
                font=font,
                spacing=cls._line_spacing,
                stroke_width=cls._stroke_width,
            )
            box_width = bbox[2] - bbox[0] + (2 * cls._padding)
            box_height = bbox[3] - bbox[1] + (2 * cls._padding)
            if box_width <= max_box_width and box_height <= max_box_height:
                return text_block, font, bbox

        raise ValueError(
            "The caption is too large to fit this image. "
            "Use a larger image or shorter text."
        )

    @staticmethod
    def _load_font(font_size):
        """Load a TrueType font when available, falling back gracefully."""
        candidates = [
            "C:/Windows/Fonts/arialbd.ttf",
            "C:/Windows/Fonts/arial.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/Library/Fonts/Arial.ttf",
        ]
        for font_path in candidates:
            if Path(font_path).exists():
                return ImageFont.truetype(font_path, font_size)
        return ImageFont.load_default(size=font_size)

    @classmethod
    def _wrap_text(cls, text, font, max_width):
        """Wrap text using measured pixel widths instead of estimates."""
        draw = ImageDraw.Draw(Image.new("RGB", (1, 1)))
        wrapped_lines = []
        for paragraph in text.splitlines():
            words = paragraph.split()
            if not words:
                wrapped_lines.append("")
                continue

            current_line = ""
            for word in words:
                candidate = f"{current_line} {word}".strip()
                if draw.textlength(candidate, font=font) <= max_width:
                    current_line = candidate
                    continue

                if current_line:
                    wrapped_lines.append(current_line)
                    current_line = ""

                if draw.textlength(word, font=font) <= max_width:
                    current_line = word
                    continue

                pieces = cls._split_long_word(word, font, max_width, draw)
                wrapped_lines.extend(pieces[:-1])
                current_line = pieces[-1]

            if current_line:
                wrapped_lines.append(current_line)
        return wrapped_lines

    @staticmethod
    def _split_long_word(word, font, max_width, draw):
        """Split an individual long token into measured chunks."""
        pieces = []
        current_piece = ""
        for character in word:
            candidate = current_piece + character
            if current_piece and draw.textlength(candidate, font=font) > max_width:
                pieces.append(current_piece)
                current_piece = character
            else:
                current_piece = candidate
        if current_piece:
            pieces.append(current_piece)
        return pieces

    @classmethod
    def _choose_position(cls, image, box_size):
        """Choose one of the quietest candidate regions with bounded jitter."""
        width, height = image.size
        box_width, box_height = box_size
        margin = max(8, min(18, min(width, height) // 18))
        max_x = max(margin, width - box_width - margin)
        max_y = max(margin, height - box_height - margin)
        x_positions = [margin, (width - box_width) // 2, max_x]
        y_positions = [margin, (height - box_height) // 2, max_y]
        candidates = list(dict.fromkeys(
            (max(margin, x), max(margin, y))
            for y in y_positions
            for x in x_positions
        ))
        ranked = sorted(
            candidates,
            key=lambda position: cls._region_score(
                image,
                (*position, box_width, box_height),
            ),
        )
        x, y = random.choice(ranked[:2])

        jitter_x = max(1, int(width * 0.025))
        jitter_y = max(1, int(height * 0.025))
        x = min(max_x, max(margin, x + random.randint(-jitter_x, jitter_x)))
        y = min(max_y, max(margin, y + random.randint(-jitter_y, jitter_y)))
        return x, y

    @staticmethod
    def _region_score(image, region):
        """Score visual detail and center overlap; lower scores are quieter."""
        x, y, width, height = region
        crop = image.crop((x, y, x + width, y + height))
        grayscale = ImageOps.grayscale(crop)
        standard_deviation = ImageStat.Stat(grayscale).stddev[0]
        edge_mean = ImageStat.Stat(
            grayscale.filter(ImageFilter.FIND_EDGES)
        ).mean[0]

        focus_box = (
            image.width * 0.25,
            image.height * 0.20,
            image.width * 0.75,
            image.height * 0.80,
        )
        overlap_width = max(
            0,
            min(x + width, focus_box[2]) - max(x, focus_box[0]),
        )
        overlap_height = max(
            0,
            min(y + height, focus_box[3]) - max(y, focus_box[1]),
        )
        overlap_ratio = (overlap_width * overlap_height) / (width * height)
        return standard_deviation + (edge_mean * 0.75) + (overlap_ratio * 90)
