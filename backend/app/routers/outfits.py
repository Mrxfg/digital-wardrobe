from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.outfit import Outfit
from app.models.outfit_item import OutfitItem
from app.models.clothing_item import ClothingItem
from typing import Optional

from app.schemas.clothing_item import ClothingItemResponse
from app.dependencies.auth import get_current_user

from app.schemas.outfit_item import (
    OutfitItemCreate,
    OutfitItemResponse
)

from app.schemas.outfit import (
    OutfitCreate,
    OutfitUpdate,
    OutfitResponse
)

router = APIRouter(
    prefix="/outfits",
    tags=["Outfits"]
)


@router.get(
    "/",
    response_model=list[OutfitResponse]
)
def get_outfits(
    name: Optional[str] = None,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Outfit).filter(
        Outfit.user_id == current_user["user_id"]
    )

    if name:
        query = query.filter(
            Outfit.name.ilike(f"%{name}%")
        )

    return query.all()

@router.get(
    "/{outfit_id}",
    response_model=OutfitResponse
)
def get_outfit(
    outfit_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    outfit = db.query(Outfit).filter(
        Outfit.id == outfit_id,
        Outfit.user_id == current_user["user_id"]
    ).first()

    if not outfit:
        raise HTTPException(
            status_code=404,
            detail="Outfit not found"
        )

    return outfit


@router.post(
    "/",
    response_model=OutfitResponse
)
def create_outfit(
    outfit: OutfitCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    new_outfit = Outfit(
        user_id=current_user["user_id"],
        name=outfit.name
    )

    db.add(new_outfit)
    db.commit()
    db.refresh(new_outfit)

    return new_outfit


@router.patch(
    "/{outfit_id}",
    response_model=OutfitResponse
)
def update_outfit(
    outfit_id: int,
    outfit: OutfitUpdate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    existing = db.query(Outfit).filter(
        Outfit.id == outfit_id,
        Outfit.user_id == current_user["user_id"]
    ).first()

    if not existing:
        raise HTTPException(
            status_code=404,
            detail="Outfit not found"
        )

    update_data = outfit.model_dump(
        exclude_unset=True
    )

    for key, value in update_data.items():
        setattr(existing, key, value)

    db.commit()
    db.refresh(existing)

    return existing


@router.delete("/{outfit_id}")
def delete_outfit(
    outfit_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    outfit = db.query(Outfit).filter(
        Outfit.id == outfit_id,
        Outfit.user_id == current_user["user_id"]
    ).first()

    if not outfit:
        raise HTTPException(
            status_code=404,
            detail="Outfit not found"
        )

    db.delete(outfit)
    db.commit()

    return {
        "message": "Outfit deleted successfully"
    }

@router.post(
    "/{outfit_id}/items",
    response_model=OutfitItemResponse
)
def add_item_to_outfit(
    outfit_id: int,
    item: OutfitItemCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    outfit = db.query(Outfit).filter(
        Outfit.id == outfit_id,
        Outfit.user_id == current_user["user_id"]).first()

    if not outfit:
        raise HTTPException(
            status_code=404,
            detail="Outfit not found"
        )

    clothing = db.query(ClothingItem).filter(
        ClothingItem.id == item.clothing_item_id,
        ClothingItem.user_id == current_user["user_id"]
    ).first()

    if not clothing:
        raise HTTPException(
            status_code=404,
            detail="Clothing item not found"
        )
    existing_item = db.query(OutfitItem).filter(
        OutfitItem.outfit_id == outfit_id,
        OutfitItem.clothing_item_id == item.clothing_item_id
    ).first()

    if existing_item:
        raise HTTPException(
            status_code=400,
            detail="Item already exists in outfit"
        )

    outfit_item = OutfitItem(
        outfit_id=outfit_id,
        clothing_item_id=item.clothing_item_id
    )

    db.add(outfit_item)
    db.commit()
    db.refresh(outfit_item)

    return outfit_item


@router.get(
    "/{outfit_id}/items",
    response_model=list[ClothingItemResponse]
)
def get_outfit_items(
    outfit_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    outfit = db.query(Outfit).filter(
        Outfit.id == outfit_id,
        Outfit.user_id == current_user["user_id"]
    ).first()

    if not outfit:
        raise HTTPException(
            status_code=404,
            detail="Outfit not found"
        )

    items = (
        db.query(ClothingItem)
        .join(
            OutfitItem,
            ClothingItem.id == OutfitItem.clothing_item_id
        )
        .filter(
            OutfitItem.outfit_id == outfit_id,
            ClothingItem.is_deleted.is_(False)
        )
        .all()
    )

    return items


@router.delete(
    "/{outfit_id}/items/{item_id}"
)
def remove_item_from_outfit(
    outfit_id: int,
    item_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    outfit = db.query(Outfit).filter(
        Outfit.id == outfit_id,
        Outfit.user_id == current_user["user_id"]
    ).first()

    if not outfit:
        raise HTTPException(
            status_code=404,
            detail="Outfit not found"
        )

    outfit_item = db.query(
        OutfitItem
    ).filter(
        OutfitItem.outfit_id == outfit_id,
        OutfitItem.clothing_item_id == item_id
    ).first()

    if not outfit_item:
        raise HTTPException(
            status_code=404,
            detail="Item not found in outfit"
        )

    db.delete(outfit_item)
    db.commit()

    return {
        "message": "Item removed from outfit"
    }