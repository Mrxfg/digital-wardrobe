import os
from typing import Optional

from fastapi import APIRouter, Request
from pydantic import BaseModel

router = APIRouter(prefix="/bot", tags=["Telegram Bot"])

BOT_TOKEN = os.getenv("BOT_TOKEN")


class TelegramUser(BaseModel):
    id: int
    is_bot: bool
    first_name: str
    username: Optional[str] = None
    language_code: Optional[str] = None


class TelegramChat(BaseModel):
    id: int
    first_name: str
    username: Optional[str] = None
    type: str


class TelegramMessage(BaseModel):
    message_id: int
    from_: TelegramUser
    chat: TelegramChat
    date: int
    text: Optional[str] = None

    class Config:
        fields = {"from_": "from"}


class TelegramUpdate(BaseModel):
    update_id: int
    message: Optional[TelegramMessage] = None


@router.post("/webhook")
async def telegram_webhook(update: TelegramUpdate):
    """
    Handle incoming Telegram webhook updates.
    Responds to /start, /help, /settings, /wardrobe commands.
    """
    if not update.message or not update.message.text:
        return {"ok": True}

    message = update.message
    chat_id = message.chat.id
    text = message.text.strip()

    # Handle commands
    if text == "/start":
        response_text = (
            "👋 Добро пожаловать в Digital Wardrobe!\n\n"
            "🎯 Ваш персональный цифровой гардероб в Telegram.\n\n"
            "📱 Используйте команды:\n"
            "/wardrobe - Открыть мой гардероб\n"
            "/settings - Настройки\n"
            "/help - Помощь\n\n"
            "Начните создавать свой стильный гардероб прямо сейчас! 👗👔"
        )
        await send_message(chat_id, response_text)

    elif text == "/help":
        response_text = (
            "ℹ️ Помощь - Digital Wardrobe\n\n"
            "📋 Доступные команды:\n\n"
            "/start - Начать работу с ботом\n"
            "/wardrobe - Открыть ваш гардероб (Mini App)\n"
            "/settings - Настройки профиля\n"
            "/help - Показать это сообщение\n\n"
            "💡 Как использовать:\n"
            "1. Добавляйте фото одежды\n"
            "2. Создавайте комплекты (outfits)\n"
            "3. Формируйте капсульные гардеробы\n"
            "4. Отслеживайте что носили\n\n"
            "🔗 Нужна помощь? Напишите @support"
        )
        await send_message(chat_id, response_text)

    elif text == "/settings" or text == "/setting":
        response_text = (
            "⚙️ Настройки\n\n"
            "👤 Профиль:\n"
            f"Имя: {message.from_.first_name}\n"
            f"Username: @{message.from_.username or 'не указан'}\n"
            f"ID: {message.from_.id}\n\n"
            "🔔 Уведомления: Включены\n"
            "🌍 Язык: Русский\n\n"
            "Для изменения настроек откройте /wardrobe"
        )
        await send_message(chat_id, response_text)

    elif text == "/wardrobe" or text == "/warderobe":
        # Send Mini App button
        response_text = "👗 Откройте ваш цифровой гардероб:"
        keyboard = {
            "inline_keyboard": [
                [
                    {
                        "text": "🚀 Открыть гардероб",
                        "web_app": {"url": "https://your-mini-app-url.com"},  # Replace with actual Mini App URL
                    }
                ]
            ]
        }
        await send_message(chat_id, response_text, reply_markup=keyboard)

    else:
        # Unknown command
        response_text = "🤔 Не понимаю эту команду.\n\n" "Используйте /help чтобы увидеть доступные команды."
        await send_message(chat_id, response_text)

    return {"ok": True}


async def send_message(chat_id: int, text: str, reply_markup: Optional[dict] = None):
    """Send message to Telegram user via Bot API."""
    import httpx

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}

    if reply_markup:
        payload["reply_markup"] = reply_markup

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload, timeout=10.0)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error sending message: {e}")
            return None


@router.get("/webhook-info")
async def get_webhook_info():
    """Get current webhook configuration from Telegram."""
    import httpx

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getWebhookInfo"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, timeout=10.0)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}


@router.post("/set-webhook")
async def set_webhook(request: Request):
    """
    Set webhook URL for the bot.
    Call this endpoint with: {"url": "https://your-domain.com/bot/webhook"}
    """
    import httpx

    data = await request.json()
    webhook_url = data.get("url")

    if not webhook_url:
        return {"error": "URL is required"}

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook"
    payload = {"url": webhook_url, "allowed_updates": ["message"]}

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload, timeout=10.0)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}


@router.post("/delete-webhook")
async def delete_webhook():
    """Delete webhook (useful for development with polling)."""
    import httpx

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, timeout=10.0)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}


@router.get("/me")
async def get_bot_info():
    """Get bot information."""
    import httpx

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getMe"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, timeout=10.0)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}
