import logging
from io import BytesIO
from pathlib import Path
from uuid import uuid4

from PIL import Image
from pillow_heif import register_heif_opener
from rembg import remove

register_heif_opener()

UPLOAD_DIR = Path("uploads")
ORIGINAL_DIR = UPLOAD_DIR / "original"
PROCESSED_DIR = UPLOAD_DIR / "processed"

ORIGINAL_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

ALLOWED_TYPES = ["image/jpeg", "image/png", "image/webp", "image/heic", "image/heif"]

MAX_IMAGE_DIMENSION = 1920

COMPRESSION_QUALITY = 85

logger = logging.getLogger(__name__)


def validate_file(content_type: str, content: bytes) -> None:
    """Validate file type and size. Raises ValueError on failure."""
    if content_type not in ALLOWED_TYPES:
        raise ValueError(f"Unsupported file type '{content_type}'. Allowed: JPG, PNG, WEBP, HEIC")

    if len(content) == 0:
        raise ValueError("File is empty")

    if len(content) > MAX_FILE_SIZE:
        raise ValueError(f"File too large ({len(content) / 1024 / 1024:.1f} MB). Maximum is {MAX_FILE_SIZE / 1024 / 1024} MB")


def validate_image(content: bytes) -> None:
    """Verify that the content is a valid image. Raises ValueError on failure."""
    try:
        Image.open(BytesIO(content)).verify()
    except Exception as e:
        raise ValueError(f"Invalid image file: {e}")


def compress_image(image: Image.Image, max_dimension: int = MAX_IMAGE_DIMENSION) -> Image.Image:
    """Resize image so the longest side doesn't exceed max_dimension (aspect ratio preserved)."""
    width, height = image.size
    if width <= max_dimension and height <= max_dimension:
        return image

    if width >= height:
        new_width = max_dimension
        new_height = int(height * (max_dimension / width))
    else:
        new_height = max_dimension
        new_width = int(width * (max_dimension / height))

    return image.resize((new_width, new_height), Image.LANCZOS)


def save_original(content: bytes, original_extension: str) -> tuple[Path, str]:
    """
    Save the original image after compression.
    Returns (saved_path, url_path).
    """
    image = Image.open(BytesIO(content))

    # Convert RGBA to RGB for JPEG saving
    if image.mode == "RGBA":
        image = image.convert("RGB")

    image = compress_image(image)

    filename = f"{uuid4()}.jpg"
    filepath = ORIGINAL_DIR / filename

    image.save(filepath, "JPEG", quality=COMPRESSION_QUALITY, optimize=True)

    logger.info(f"Saved compressed original: {filepath} ({image.size[0]}x{image.size[1]})")
    return filepath, f"/uploads/original/{filename}"


def save_processed(content: bytes) -> tuple[Path, str]:
    """
    Remove background, compress, and save the processed image as PNG.
    Returns (saved_path, url_path).
    """
    processed_content = remove(content)
    image = Image.open(BytesIO(processed_content))

    image = compress_image(image)

    filename = f"{uuid4()}.png"
    filepath = PROCESSED_DIR / filename

    image.save(filepath, "PNG", optimize=True)

    logger.info(f"Saved processed image: {filepath} ({image.size[0]}x{image.size[1]})")
    return filepath, f"/uploads/processed/{filename}"
