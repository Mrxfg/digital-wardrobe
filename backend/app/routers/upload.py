from io import BytesIO
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, File, HTTPException, UploadFile
from PIL import Image
from pillow_heif import register_heif_opener
from rembg import remove

register_heif_opener()

UPLOAD_DIR = Path("uploads")
ORIGINAL_DIR = UPLOAD_DIR / "original"
PROCESSED_DIR = UPLOAD_DIR / "processed"

ORIGINAL_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

router = APIRouter(prefix="/upload", tags=["Upload"])


MAX_FILE_SIZE = 10 * 1024 * 1024

ALLOWED_TYPES = ["image/jpeg", "image/png", "image/webp", "image/heic", "image/heif"]


@router.post("/")
async def upload_image(file: UploadFile = File(...)):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail=("Only JPG, PNG, WEBP and HEIC images are allowed"))

    content = await file.read()

    if len(content) == 0:
        raise HTTPException(status_code=400, detail="File is empty")

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="Maximum file size is 10 MB")

    try:
        Image.open(BytesIO(content)).verify()

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image file: {str(e)}")

    original_extension = Path(file.filename).suffix.lower()

    original_filename = f"{uuid4()}{original_extension}"

    original_filepath = ORIGINAL_DIR / original_filename

    with open(original_filepath, "wb") as buffer:
        buffer.write(content)

    try:
        processed_content = remove(content)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Background removal failed: {str(e)}")

    processed_filename = f"{uuid4()}.png"

    processed_filepath = PROCESSED_DIR / processed_filename

    with open(processed_filepath, "wb") as buffer:
        buffer.write(processed_content)

    return {
        "image_url": f"/uploads/processed/{processed_filename}",
        "original_image_url": f"/uploads/original/{original_filename}",
    }
