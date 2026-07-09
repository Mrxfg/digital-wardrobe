from datetime import date, datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, selectinload

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.clothing_item import ClothingItem
from app.models.outfit import Outfit
from app.models.outfit_item import OutfitItem
from app.models.users import User
from app.models.wear_record import WearRecord
from app.schemas.wear_record import (
    WearRecordCreate,
    WearRecordResponse,
    WearRecordUpdate,
)

router = APIRouter(prefix="/wear-records", tags=["Wear Records"])


@router.get("/check-today")
def check_worn_today(
    telegram_id: str = Query(...),
    db: Session = Depends(get_db),
):
    """Check if user has already logged wear records today.
    Used by the Telegram bot to avoid duplicate notifications (US-15)."""
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if not user:
        return {"has_worn_today": False}

    today = date.today()
    record = db.query(WearRecord).filter(WearRecord.user_id == user.id, WearRecord.worn_date == today).first()
    return {"has_worn_today": record is not None}


@router.post("/", response_model=WearRecordResponse, status_code=status.HTTP_201_CREATED)
def create_wear_record(
    record: WearRecordCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    outfit = db.query(Outfit).filter(Outfit.id == record.outfit_id, Outfit.user_id == current_user["user_id"]).first()

    if not outfit:
        raise HTTPException(status_code=404, detail="Outfit not found")

    wear_record = WearRecord(
        user_id=current_user["user_id"],
        outfit_id=record.outfit_id,
        worn_date=record.worn_date,
    )

    db.add(wear_record)

    # Update last_worn_at for all clothing items in the outfit
    outfit_items = db.query(OutfitItem).filter(OutfitItem.outfit_id == record.outfit_id).all()
    for item in outfit_items:
        db.query(ClothingItem).filter(
            ClothingItem.id == item.clothing_item_id,
            ClothingItem.user_id == current_user["user_id"],
        ).update({"last_worn_at": datetime.combine(record.worn_date, datetime.min.time())})

    db.commit()
    db.refresh(wear_record)

    return _build_response(db, wear_record.id, current_user["user_id"])


@router.get("/", response_model=list[WearRecordResponse])
def get_wear_records(
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(WearRecord).options(selectinload(WearRecord.outfit)).filter(WearRecord.user_id == current_user["user_id"])

    if date_from:
        query = query.filter(WearRecord.worn_date >= date_from)
    if date_to:
        query = query.filter(WearRecord.worn_date <= date_to)

    records = query.order_by(WearRecord.worn_date.desc()).all()

    return [_record_to_response(r, db) for r in records]


@router.get("/{record_id}", response_model=WearRecordResponse)
def get_wear_record(
    record_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return _build_response(db, record_id, current_user["user_id"])


@router.put("/{record_id}", response_model=WearRecordResponse)
def update_wear_record(
    record_id: int,
    record: WearRecordUpdate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    existing = db.query(WearRecord).filter(WearRecord.id == record_id, WearRecord.user_id == current_user["user_id"]).first()

    if not existing:
        raise HTTPException(status_code=404, detail="Wear record not found")

    if record.outfit_id is not None:
        outfit = db.query(Outfit).filter(Outfit.id == record.outfit_id, Outfit.user_id == current_user["user_id"]).first()
        if not outfit:
            raise HTTPException(status_code=404, detail="Outfit not found")
        existing.outfit_id = record.outfit_id

    if record.worn_date is not None:
        existing.worn_date = record.worn_date

    db.commit()
    db.refresh(existing)

    return _build_response(db, existing.id, current_user["user_id"])


@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_wear_record(
    record_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    record = db.query(WearRecord).filter(WearRecord.id == record_id, WearRecord.user_id == current_user["user_id"]).first()

    if not record:
        raise HTTPException(status_code=404, detail="Wear record not found")

    db.delete(record)
    db.commit()

    return None


def _build_response(db: Session, record_id: int, user_id: int) -> WearRecordResponse:
    record = (
        db.query(WearRecord)
        .options(selectinload(WearRecord.outfit))
        .filter(WearRecord.id == record_id, WearRecord.user_id == user_id)
        .first()
    )

    if not record:
        raise HTTPException(status_code=404, detail="Wear record not found")

    return _record_to_response(record, db)


def _record_to_response(record: WearRecord, db: Session) -> WearRecordResponse:
    from app.schemas.wear_record import WearRecordOutfit, WearRecordOutfitItem

    outfit_data = None
    if record.outfit:
        items = (
            db.query(OutfitItem)
            .join(ClothingItem, OutfitItem.clothing_item_id == ClothingItem.id)
            .filter(OutfitItem.outfit_id == record.outfit.id)
            .with_entities(OutfitItem.clothing_item_id, ClothingItem.image_url)
            .all()
        )

        outfit_data = WearRecordOutfit(
            name=record.outfit.name,
            items=[WearRecordOutfitItem(clothing_id=item.clothing_item_id, image_url=item.image_url) for item in items],
        )

    return WearRecordResponse(
        id=record.id,
        user_id=record.user_id,
        outfit_id=record.outfit_id,
        worn_date=record.worn_date,
        outfit=outfit_data,
    )
