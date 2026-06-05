from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.wear_record import WearRecord
from app.models.outfit import Outfit

from app.schemas.wear_record import (
    WearRecordCreate,
    WearRecordResponse
)

router = APIRouter(
    prefix="/wear-records",
    tags=["Wear Records"]
)

@router.post(
    "/",
    response_model=WearRecordResponse
)
def create_wear_record(
    record: WearRecordCreate,
    db: Session = Depends(get_db)
):
    outfit = db.query(Outfit).filter(
        Outfit.id == record.outfit_id
    ).first()

    if not outfit:
        raise HTTPException(
            status_code=404,
            detail="Outfit not found"
        )

    wear_record = WearRecord(
        user_id=1,
        outfit_id=record.outfit_id,
        worn_date=record.worn_date
    )

    db.add(wear_record)
    db.commit()
    db.refresh(wear_record)

    return wear_record

@router.get(
    "/",
    response_model=list[WearRecordResponse]
)
def get_wear_records(
    db: Session = Depends(get_db)
):
    return db.query(
        WearRecord
    ).all()

@router.get(
    "/{record_id}",
    response_model=WearRecordResponse
)
def get_wear_record(
    record_id: int,
    db: Session = Depends(get_db)
):
    record = db.query(
        WearRecord
    ).filter(
        WearRecord.id == record_id
    ).first()

    if not record:
        raise HTTPException(
            status_code=404,
            detail="Wear record not found"
        )

    return record

@router.delete("/{record_id}")
def delete_wear_record(
    record_id: int,
    db: Session = Depends(get_db)
):
    record = db.query(
        WearRecord
    ).filter(
        WearRecord.id == record_id
    ).first()

    if not record:
        raise HTTPException(
            status_code=404,
            detail="Wear record not found"
        )

    db.delete(record)
    db.commit()

    return {
        "message": "Wear record deleted successfully"
    }