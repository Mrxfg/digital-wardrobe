from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, selectinload

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.clothing_item import ClothingItem
from app.models.outfit import Outfit
from app.models.outfit_item import OutfitItem
from app.schemas.outfit import OutfitCreate, OutfitResponse, OutfitUpdate
from app.schemas.outfit_item import OutfitItemCreate, OutfitItemWithClothingResponse

router = APIRouter(prefix="/outfits", tags=["Outfits"])


@router.get("/", response_model=list[OutfitResponse])
def get_outfits(
    name: Optional[str] = None,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = (
        db.query(Outfit)
        .options(selectinload(Outfit.items).selectinload(OutfitItem.clothing_item))
        .filter(Outfit.user_id == current_user["user_id"])
    )

    if name:
        query = query.filter(Outfit.name.ilike(f"%{name}%"))

    return query.order_by(Outfit.created_at.desc()).all()


@router.get("/trash", response_model=list[OutfitResponse])
def get_trash_outfits(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return (
        db.query(Outfit)
        .options(selectinload(Outfit.items).selectinload(OutfitItem.clothing_item))
        .filter(Outfit.user_id == current_user["user_id"], Outfit.is_deleted.is_(True))
        .all()
    )


@router.get("/{outfit_id}", response_model=OutfitResponse)
def get_outfit(outfit_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    outfit = (
        db.query(Outfit)
        .options(selectinload(Outfit.items).selectinload(OutfitItem.clothing_item))
        .filter(Outfit.id == outfit_id, Outfit.user_id == current_user["user_id"], Outfit.is_deleted.is_(False))
        .first()
    )

    if not outfit:
        raise HTTPException(status_code=404, detail="Outfit not found")

    return outfit


@router.post("/", response_model=OutfitResponse, status_code=status.HTTP_201_CREATED)
def create_outfit(
    outfit_data: OutfitCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    new_outfit = Outfit(user_id=current_user["user_id"], name=outfit_data.name)
    db.add(new_outfit)
    db.flush()

    for item_data in outfit_data.items:
        clothing = (
            db.query(ClothingItem)
            .filter(
                ClothingItem.id == item_data.clothing_id,
                ClothingItem.user_id == current_user["user_id"],
            )
            .first()
        )

        if not clothing:
            db.rollback()
            raise HTTPException(
                status_code=400,
                detail=f"Clothing item {item_data.clothing_id} not found",
            )

        outfit_item = OutfitItem(
            outfit_id=new_outfit.id,
            clothing_id=item_data.clothing_id,
            x=item_data.x,
            y=item_data.y,
            scale=item_data.scale,
        )
        db.add(outfit_item)

    db.commit()
    db.refresh(new_outfit)

    # Reload with eagerly loaded relationships for the response
    return (
        db.query(Outfit)
        .options(selectinload(Outfit.items).selectinload(OutfitItem.clothing_item))
        .filter(Outfit.id == new_outfit.id)
        .first()
    )


@router.patch("/{outfit_id}", response_model=OutfitResponse)
def update_outfit(
    outfit_id: int,
    outfit_data: OutfitUpdate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    existing = (
        db.query(Outfit)
        .options(selectinload(Outfit.items))
        .filter(
            Outfit.id == outfit_id,
            Outfit.user_id == current_user["user_id"],
            Outfit.is_deleted.is_(False),
        )
        .first()
    )

    if not existing:
        raise HTTPException(status_code=404, detail="Outfit not found")

    if outfit_data.name is not None:
        existing.name = outfit_data.name

    if outfit_data.items is not None:
        # Replace all items
        for item in existing.items:
            db.delete(item)

        for item_data in outfit_data.items:
            clothing = (
                db.query(ClothingItem)
                .filter(
                    ClothingItem.id == item_data.clothing_id,
                    ClothingItem.user_id == current_user["user_id"],
                )
                .first()
            )

            if not clothing:
                db.rollback()
                raise HTTPException(
                    status_code=400,
                    detail=f"Clothing item {item_data.clothing_id} not found",
                )

            db.add(
                OutfitItem(
                    outfit_id=existing.id,
                    clothing_id=item_data.clothing_id,
                    x=item_data.x,
                    y=item_data.y,
                    scale=item_data.scale,
                )
            )

    db.commit()
    db.refresh(existing)

    return (
        db.query(Outfit)
        .options(selectinload(Outfit.items).selectinload(OutfitItem.clothing_item))
        .filter(Outfit.id == existing.id)
        .first()
    )


@router.delete("/{outfit_id}")
def delete_outfit(outfit_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    outfit = (
        db.query(Outfit)
        .filter(Outfit.id == outfit_id, Outfit.user_id == current_user["user_id"], Outfit.is_deleted.is_(False))
        .first()
    )

    if not outfit:
        raise HTTPException(status_code=404, detail="Outfit not found")

    outfit.is_deleted = True
    db.commit()

    return {"message": "Outfit deleted successfully"}


@router.post("/{outfit_id}/restore")
def restore_outfit(outfit_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    outfit = (
        db.query(Outfit)
        .filter(Outfit.id == outfit_id, Outfit.user_id == current_user["user_id"], Outfit.is_deleted.is_(True))
        .first()
    )

    if not outfit:
        raise HTTPException(status_code=404, detail="Outfit not found")

    outfit.is_deleted = False
    db.commit()

    return {"message": "Outfit restored successfully"}


@router.delete("/{outfit_id}/permanent")
def permanent_delete_outfit(outfit_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    outfit = (
        db.query(Outfit)
        .filter(Outfit.id == outfit_id, Outfit.user_id == current_user["user_id"], Outfit.is_deleted.is_(True))
        .first()
    )

    if not outfit:
        raise HTTPException(status_code=404, detail="Outfit not found")

    db.delete(outfit)
    db.commit()

    return {"message": "Outfit permanently deleted"}


# --- Individual item management ---


@router.post("/{outfit_id}/items", response_model=OutfitItemWithClothingResponse, status_code=status.HTTP_201_CREATED)
def add_item_to_outfit(
    outfit_id: int,
    item: OutfitItemCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    outfit = (
        db.query(Outfit)
        .filter(Outfit.id == outfit_id, Outfit.user_id == current_user["user_id"])
        .first()
    )

    if not outfit:
        raise HTTPException(status_code=404, detail="Outfit not found")

    clothing = (
        db.query(ClothingItem)
        .filter(ClothingItem.id == item.clothing_id, ClothingItem.user_id == current_user["user_id"])
        .first()
    )

    if not clothing:
        raise HTTPException(status_code=404, detail="Clothing item not found")

    outfit_item = OutfitItem(
        outfit_id=outfit_id,
        clothing_id=item.clothing_id,
        x=item.x,
        y=item.y,
        scale=item.scale,
    )

    db.add(outfit_item)
    db.commit()
    db.refresh(outfit_item)

    return (
        db.query(OutfitItem)
        .options(selectinload(OutfitItem.clothing_item))
        .filter(OutfitItem.id == outfit_item.id)
        .first()
    )


@router.get("/{outfit_id}/items", response_model=list[OutfitItemWithClothingResponse])
def get_outfit_items(outfit_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    outfit = (
        db.query(Outfit)
        .filter(Outfit.id == outfit_id, Outfit.user_id == current_user["user_id"])
        .first()
    )

    if not outfit:
        raise HTTPException(status_code=404, detail="Outfit not found")

    return (
        db.query(OutfitItem)
        .options(selectinload(OutfitItem.clothing_item))
        .filter(OutfitItem.outfit_id == outfit_id)
        .all()
    )


@router.delete("/{outfit_id}/items/{item_id}")
def remove_item_from_outfit(
    outfit_id: int,
    item_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    outfit = (
        db.query(Outfit)
        .filter(Outfit.id == outfit_id, Outfit.user_id == current_user["user_id"])
        .first()
    )

    if not outfit:
        raise HTTPException(status_code=404, detail="Outfit not found")

    outfit_item = (
        db.query(OutfitItem)
        .filter(OutfitItem.outfit_id == outfit_id, OutfitItem.id == item_id)
        .first()
    )

    if not outfit_item:
        raise HTTPException(status_code=404, detail="Item not found in outfit")

    db.delete(outfit_item)
    db.commit()

    return {"message": "Item removed from outfit"}
