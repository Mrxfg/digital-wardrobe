import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.client.session.aiohttp import AiohttpSession
from aiohttp import BasicAuth

# --- Конфигурация ---
TOKEN = "YOUR_API_TOKEN"
MINI_APP_URL = "YOUR_LINK"

logging.basicConfig(level=logging.INFO)

dp = Dispatcher()

@dp.message(CommandStart())
async def command_start_handler(message: types.Message):
    user_name = message.from_user.first_name or "друг"

    welcome_text = (
        f"Привет, {user_name}! 👋\n\n"
        "Добро пожаловать в твой цифровой гардероб.\n\n"
        "Здесь ты можешь:\n"
        "• хранить свои вещи\n"
        "• создавать стильные образы\n"
        "• быстро подбирать луки\n\n"
        "Нажми кнопку ниже, чтобы открыть приложение."
    )

    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(
            text="Открыть гардероб",
            url=MINI_APP_URL
        )
    )

    await message.answer(
        welcome_text,
        reply_markup=builder.as_markup()
    )


@dp.message(Command("wardrobe"))
async def command_wardrobe_handler(message: types.Message):
    text = "Твой гардероб всегда под рукой! Нажми на кнопку ниже, чтобы заглянуть внутрь 👇"
    
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(
            text="Открыть гардероб",
            url=MINI_APP_URL
        )
    )
    
    await message.answer(text, reply_markup=builder.as_markup())


@dp.message(Command("help"))
async def command_help_handler(message: types.Message):
    help_text = (
        "🤖 **Доступные команды:**\n"
        "/start — Перезапустить бота и получить приветствие\n"
        "/wardrobe — Быстрая ссылка для открытия гардероба\n"
        "/settings — Настройки профиля и локации\n"
        "/help — Показать это меню помощи\n\n"
 )
    await message.answer(help_text, parse_mode="Markdown")

@dp.message(Command("settings"))
async def command_settings_handler(message: types.Message):
    settings_text = (
        "⚙️ **Настройки профиля**\n\n"
        "Текущая локация: _Не определена_\n\n"
        "Выбор города и синхронизация погоды для подбора луков сейчас находятся в разработке. "
        "Эта функция появится в следующем обновлении! 🚀"
    )
    await message.answer(settings_text, parse_mode="Markdown")

@dp.message()
async def unknown_message_handler(message: types.Message):
    await message.answer(
        "Я пока понимаю только эти команды:\n\n"
        "/wardrobe — открыть цифровой гардероб \n"
        "/settings — настройки профиля\n"
        "/help — помощь и поддержка"
    )


async def set_bot_commands(bot: Bot):
    commands = [
        types.BotCommand(command="start", description="Запустить бота"),
        types.BotCommand(command="wardrobe", description="Открыть цифровой гардероб"),
        types.BotCommand(command="settings", description="Настройки локации"),
        types.BotCommand(command="help", description="Помощь и контакты поддержки"),
    ]
    await bot.set_my_commands(commands)


async def main():
    proxy_url = "http://PROXY_IP:PORT"
    proxy_auth = BasicAuth("PROXY_LOGIN", "PROXY_PASSWORD")
    
    bot_session = AiohttpSession(
        proxy=(proxy_url, proxy_auth)
    )
    
    bot = Bot(token=TOKEN, session=bot_session)
    
    await set_bot_commands(bot)
    
    me = await bot.get_me()
    print(f"Бот подключился: @{me.username}")
    
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Бот остановлен вручную")
