from datetime import datetime, timezone
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
from app.schemas.outfit import OutfitCreate, OutfitResponse, OutfitUpdate
from app.schemas.outfit_item import OutfitItemCreate, OutfitItemResponse

router = APIRouter(prefix="/outfits", tags=["Outfits"])


@router.get("/", response_model=list[OutfitResponse])
def get_outfits(
    name: Optional[str] = None,
    capsule_id: Optional[int] = None,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = (
        db.query(Outfit)
        .options(selectinload(Outfit.items).selectinload(OutfitItem.clothing_item))
        .filter(
            Outfit.user_id == current_user["user_id"],
            Outfit.is_deleted.is_(False),
        )
    )

    if capsule_id is not None:
        query = query.filter(Outfit.capsule_id == capsule_id)
    else:
        query = query.filter(Outfit.capsule_id.is_(None))

    if name:
        query = query.filter(Outfit.name.ilike(f"%{name}%"))

    return query.all()


@router.get("/trash", response_model=list[OutfitResponse])
def get_trash_outfits(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    outfits = (
        db.query(Outfit)
        .options(selectinload(Outfit.items).selectinload(OutfitItem.clothing_item))
        .filter(Outfit.user_id == current_user["user_id"], Outfit.is_deleted.is_(True))
        .order_by(Outfit.created_at.desc())
        .all()
    )
    return [
        OutfitResponse(
            id=o.id,
            user_id=o.user_id,
            name=o.name,
            is_deleted=o.is_deleted,
            days_until_deleted=(max(0, 14 - (datetime.now(timezone.utc) - o.deleted_at).days) if o.deleted_at else None),
            items=[
                OutfitItemResponse(
                    id=item.id,
                    outfit_id=item.outfit_id,
                    clothing_item_id=item.clothing_item_id,
                    x=item.x,
                    y=item.y,
                    scale=item.scale,
                    image_url=item.image_url,
                )
                for item in o.items
            ],
        )
        for o in outfits
    ]


@router.get("/{outfit_id}", response_model=OutfitResponse)
def get_outfit(
    outfit_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    outfit = (
        db.query(Outfit)
        .options(selectinload(Outfit.items).selectinload(OutfitItem.clothing_item))
        .filter(
            Outfit.id == outfit_id,
            Outfit.user_id == current_user["user_id"],
            Outfit.is_deleted.is_(False),
        )
        .first()
    )

    if not outfit:
        raise HTTPException(status_code=404, detail="Outfit not found")

    return outfit


@router.post("/", response_model=OutfitResponse, status_code=status.HTTP_201_CREATED)
def create_outfit(
    outfit: OutfitCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # If capsule_id is provided, validate capsule and item membership
    if outfit.capsule_id is not None:
        capsule = (
            db.query(Capsule)
            .filter(
                Capsule.id == outfit.capsule_id,
                Capsule.user_id == current_user["user_id"],
            )
            .first()
        )
        if not capsule:
            raise HTTPException(status_code=404, detail="Capsule not found")

        capsule_item_ids = {
            ci.clothing_item_id for ci in db.query(CapsuleItem).filter(CapsuleItem.capsule_id == outfit.capsule_id).all()
        }
        for item_data in outfit.items:
            if item_data.clothing_item_id not in capsule_item_ids:
                raise HTTPException(
                    status_code=400,
                    detail=f"Clothing item {item_data.clothing_item_id} is not in capsule {outfit.capsule_id}",
                )

    new_outfit = Outfit(
        user_id=current_user["user_id"],
        name=outfit.name,
        capsule_id=outfit.capsule_id,
    )

    db.add(new_outfit)
    db.flush()

    if outfit.items:
        for item_data in outfit.items:
            clothing = (
                db.query(ClothingItem)
                .filter(
                    ClothingItem.id == item_data.clothing_item_id,
                    ClothingItem.user_id == current_user["user_id"],
                )
                .first()
            )
            if not clothing:
                raise HTTPException(
                    status_code=404,
                    detail=f"Clothing item {item_data.clothing_item_id} not found",
                )
            db.add(
                OutfitItem(
                    outfit_id=new_outfit.id,
                    clothing_item_id=item_data.clothing_item_id,
                    x=item_data.x,
                    y=item_data.y,
                    scale=item_data.scale,
                )
            )

    db.commit()

    # Reload with items for response
    outfit_with_items = (
        db.query(Outfit)
        .options(selectinload(Outfit.items).selectinload(OutfitItem.clothing_item))
        .filter(Outfit.id == new_outfit.id)
        .first()
    )

    return outfit_with_items


@router.patch("/{outfit_id}", response_model=OutfitResponse)
def update_outfit(
    outfit_id: int,
    outfit: OutfitUpdate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    existing = db.query(Outfit).filter(Outfit.id == outfit_id, Outfit.user_id == current_user["user_id"]).first()

    if not existing:
        raise HTTPException(status_code=404, detail="Outfit not found")

    update_data = outfit.model_dump(exclude_unset=True)

    if "items" in update_data:
        items_data = update_data.pop("items")

        # If outfit belongs to a capsule, validate all new items belong to it
        if existing.capsule_id is not None:
            capsule_item_ids = {
                ci.clothing_item_id for ci in db.query(CapsuleItem).filter(CapsuleItem.capsule_id == existing.capsule_id).all()
            }
            for item_data in items_data:
                if item_data["clothing_item_id"] not in capsule_item_ids:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Clothing item {item_data['clothing_item_id']} is not in capsule {existing.capsule_id}",
                    )

        db.query(OutfitItem).filter(OutfitItem.outfit_id == outfit_id).delete()

        for item_data in items_data:
            clothing = (
                db.query(ClothingItem)
                .filter(
                    ClothingItem.id == item_data["clothing_item_id"],
                    ClothingItem.user_id == current_user["user_id"],
                )
                .first()
            )
            if not clothing:
                raise HTTPException(
                    status_code=404,
                    detail=f"Clothing item {item_data['clothing_item_id']} not found",
                )
            db.add(
                OutfitItem(
                    outfit_id=outfit_id,
                    clothing_item_id=item_data["clothing_item_id"],
                    x=item_data.get("x", 0.0),
                    y=item_data.get("y", 0.0),
                    scale=item_data.get("scale", 1.0),
                )
            )

    for key, value in update_data.items():
        setattr(existing, key, value)

    db.commit()

    # Reload with items for response
    outfit_with_items = (
        db.query(Outfit)
        .options(selectinload(Outfit.items).selectinload(OutfitItem.clothing_item))
        .filter(Outfit.id == existing.id)
        .first()
    )

    return outfit_with_items


@router.delete("/{outfit_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_outfit(
    outfit_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    outfit = (
        db.query(Outfit)
        .filter(
            Outfit.id == outfit_id,
            Outfit.user_id == current_user["user_id"],
            Outfit.is_deleted.is_(False),
        )
        .first()
    )

    if not outfit:
        raise HTTPException(status_code=404, detail="Outfit not found")

    outfit.is_deleted = True
    outfit.deleted_at = datetime.now(timezone.utc)
    db.commit()

    return None


@router.post("/{outfit_id}/restore")
def restore_outfit(
    outfit_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    outfit = (
        db.query(Outfit)
        .filter(
            Outfit.id == outfit_id,
            Outfit.user_id == current_user["user_id"],
            Outfit.is_deleted.is_(True),
        )
        .first()
    )

    if not outfit:
        raise HTTPException(status_code=404, detail="Outfit not found")

    outfit.is_deleted = False
    outfit.deleted_at = None
    db.commit()

    return {"message": "Outfit restored successfully"}


@router.delete("/{outfit_id}/permanent")
def permanent_delete_outfit(
    outfit_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    outfit = (
        db.query(Outfit)
        .filter(
            Outfit.id == outfit_id,
            Outfit.user_id == current_user["user_id"],
            Outfit.is_deleted.is_(True),
        )
        .first()
    )

    if not outfit:
        raise HTTPException(status_code=404, detail="Outfit not found")

    db.delete(outfit)
    db.commit()

    return {"message": "Outfit permanently deleted"}


@router.post(
    "/{outfit_id}/items",
    response_model=OutfitItemResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_item_to_outfit(
    outfit_id: int,
    item: OutfitItemCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    outfit = db.query(Outfit).filter(Outfit.id == outfit_id, Outfit.user_id == current_user["user_id"]).first()

    if not outfit:
        raise HTTPException(status_code=404, detail="Outfit not found")

    # If outfit belongs to a capsule, validate item belongs to that capsule
    if outfit.capsule_id is not None:
        capsule_item = (
            db.query(CapsuleItem)
            .filter(
                CapsuleItem.capsule_id == outfit.capsule_id,
                CapsuleItem.clothing_item_id == item.clothing_item_id,
            )
            .first()
        )
        if not capsule_item:
            raise HTTPException(
                status_code=400,
                detail=f"Clothing item {item.clothing_item_id} is not in capsule {outfit.capsule_id}",
            )

    clothing = (
        db.query(ClothingItem)
        .filter(
            ClothingItem.id == item.clothing_item_id,
            ClothingItem.user_id == current_user["user_id"],
        )
        .first()
    )

    if not clothing:
        raise HTTPException(status_code=404, detail="Clothing item not found")

    existing_item = (
        db.query(OutfitItem)
        .filter(
            OutfitItem.outfit_id == outfit_id,
            OutfitItem.clothing_item_id == item.clothing_item_id,
        )
        .first()
    )

    if existing_item:
        raise HTTPException(status_code=400, detail="Item already exists in outfit")

    outfit_item = OutfitItem(
        outfit_id=outfit_id,
        clothing_item_id=item.clothing_item_id,
        x=item.x,
        y=item.y,
        scale=item.scale,
    )

    db.add(outfit_item)
    db.commit()
    db.refresh(outfit_item)

    return outfit_item


@router.get("/{outfit_id}/items", response_model=list[OutfitItemResponse])
def get_outfit_items(
    outfit_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    outfit = db.query(Outfit).filter(Outfit.id == outfit_id, Outfit.user_id == current_user["user_id"]).first()

    if not outfit:
        raise HTTPException(status_code=404, detail="Outfit not found")

    items = (
        db.query(OutfitItem).options(selectinload(OutfitItem.clothing_item)).filter(OutfitItem.outfit_id == outfit_id).all()
    )

    return items


@router.delete("/{outfit_id}/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_item_from_outfit(
    outfit_id: int,
    item_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    outfit = db.query(Outfit).filter(Outfit.id == outfit_id, Outfit.user_id == current_user["user_id"]).first()

    if not outfit:
        raise HTTPException(status_code=404, detail="Outfit not found")

    outfit_item = db.query(OutfitItem).filter(OutfitItem.outfit_id == outfit_id, OutfitItem.id == item_id).first()

    if not outfit_item:
        raise HTTPException(status_code=404, detail="Item not found in outfit")

    db.delete(outfit_item)
    db.commit()

    return None
