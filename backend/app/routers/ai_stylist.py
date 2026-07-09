import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.ai_chat import AiChatHistory
from app.models.clothing_item import ClothingItem
from app.models.users import User
from app.schemas.ai_chat import ChatRequest, ChatResponse
from app.services.ai_stylist import chat_with_ai
from app.services.weather import fetch_weather, get_city_name

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai-stylist", tags=["AI Stylist"])


@router.post("/chat", response_model=ChatResponse)
async def ai_chat(
    body: ChatRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Chat with the AI stylist. Saves conversation history in the database."""

    if not body.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    user_id = current_user["user_id"]

    # Load user's wardrobe for context
    items = (
        db.query(ClothingItem)
        .filter(
            ClothingItem.user_id == user_id,
            ClothingItem.is_deleted.is_(False),
        )
        .all()
    )

    # Build wardrobe text for the AI prompt
    if not items:
        wardrobe_text = "The user has no items in their wardrobe yet."
    else:
        wardrobe_lines = []
        for item in items:
            color = item.color or "unknown color"
            name = item.name or "unnamed item"
            category = item.category or "other"
            season = item.season or "any season"
            wardrobe_lines.append(f"- {name} ({color}, {category}, {season})")
        wardrobe_text = "\n".join(wardrobe_lines)

    # Fetch current weather for context
    weather_text = ""
    user = db.query(User).filter(User.id == user_id).first()
    if user and user.latitude is not None and user.longitude is not None:
        try:
            weather_data = await fetch_weather(user.latitude, user.longitude)
            if weather_data:
                city = user.city or await get_city_name(user.latitude, user.longitude) or "your location"
                weather_text = (
                    f"Current weather in {city}: {weather_data.weather_description}, "
                    f"temperature {weather_data.temperature}°C (feels like {weather_data.feels_like}°C), "
                    f"humidity {weather_data.humidity}%, wind {weather_data.wind_speed} km/h"
                )
        except Exception:
            logger.warning(f"Failed to fetch weather for user {user_id}", exc_info=True)

    # Load last 10 messages for context (5 user-assistant pairs)
    history_records = (
        db.query(AiChatHistory)
        .filter(AiChatHistory.user_id == user_id)
        .order_by(AiChatHistory.created_at.desc())
        .limit(10)
        .all()
    )
    history_records.reverse()  # chronological order

    history = [{"role": r.role, "message": r.message} for r in history_records]

    # Save user message
    user_history = AiChatHistory(user_id=user_id, role="user", message=body.message.strip())
    db.add(user_history)
    db.flush()

    # Get AI response
    reply, was_fallback = chat_with_ai(wardrobe_text, body.message.strip(), history, weather_text)

    if was_fallback:
        logger.info(f"AI chat fallback used for user {user_id}")

    # Save assistant response
    assistant_history = AiChatHistory(user_id=user_id, role="assistant", message=reply)
    db.add(assistant_history)
    db.commit()

    return ChatResponse(reply=reply)
