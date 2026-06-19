from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.clothing_item import ClothingItem
from app.schemas.clothing_item import ClothingItemResponse
from app.services.upload import save_original, save_processed, validate_file, validate_image

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
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Upload and process the photo
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
        _, image_url = save_processed(content)
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
