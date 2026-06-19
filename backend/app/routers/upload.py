from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.services.upload import (
    save_original,
    save_processed,
    validate_file,
    validate_image,
)

router = APIRouter(prefix="/upload", tags=["Upload"])


@router.post("/")
async def upload_image(file: UploadFile = File(...)):
    content_type = file.content_type or "application/octet-stream"
    content = await file.read()

    # Validate file
    try:
        validate_file(content_type, content)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Validate image integrity
    try:
        validate_image(content)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Save compressed original
    original_extension = Path(file.filename).suffix.lower() if file.filename else ".jpg"
    try:
        _, original_url = save_original(content, original_extension)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save original image: {e}")

    # Remove background and save processed
    try:
        _, image_url = save_processed(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Background removal failed: {e}")

    return {
        "image_url": image_url,
        "original_image_url": original_url,
    }
