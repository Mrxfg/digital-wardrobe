from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, selectinload

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.capsule import Capsule
from app.models.capsule_item import CapsuleItem
from app.models.clothing_item import ClothingItem
from app.models.outfit import Outfit
from app.models.outfit_item import OutfitItem
from app.schemas.capsule import (
    CapsuleCreate,
    CapsuleDetailResponse,
    CapsuleItemLight,
    CapsuleOutfit,
    CapsuleOutfitItem,
    CapsuleResponse,
    CapsuleUpdate,
)
from app.schemas.capsule_item import CapsuleItemCreate, CapsuleItemResponse
from app.schemas.clothing_item import ClothingItemResponse

router = APIRouter(prefix="/capsules", tags=["Capsules"])


@router.get("/", response_model=list[CapsuleResponse])
def get_capsules(name: Optional[str] = None, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    query = (
        db.query(Capsule)
        .options(selectinload(Capsule.items))
        .filter(
            Capsule.user_id == current_user["user_id"],
            Capsule.is_deleted.is_(False),
        )
    )

    if name:
        query = query.filter(Capsule.name.ilike(f"%{name}%"))

    capsules = query.order_by(Capsule.created_at.desc()).all()

    return [
        CapsuleResponse(
            id=c.id,
            user_id=c.user_id,
            name=c.name,
            description=c.description,
            season=c.season,
            is_deleted=c.is_deleted,
            items=[CapsuleItemLight(id=item.id, image_url=item.image_url) for item in c.items],
        )
        for c in capsules
    ]


@router.get("/trash", response_model=list[CapsuleResponse])
def get_trash_capsules(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    capsules = (
        db.query(Capsule)
        .options(selectinload(Capsule.items))
        .filter(Capsule.user_id == current_user["user_id"], Capsule.is_deleted.is_(True))
        .order_by(Capsule.created_at.desc())
        .all()
    )

    return [
        CapsuleResponse(
            id=c.id,
            user_id=c.user_id,
            name=c.name,
            description=c.description,
            season=c.season,
            is_deleted=c.is_deleted,
            items=[CapsuleItemLight(id=item.id, image_url=item.image_url) for item in c.items],
        )
        for c in capsules
    ]


@router.get("/{capsule_id}", response_model=CapsuleDetailResponse)
def get_capsule(capsule_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    capsule = (
        db.query(Capsule)
        .options(selectinload(Capsule.items))
        .filter(
            Capsule.id == capsule_id,
            Capsule.user_id == current_user["user_id"],
            Capsule.is_deleted.is_(False),
        )
        .first()
    )

    if not capsule:
        raise HTTPException(status_code=404, detail="Capsule not found")

    # Find outfits that use items from this capsule
    item_ids = [item.id for item in capsule.items]

    outfits_query = (
        db.query(Outfit)
        .join(OutfitItem)
        .filter(
            OutfitItem.clothing_item_id.in_(item_ids),
            Outfit.user_id == current_user["user_id"],
            Outfit.is_deleted.is_(False),
        )
        .distinct()
        .all()
    )

    outfits_data = []
    for outfit in outfits_query:
        outfit_items = (
            db.query(OutfitItem)
            .options(selectinload(OutfitItem.clothing_item))
            .filter(OutfitItem.outfit_id == outfit.id)
            .all()
        )

        outfits_data.append(
            CapsuleOutfit(
                name=outfit.name,
                items=[
                    CapsuleOutfitItem(
                        clothing_id=item.clothing_item_id,
                        image_url=item.image_url,
                    )
                    for item in outfit_items
                ],
            )
        )

    return CapsuleDetailResponse(
        id=capsule.id,
        user_id=capsule.user_id,
        name=capsule.name,
        description=capsule.description,
        season=capsule.season,
        is_deleted=capsule.is_deleted,
        created_at=capsule.created_at,
        items=capsule.items,
        outfits=outfits_data,
    )


@router.post("/", response_model=CapsuleResponse, status_code=status.HTTP_201_CREATED)
def create_capsule(capsule: CapsuleCreate, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    new_capsule = Capsule(
        user_id=current_user["user_id"],
        name=capsule.name,
        description=capsule.description,
        season=capsule.season,
    )

    db.add(new_capsule)
    db.flush()

    if capsule.items:
        if len(capsule.items) > 8:
            raise HTTPException(status_code=400, detail="Capsule can contain maximum 8 items")

        items = (
            db.query(ClothingItem)
            .filter(
                ClothingItem.id.in_(capsule.items),
                ClothingItem.user_id == current_user["user_id"],
                ClothingItem.is_deleted.is_(False),
            )
            .all()
        )
        found_ids = {item.id for item in items}
        for item_id in capsule.items:
            if item_id not in found_ids:
                raise HTTPException(status_code=404, detail=f"Clothing item {item_id} not found")
            db.add(CapsuleItem(capsule_id=new_capsule.id, clothing_item_id=item_id))

    db.commit()
    db.refresh(new_capsule)

    # Reload with items for response
    capsule_with_items = db.query(Capsule).options(selectinload(Capsule.items)).filter(Capsule.id == new_capsule.id).first()

    return CapsuleResponse(
        id=capsule_with_items.id,
        user_id=capsule_with_items.user_id,
        name=capsule_with_items.name,
        description=capsule_with_items.description,
        season=capsule_with_items.season,
        is_deleted=capsule_with_items.is_deleted,
        items=[CapsuleItemLight(id=item.id, image_url=item.image_url) for item in capsule_with_items.items],
    )


@router.patch("/{capsule_id}", response_model=CapsuleResponse)
def update_capsule(
    capsule_id: int, capsule: CapsuleUpdate, current_user=Depends(get_current_user), db: Session = Depends(get_db)
):
    existing = db.query(Capsule).filter(Capsule.id == capsule_id, Capsule.user_id == current_user["user_id"]).first()

    if not existing:
        raise HTTPException(status_code=404, detail="Capsule not found")

    update_data = capsule.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(existing, key, value)

    db.commit()
    db.refresh(existing)

    # Reload with items
    capsule_with_items = db.query(Capsule).options(selectinload(Capsule.items)).filter(Capsule.id == existing.id).first()

    return CapsuleResponse(
        id=capsule_with_items.id,
        user_id=capsule_with_items.user_id,
        name=capsule_with_items.name,
        description=capsule_with_items.description,
        season=capsule_with_items.season,
        is_deleted=capsule_with_items.is_deleted,
        items=[CapsuleItemLight(id=item.id, image_url=item.image_url) for item in capsule_with_items.items],
    )


@router.delete("/{capsule_id}")
def delete_capsule(capsule_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    capsule = (
        db.query(Capsule)
        .filter(
            Capsule.id == capsule_id,
            Capsule.user_id == current_user["user_id"],
            Capsule.is_deleted.is_(False),
        )
        .first()
    )

    if not capsule:
        raise HTTPException(status_code=404, detail="Capsule not found")

    capsule.is_deleted = True
    db.commit()

    return {"message": "Capsule deleted successfully"}


@router.post("/{capsule_id}/restore")
def restore_capsule(capsule_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    capsule = (
        db.query(Capsule)
        .filter(
            Capsule.id == capsule_id,
            Capsule.user_id == current_user["user_id"],
            Capsule.is_deleted.is_(True),
        )
        .first()
    )

    if not capsule:
        raise HTTPException(status_code=404, detail="Capsule not found")

    capsule.is_deleted = False
    db.commit()

    return {"message": "Capsule restored successfully"}


@router.delete("/{capsule_id}/permanent")
def permanent_delete_capsule(capsule_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    capsule = (
        db.query(Capsule)
        .filter(
            Capsule.id == capsule_id,
            Capsule.user_id == current_user["user_id"],
            Capsule.is_deleted.is_(True),
        )
        .first()
    )

    if not capsule:
        raise HTTPException(status_code=404, detail="Capsule not found")

    db.delete(capsule)
    db.commit()

    return {"message": "Capsule permanently deleted"}


@router.post("/{capsule_id}/items", response_model=CapsuleItemResponse)
def add_item_to_capsule(
    capsule_id: int, item: CapsuleItemCreate, current_user=Depends(get_current_user), db: Session = Depends(get_db)
):
    capsule = db.query(Capsule).filter(Capsule.id == capsule_id, Capsule.user_id == current_user["user_id"]).first()

    if not capsule:
        raise HTTPException(status_code=404, detail="Capsule not found")

    count = db.query(CapsuleItem).filter(CapsuleItem.capsule_id == capsule_id).count()

    if count >= 8:
        raise HTTPException(status_code=400, detail="Capsule can contain maximum 8 items")

    clothing = (
        db.query(ClothingItem)
        .filter(ClothingItem.id == item.clothing_item_id, ClothingItem.user_id == current_user["user_id"])
        .first()
    )

    if not clothing:
        raise HTTPException(status_code=404, detail="Clothing item not found")

    existing_item = (
        db.query(CapsuleItem)
        .filter(CapsuleItem.capsule_id == capsule_id, CapsuleItem.clothing_item_id == item.clothing_item_id)
        .first()
    )

    if existing_item:
        raise HTTPException(status_code=400, detail="Item already exists in capsule")

    capsule_item = CapsuleItem(capsule_id=capsule_id, clothing_item_id=item.clothing_item_id)

    db.add(capsule_item)
    db.commit()
    db.refresh(capsule_item)

    return capsule_item


@router.get("/{capsule_id}/items", response_model=list[ClothingItemResponse])
def get_capsule_items(capsule_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    capsule = db.query(Capsule).filter(Capsule.id == capsule_id, Capsule.user_id == current_user["user_id"]).first()

    if not capsule:
        raise HTTPException(status_code=404, detail="Capsule not found")

    items = (
        db.query(ClothingItem)
        .join(CapsuleItem, ClothingItem.id == CapsuleItem.clothing_item_id)
        .filter(CapsuleItem.capsule_id == capsule_id, ClothingItem.is_deleted.is_(False))
        .all()
    )

    return items


@router.delete("/{capsule_id}/items/{item_id}")
def remove_item_from_capsule(
    capsule_id: int, item_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)
):
    capsule = db.query(Capsule).filter(Capsule.id == capsule_id, Capsule.user_id == current_user["user_id"]).first()

    if not capsule:
        raise HTTPException(status_code=404, detail="Capsule not found")

    capsule_item = (
        db.query(CapsuleItem).filter(CapsuleItem.capsule_id == capsule_id, CapsuleItem.clothing_item_id == item_id).first()
    )

    if not capsule_item:
        raise HTTPException(status_code=404, detail="Item not found in capsule")

    db.delete(capsule_item)
    db.commit()

    return {"message": "Item removed from capsule"}
