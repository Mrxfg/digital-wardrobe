from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.clothing_item import ClothingItem
from app.models.item_tag import ItemTag
from app.models.tag import Tag
from app.schemas.tag import TagCreate, TagResponse, TagWithCount

router = APIRouter(prefix="/tags", tags=["Tags"])


@router.get("/", response_model=list[TagWithCount])
def list_tags(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    """Return all unique tags with usage count for the current user."""
    results = (
        db.query(Tag, func.count(ItemTag.clothing_item_id).label("item_count"))
        .join(ItemTag, Tag.id == ItemTag.tag_id, isouter=True)
        .join(ClothingItem, ItemTag.clothing_item_id == ClothingItem.id)
        .filter(ClothingItem.user_id == current_user["user_id"])
        .group_by(Tag.id)
        .order_by(Tag.name)
        .all()
    )

    return [TagWithCount(id=tag.id, name=tag.name, created_at=tag.created_at, item_count=count) for tag, count in results]


@router.post("/", response_model=TagResponse, status_code=201)
def create_tag(tag: TagCreate, db: Session = Depends(get_db)):
    """Create a new tag (global, not user-specific)."""
    existing = db.query(Tag).filter(func.lower(Tag.name) == tag.name.lower()).first()

    if existing:
        raise HTTPException(status_code=409, detail=f"Tag '{tag.name}' already exists")

    new_tag = Tag(name=tag.name)
    db.add(new_tag)
    db.commit()
    db.refresh(new_tag)
    return new_tag


@router.delete("/{tag_id}")
def delete_tag(tag_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    """Delete a tag. Only if no user items reference it."""
    tag = db.query(Tag).filter(Tag.id == tag_id).first()

    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    db.query(ItemTag).filter(ItemTag.tag_id == tag_id).delete()
    db.delete(tag)
    db.commit()

    return {"message": "Tag deleted successfully"}


# --- Item-Tag assignment ---


@router.get("/items/{item_id}", response_model=list[TagResponse])
def get_item_tags(item_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all tags assigned to a specific item."""
    item = db.query(ClothingItem).filter(ClothingItem.id == item_id, ClothingItem.user_id == current_user["user_id"]).first()

    if not item:
        raise HTTPException(status_code=404, detail="Clothing item not found")

    return item.tags


@router.post("/items/{item_id}", response_model=list[TagResponse], status_code=201)
def assign_tag_to_item(item_id: int, tag: TagCreate, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    """Assign a tag to a clothing item. Creates the tag if it doesn't exist."""
    item = db.query(ClothingItem).filter(ClothingItem.id == item_id, ClothingItem.user_id == current_user["user_id"]).first()

    if not item:
        raise HTTPException(status_code=404, detail="Clothing item not found")

    # Find or create the tag
    tag_record = db.query(Tag).filter(func.lower(Tag.name) == tag.name.lower()).first()

    if not tag_record:
        tag_record = Tag(name=tag.name)
        db.add(tag_record)
        db.flush()

    # Check if already assigned
    existing = db.query(ItemTag).filter(ItemTag.clothing_item_id == item_id, ItemTag.tag_id == tag_record.id).first()

    if existing:
        raise HTTPException(status_code=409, detail=f"Item already has tag '{tag.name}'")

    db.add(ItemTag(clothing_item_id=item_id, tag_id=tag_record.id))
    db.commit()

    # Refresh item to get updated tags
    db.refresh(item)
    return item.tags


@router.delete("/items/{item_id}/{tag_id}")
def remove_tag_from_item(item_id: int, tag_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    """Remove a tag from a clothing item."""
    item = db.query(ClothingItem).filter(ClothingItem.id == item_id, ClothingItem.user_id == current_user["user_id"]).first()

    if not item:
        raise HTTPException(status_code=404, detail="Clothing item not found")

    link = db.query(ItemTag).filter(ItemTag.clothing_item_id == item_id, ItemTag.tag_id == tag_id).first()

    if not link:
        raise HTTPException(status_code=404, detail="Tag not assigned to this item")

    db.delete(link)
    db.commit()

    return {"message": "Tag removed from item"}
