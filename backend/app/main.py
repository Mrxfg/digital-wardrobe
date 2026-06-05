from fastapi import FastAPI

from app.database import Base, engine

from app.models.users import User
from app.models.clothing_item import ClothingItem
from app.models.outfit import Outfit
from app.models.outfit_item import OutfitItem
from app.models.wear_record import WearRecord

from app.routers.clothes import router as clothes_router
from app.routers.outfits import router as outfits_router

from app.routers.wear_records import router as wear_records_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Digital Wardrobe API",
    version="1.0.0"
)

app.include_router(clothes_router)
app.include_router(outfits_router)
app.include_router(wear_records_router)

@app.get("/")
def root():
    return {
        "message": "Digital Wardrobe Backend"
    }