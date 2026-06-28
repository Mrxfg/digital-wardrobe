from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.clothing_item import ClothingItem
from app.models.outfit import Outfit
from app.models.outfit_item import OutfitItem
from app.schemas.outfit import OutfitCreate, OutfitItemCreate, OutfitItemResponse, OutfitResponse, OutfitUpdate

router = APIRouter(prefix="/outfits", tags=["Outfits"])

POSITIONS = ["top", "bottom", "shoes", "accessory"]


def _load_positioned_items(outfit: Outfit, db: Session) -> dict:
    """Load outfit items grouped by position."""
    result = {p: None for p in POSITIONS}
    outfit_items = (
        db.query(OutfitItem, ClothingItem)
        .join(ClothingItem, OutfitItem.clothing_item_id == ClothingItem.id)
        .filter(OutfitItem.outfit_id == outfit.id)
        .all()
    )
    for oi, ci in outfit_items:
        result[oi.position] = ci
    return result


def _enrich_outfit(outfit: Outfit, db: Session) -> Outfit:
    """Attach positioned items to an outfit object for serialization."""
    positioned = _load_positioned_items(outfit, db)
    for pos in POSITIONS:
        setattr(outfit, pos, positioned[pos])
    return outfit


@router.get("/", response_model=list[OutfitResponse])
def get_outfits(name: Optional[str] = None, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    query = db.query(Outfit).filter(
        Outfit.user_id == current_user["user_id"],
        Outfit.is_deleted.is_(False),
    )

    if name:
        query = query.filter(Outfit.name.ilike(f"%{name}%"))

    outfits = query.all()
    for o in outfits:
        _enrich_outfit(o, db)
    return outfits


@router.get("/trash", response_model=list[OutfitResponse])
def get_trash_outfits(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    outfits = db.query(Outfit).filter(Outfit.user_id == current_user["user_id"], Outfit.is_deleted.is_(True)).all()
    for o in outfits:
        _enrich_outfit(o, db)
    return outfits


@router.get("/{outfit_id}", response_model=OutfitResponse)
def get_outfit(outfit_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    outfit = (
        db.query(Outfit)
        .filter(Outfit.id == outfit_id, Outfit.user_id == current_user["user_id"], Outfit.is_deleted.is_(False))
        .first()
    )

    if not outfit:
        raise HTTPException(status_code=404, detail="Outfit not found")

    return _enrich_outfit(outfit, db)


@router.post("/", response_model=OutfitResponse)
def create_outfit(outfit: OutfitCreate, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    new_outfit = Outfit(user_id=current_user["user_id"], name=outfit.name)

    db.add(new_outfit)
    db.flush()

    # Add items by position
    items_to_add = []
    for pos in POSITIONS:
        item_id = getattr(outfit, pos, None)
        if item_id is not None:
            clothing = (
                db.query(ClothingItem)
                .filter(ClothingItem.id == item_id, ClothingItem.user_id == current_user["user_id"])
                .first()
            )
            if not clothing:
                db.rollback()
                raise HTTPException(status_code=404, detail=f"Clothing item {item_id} not found")

            outfit_item = OutfitItem(outfit_id=new_outfit.id, clothing_item_id=item_id, position=pos)
            db.add(outfit_item)

    db.commit()
    db.refresh(new_outfit)

    return _enrich_outfit(new_outfit, db)


@router.patch("/{outfit_id}", response_model=OutfitResponse)
def update_outfit(outfit_id: int, outfit: OutfitUpdate, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    existing = (
        db.query(Outfit)
        .filter(Outfit.id == outfit_id, Outfit.user_id == current_user["user_id"], Outfit.is_deleted.is_(False))
        .first()
    )

    if not existing:
        raise HTTPException(status_code=404, detail="Outfit not found")

    update_data = outfit.model_dump(exclude_unset=True)

    # Handle position updates separately
    position_updates = {}
    for pos in POSITIONS:
        if pos in update_data:
            position_updates[pos] = update_data.pop(pos)

    for key, value in update_data.items():
        setattr(existing, key, value)

    # Update position links
    if position_updates:
        for pos, item_id in position_updates.items():
            if item_id is None:
                # Remove item from this position
                db.query(OutfitItem).filter(
                    OutfitItem.outfit_id == existing.id,
                    OutfitItem.position == pos,
                ).delete()
            else:
                # Upsert item for this position
                existing_link = (
                    db.query(OutfitItem)
                    .filter(OutfitItem.outfit_id == existing.id, OutfitItem.position == pos)
                    .first()
                )
                if existing_link:
                    existing_link.clothing_item_id = item_id
                else:
                    clothing = (
                        db.query(ClothingItem)
                        .filter(ClothingItem.id == item_id, ClothingItem.user_id == current_user["user_id"])
                        .first()
                    )
                    if not clothing:
                        db.rollback()
                        raise HTTPException(status_code=404, detail=f"Clothing item {item_id} not found")
                    db.add(OutfitItem(outfit_id=existing.id, clothing_item_id=item_id, position=pos))

    db.commit()
    db.refresh(existing)

    return _enrich_outfit(existing, db)


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


@router.post("/{outfit_id}/items", response_model=OutfitItemResponse)
def add_item_to_outfit(
    outfit_id: int, item: OutfitItemCreate, current_user=Depends(get_current_user), db: Session = Depends(get_db)
):
    outfit = db.query(Outfit).filter(Outfit.id == outfit_id, Outfit.user_id == current_user["user_id"]).first()

    if not outfit:
        raise HTTPException(status_code=404, detail="Outfit not found")

    clothing = (
        db.query(ClothingItem)
        .filter(ClothingItem.id == item.clothing_item_id, ClothingItem.user_id == current_user["user_id"])
        .first()
    )

    if not clothing:
        raise HTTPException(status_code=404, detail="Clothing item not found")

    # Check if position already has an item
    existing_item = (
        db.query(OutfitItem)
        .filter(OutfitItem.outfit_id == outfit_id, OutfitItem.position == item.position)
        .first()
    )
    if existing_item:
        raise HTTPException(status_code=400, detail=f"Position '{item.position}' already has an item. Use PATCH to update.")

    outfit_item = OutfitItem(outfit_id=outfit_id, clothing_item_id=item.clothing_item_id, position=item.position)

    db.add(outfit_item)
    db.commit()
    db.refresh(outfit_item)

    return outfit_item


@router.get("/{outfit_id}/items", response_model=list[OutfitItemResponse])
def get_outfit_items(outfit_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    outfit = db.query(Outfit).filter(Outfit.id == outfit_id, Outfit.user_id == current_user["user_id"]).first()

    if not outfit:
        raise HTTPException(status_code=404, detail="Outfit not found")

    return db.query(OutfitItem).filter(OutfitItem.outfit_id == outfit_id).all()


@router.delete("/{outfit_id}/items/{item_id}")
def remove_item_from_outfit(
    outfit_id: int, item_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)
):
    outfit = db.query(Outfit).filter(Outfit.id == outfit_id, Outfit.user_id == current_user["user_id"]).first()

    if not outfit:
        raise HTTPException(status_code=404, detail="Outfit not found")

    outfit_item = (
        db.query(OutfitItem).filter(OutfitItem.outfit_id == outfit_id, OutfitItem.clothing_item_id == item_id).first()
    )

    if not outfit_item:
        raise HTTPException(status_code=404, detail="Item not found in outfit")

    db.delete(outfit_item)
    db.commit()

    return {"message": "Item removed from outfit"}
