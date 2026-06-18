from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.database import Base, engine
from app.models.capsule import Capsule  # noqa: F401
from app.models.capsule_item import CapsuleItem  # noqa: F401
from app.models.clothing_item import ClothingItem  # noqa: F401
from app.models.outfit import Outfit  # noqa: F401
from app.models.outfit_item import OutfitItem  # noqa: F401
from app.models.users import User  # noqa: F401
from app.models.wear_record import WearRecord  # noqa: F401
from app.routers.auth import router as auth_router
from app.routers.capsules import router as capsules_router
from app.routers.clothes import router as clothes_router
from app.routers.outfits import router as outfits_router
from app.routers.upload import router as upload_router
from app.routers.wear_records import router as wear_records_router
from app.routers.weather import router as weather_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Digital Wardrobe API", version="1.0.0")

# CORS configuration for Telegram Mini App
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific Telegram origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(clothes_router)
app.include_router(outfits_router)
app.include_router(wear_records_router)
app.include_router(auth_router)
app.include_router(capsules_router)
app.include_router(upload_router)
app.include_router(weather_router)

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


@app.get("/")
def root():
    return {"message": "Digital Wardrobe Backend"}


@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "digital-wardrobe-api", "version": "1.0.0"}
