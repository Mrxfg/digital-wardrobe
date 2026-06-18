from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from typing import Optional
from sqlalchemy import func
from app.dependencies.auth import get_current_user
from app.database import get_db
from app.models.clothing_item import ClothingItem
from app.models.capsule_item import CapsuleItem
from app.models.outfit_item import OutfitItem
from app.schemas.clothing_item import (
    ClothingItemCreate,
    ClothingItemUpdate,
    ClothingItemResponse
)

router = APIRouter(
    prefix="/clothes",
    tags=["Clothes"]
)


@router.get(
    "/",
    response_model=list[ClothingItemResponse]
)
def get_clothes(
    name: Optional[str] = None,
    category: Optional[str] = None,
    color: Optional[str] = None,
    season: Optional[str] = None,
    material: Optional[str] = None,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(ClothingItem).filter(
        ClothingItem.user_id == current_user["user_id"],
        ClothingItem.is_deleted.is_(False)
    )

    if name:
        query = query.filter(
            ClothingItem.name.ilike(f"%{name}%")
        )

    if category:
        query = query.filter(
            func.lower(ClothingItem.category) == category.lower()
    )

    if color:
        query = query.filter(
            func.lower(ClothingItem.color) == color.lower()
    )

    if season:
        query = query.filter(
            func.lower(ClothingItem.season) == season.lower()
    )
    if material:
        query = query.filter(
            func.lower(ClothingItem.material) == material.lower()
    )
    return query.all()


@router.get("/trash", response_model=list[ClothingItemResponse])
def get_trash(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(ClothingItem).filter(
        ClothingItem.user_id == current_user["user_id"],
        ClothingItem.is_deleted.is_(True)
    ).all()

@router.get(
    "/{item_id}",
    response_model=ClothingItemResponse
)
def get_clothing_by_id(
    item_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    item = db.query(ClothingItem).filter(
        ClothingItem.id == item_id,
        ClothingItem.user_id == current_user["user_id"],
        ClothingItem.is_deleted.is_(False)
    ).first()

    if not item:
        raise HTTPException(
            status_code=404,
            detail="Clothing item not found"
        )

    return item


@router.delete("/{item_id}")
def delete_clothing(
    item_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    item = db.query(ClothingItem).filter(
        ClothingItem.id == item_id,
        ClothingItem.user_id == current_user["user_id"],
        ClothingItem.is_deleted.is_(False)
    ).first()

    if not item:
        raise HTTPException(
            status_code=404,
            detail="Clothing item not found"
        )

    item.is_deleted = True
    db.commit()

    return {
        "message": "Clothing item deleted successfully"
    }


@router.patch(
    "/{item_id}",
    response_model=ClothingItemResponse
)
def update_clothing(
    item_id: int,
    clothing: ClothingItemUpdate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    item = db.query(ClothingItem).filter(
        ClothingItem.id == item_id,
        ClothingItem.user_id == current_user["user_id"],
        ClothingItem.is_deleted.is_(False)
    ).first()

    if not item:
        raise HTTPException(
            status_code=404,
            detail="Clothing item not found"
        )

    update_data = clothing.model_dump(
        exclude_unset=True
    )

    for key, value in update_data.items():
        setattr(item, key, value)

    db.commit()
    db.refresh(item)

    return item


@router.post(
    "/",
    response_model=ClothingItemResponse
)
def create_clothing(
    clothing: ClothingItemCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    new_item = ClothingItem(
        user_id=current_user["user_id"],
        name=clothing.name,
        category=clothing.category,
        color=clothing.color,
        season=clothing.season,
        material=clothing.material,
        image_url=clothing.image_url,
        original_image_url=clothing.original_image_url
    )

    db.add(new_item)

    db.commit()

    db.refresh(new_item)

    return new_item

@router.post("/{item_id}/restore")
def restore_clothing(
    item_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    item = db.query(ClothingItem).filter(
        ClothingItem.id == item_id,
        ClothingItem.user_id == current_user["user_id"],
        ClothingItem.is_deleted.is_(True)
    ).first()

    if not item:
        raise HTTPException(
            status_code=404,
            detail="Clothing item not found"
        )

    item.is_deleted = False

    db.commit()

    return {
        "message": "Clothing item restored successfully"
    }


@router.delete("/{item_id}/permanent")
def permanent_delete_clothing(
    item_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    item = db.query(ClothingItem).filter(
        ClothingItem.id == item_id,
        ClothingItem.user_id == current_user["user_id"],
        ClothingItem.is_deleted.is_(True)
    ).first()

    if not item:
        raise HTTPException(
            status_code=404,
            detail="Clothing item not found"
        )

    db.query(CapsuleItem).filter(
        CapsuleItem.clothing_item_id == item_id
    ).delete()

    db.query(OutfitItem).filter(
        OutfitItem.clothing_item_id == item_id
    ).delete()

    db.delete(item)

    db.commit()

    return {
        "message": "Clothing item permanently deleted"
    }