from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.clothing_item import ClothingItem
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
    db: Session = Depends(get_db)
):
    clothes = db.query(
        ClothingItem
    ).all()

    return clothes

@router.get(
    "/{item_id}",
    response_model=ClothingItemResponse
)
def get_clothing_by_id(
    item_id: int,
    db: Session = Depends(get_db)
):
    item = db.query(ClothingItem).filter(
        ClothingItem.id == item_id
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
    db: Session = Depends(get_db)
):
    item = db.query(ClothingItem).filter(
        ClothingItem.id == item_id
    ).first()

    if not item:
        raise HTTPException(
            status_code=404,
            detail="Clothing item not found"
        )

    db.delete(item)
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
    db: Session = Depends(get_db)
):
    item = db.query(ClothingItem).filter(
        ClothingItem.id == item_id
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
    db: Session = Depends(get_db)
):
    new_item = ClothingItem(
        user_id=1,
        name=clothing.name,
        category=clothing.category,
        season=clothing.season,
        image_url=clothing.image_url
    )

    db.add(new_item)

    db.commit()

    db.refresh(new_item)

    return new_item