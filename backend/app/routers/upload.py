from pathlib import Path
from uuid import uuid4
from io import BytesIO

from fastapi import (
    APIRouter,
    UploadFile,
    File,
    HTTPException
)

from PIL import Image
from pillow_heif import register_heif_opener

register_heif_opener()

router = APIRouter(
    prefix="/upload",
    tags=["Upload"]
)

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

MAX_FILE_SIZE = 10 * 1024 * 1024

ALLOWED_TYPES = [
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/heic",
    "image/heif"
]


@router.post("/")
async def upload_image(
    file: UploadFile = File(...)
):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail=(
                "Only JPG, PNG, WEBP and HEIC images are allowed"
            )
        )

    content = await file.read()

    if len(content) == 0:
        raise HTTPException(
            status_code=400,
            detail="File is empty"
        )

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="Maximum file size is 10 MB"
        )

    try:
        Image.open(
            BytesIO(content)
        ).verify()

    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Invalid image file"
        )

    extension = Path(
        file.filename
    ).suffix.lower()

    filename = f"{uuid4()}{extension}"

    filepath = UPLOAD_DIR / filename

    with open(filepath, "wb") as buffer:
        buffer.write(content)

    return {
        "image_url": f"/uploads/{filename}"
    }