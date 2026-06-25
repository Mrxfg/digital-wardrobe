import logging

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.clothing_item import ClothingItem
from app.schemas.clothing_item import ClothingItemResponse
from app.services.upload import save_original, save_processed, validate_file, validate_image

logger = logging.getLogger(__name__)

REQUIRED_FIELDS = ["name", "category", "color", "season", "material"]

router = APIRouter(prefix="/items", tags=["Items"])


@router.post("/", response_model=ClothingItemResponse, status_code=status.HTTP_201_CREATED)
async def create_item(
    name: str = Form(...),
    category: str = Form(...),
    color: str = Form(...),
    season: str = Form(...),
    material: str = Form(...),
    photo: UploadFile = File(...),
    remove_background: bool = Form(True),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new clothing item with optional background removal."""
    content_type = photo.content_type or "application/octet-stream"
    content = await photo.read()

    try:
        validate_file(content_type, content)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    try:
        validate_image(content)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    original_extension = f".{photo.filename.rsplit('.', 1)[-1]}" if photo.filename and "." in photo.filename else ".jpg"

    try:
        _, original_url = save_original(content, original_extension)

        if remove_background:
            _, image_url = save_processed(content)
            logger.info("Background removed for item '%s'", name)
        else:
            image_url = original_url
            logger.info("Background removal skipped for item '%s'", name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Photo processing failed: {e}")

    # Create the clothing item record
    item = ClothingItem(
        user_id=current_user["user_id"],
        name=name,
        category=category,
        color=color,
        season=season,
        material=material,
        image_url=image_url,
        original_image_url=original_url,
    )

    db.add(item)
    db.commit()
    db.refresh(item)

    return item


@router.post("/remove-background")
async def remove_background(file: UploadFile = File(...)):
    """Remove background from an uploaded image and return the processed PNG."""
    content_type = file.content_type or "application/octet-stream"
    content = await file.read()

    # Validate file type
    try:
        validate_file(content_type, content)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Validate image integrity
    try:
        validate_image(content)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Process — remove background
    try:
        processed_path, _ = save_processed(content)
    except Exception as e:
        logger.error("Background removal failed: %s", e)
        raise HTTPException(status_code=500, detail=f"Background removal failed: {e}")

    # Read processed PNG and return as image/png
    png_bytes = processed_path.read_bytes()

    return Response(content=png_bytes, media_type="image/png")
