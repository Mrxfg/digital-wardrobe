from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.capsule_item import CapsuleItem
from app.models.clothing_item import ClothingItem
from app.models.outfit_item import OutfitItem
from app.schemas.clothing_item import ClothingItemCreate, ClothingItemResponse, ClothingItemUpdate

router = APIRouter(prefix="/clothes", tags=["Clothes"])


@router.get("/", response_model=list[ClothingItemResponse])
def get_clothes(
    name: Optional[str] = None,
    category: Optional[str] = None,
    color: Optional[str] = None,
    season: Optional[str] = None,
    material: Optional[str] = None,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(ClothingItem).filter(ClothingItem.user_id == current_user["user_id"], ClothingItem.is_deleted.is_(False))

    if name:
        query = query.filter(ClothingItem.name.ilike(f"%{name}%"))

    if category:
        query = query.filter(func.lower(ClothingItem.category) == category.lower())

    if color:
        query = query.filter(func.lower(ClothingItem.color) == color.lower())

    if season:
        query = query.filter(func.lower(ClothingItem.season) == season.lower())
    if material:
        query = query.filter(func.lower(ClothingItem.material) == material.lower())
    return query.all()


@router.get("/trash", response_model=list[ClothingItemResponse])
def get_trash(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return (
        db.query(ClothingItem)
        .filter(ClothingItem.user_id == current_user["user_id"], ClothingItem.is_deleted.is_(True))
        .order_by(ClothingItem.deleted_at.desc().nullslast())
        .all()
    )


@router.get("/{item_id}", response_model=ClothingItemResponse)
def get_clothing_by_id(item_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    item = (
        db.query(ClothingItem)
        .filter(
            ClothingItem.id == item_id, ClothingItem.user_id == current_user["user_id"], ClothingItem.is_deleted.is_(False)
        )
        .first()
    )

    if not item:
        raise HTTPException(status_code=404, detail="Clothing item not found")

    return item


@router.delete("/{item_id}")
def delete_clothing(item_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    item = (
        db.query(ClothingItem)
        .filter(
            ClothingItem.id == item_id, ClothingItem.user_id == current_user["user_id"], ClothingItem.is_deleted.is_(False)
        )
        .first()
    )

    if not item:
        raise HTTPException(status_code=404, detail="Clothing item not found")

    item.is_deleted = True
    item.deleted_at = datetime.now(timezone.utc)
    db.commit()

    return {"message": "Clothing item deleted successfully", "deleted_at": item.deleted_at.isoformat()}


@router.patch("/{item_id}", response_model=ClothingItemResponse)
def update_clothing(
    item_id: int, clothing: ClothingItemUpdate, current_user=Depends(get_current_user), db: Session = Depends(get_db)
):
    item = (
        db.query(ClothingItem)
        .filter(
            ClothingItem.id == item_id, ClothingItem.user_id == current_user["user_id"], ClothingItem.is_deleted.is_(False)
        )
        .first()
    )

    if not item:
        raise HTTPException(status_code=404, detail="Clothing item not found")

    update_data = clothing.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(item, key, value)

    db.commit()
    db.refresh(item)

    return item


@router.post("/", response_model=ClothingItemResponse)
def create_clothing(clothing: ClothingItemCreate, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    new_item = ClothingItem(
        user_id=current_user["user_id"],
        name=clothing.name,
        category=clothing.category,
        color=clothing.color,
        season=clothing.season,
        material=clothing.material,
        image_url=clothing.image_url,
        original_image_url=clothing.original_image_url,
    )

    db.add(new_item)

    db.commit()

    db.refresh(new_item)

    return new_item


@router.post("/{item_id}/restore")
def restore_clothing(item_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    item = (
        db.query(ClothingItem)
        .filter(ClothingItem.id == item_id, ClothingItem.user_id == current_user["user_id"], ClothingItem.is_deleted.is_(True))
        .first()
    )

    if not item:
        raise HTTPException(status_code=404, detail="Clothing item not found")

    item.is_deleted = False
    item.deleted_at = None

    db.commit()

    return {"message": "Clothing item restored successfully"}


@router.delete("/{item_id}/permanent")
def permanent_delete_clothing(item_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    item = (
        db.query(ClothingItem)
        .filter(ClothingItem.id == item_id, ClothingItem.user_id == current_user["user_id"], ClothingItem.is_deleted.is_(True))
        .first()
    )

    if not item:
        raise HTTPException(status_code=404, detail="Clothing item not found")

    # Delete associated photo files from disk
    _delete_item_files(item)

    db.query(CapsuleItem).filter(CapsuleItem.clothing_item_id == item_id).delete()

    db.query(OutfitItem).filter(OutfitItem.clothing_item_id == item_id).delete()

    db.delete(item)

    db.commit()

    return {"message": "Clothing item permanently deleted"}


def _delete_item_files(item: ClothingItem):
    """Delete the image files associated with a clothing item from disk."""
    upload_dir = Path("uploads")

    if item.image_url:
        image_path = upload_dir / item.image_url.lstrip("/")
        _safe_unlink(image_path)

    if item.original_image_url:
        original_path = upload_dir / item.original_image_url.lstrip("/")
        _safe_unlink(original_path)


def _safe_unlink(path: Path):
    """Remove a file if it exists, silently ignore if it doesn't."""
    try:
        path.unlink(missing_ok=True)
    except Exception as e:
        print(f"Warning: could not delete file {path}: {e}")
