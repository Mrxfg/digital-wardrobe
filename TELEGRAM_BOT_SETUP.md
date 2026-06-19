# Telegram Bot Setup Guide

## 📱 Overview

This guide will help you set up and configure the Telegram Bot for Digital Wardrobe application.

## ✅ Current Bot Configuration

**Bot Token:** `your-telegram-bot-token`

**Available Commands:**
- `/start` - Welcome message and introduction
- `/help` - List of available commands
- `/settings` - User settings and profile info
- `/wardrobe` - Open Digital Wardrobe Mini App

---

## 🚀 Quick Setup

### 1. Deploy Backend API

Make sure your backend is deployed and accessible:

```bash
# On your VM (your-server-ip)
cd /opt/digital-wardrobe
docker compose up -d

# Check if bot endpoint is working
curl http://your-server-ip:8000/bot/me
```

### 2. Set Webhook

**Option A: Using curl (recommended)**

```bash
curl -X POST "http://your-server-ip:8000/bot/set-webhook" \
  -H "Content-Type: application/json" \
  -d '{"url": "http://your-server-ip:8000/bot/webhook"}'
```

**Option B: Using Telegram API directly**

```bash
curl -X POST "https://api.telegram.org/botyour-telegram-bot-token/setWebhook" \
  -H "Content-Type: application/json" \
  -d '{"url": "http://your-server-ip:8000/bot/webhook"}'
```

### 3. Verify Webhook

```bash
# Check webhook status
curl http://your-server-ip:8000/bot/webhook-info

# Expected response:
{
  "ok": true,
  "result": {
    "url": "http://your-server-ip:8000/bot/webhook",
    "has_custom_certificate": false,
    "pending_update_count": 0
  }
}
```

### 4. Test Bot

Open Telegram and send `/start` to your bot. You should receive a welcome message!

---

## 🔧 Bot Endpoints

### GET /bot/me
Get bot information.

**Response:**
```json
{
  "ok": true,
  "result": {
    "id": 8930175741,
    "is_bot": true,
    "first_name": "Digital Wardrobe",
    "username": "your_bot_username"
  }
}
```

### POST /bot/webhook
Webhook endpoint that receives updates from Telegram.

**Automatically handles:**
- `/start` - Welcome message
- `/help` - Help information
- `/settings` - User settings
- `/wardrobe` - Open Mini App

### GET /bot/webhook-info
Get current webhook configuration.

### POST /bot/set-webhook
Set webhook URL for the bot.

**Request Body:**
```json
{
  "url": "https://your-domain.com/bot/webhook"
}
```

### POST /bot/delete-webhook
Delete webhook (useful for local development with polling).

---

## 📝 Bot Commands

### /start
**Response:**
```
👋 Добро пожаловать в Digital Wardrobe!

🎯 Ваш персональный цифровой гардероб в Telegram.

📱 Используйте команды:
/wardrobe - Открыть мой гардероб
/settings - Настройки
/help - Помощь

Начните создавать свой стильный гардероб прямо сейчас! 👗👔
```

### /help
**Response:**
```
ℹ️ Помощь - Digital Wardrobe

📋 Доступные команды:

/start - Начать работу с ботом
/wardrobe - Открыть ваш гардероб (Mini App)
/settings - Настройки профиля
/help - Показать это сообщение

💡 Как использовать:
1. Добавляйте фото одежды
2. Создавайте комплекты (outfits)
3. Формируйте капсульные гардеробы
4. Отслеживайте что носили

🔗 Нужна помощь? Напишите @support
```

### /settings
**Response:**
```
⚙️ Настройки

👤 Профиль:
Имя: John
Username: @john_doe
ID: 123456789

🔔 Уведомления: Включены
🌍 Язык: Русский

Для изменения настроек откройте /wardrobe
```

### /wardrobe
Opens Telegram Mini App with inline keyboard button.

---

## 🔐 Security Considerations

### 1. Use HTTPS in Production

For production, **always use HTTPS** for webhook:

```bash
# Set webhook with HTTPS
curl -X POST "http://your-server-ip:8000/bot/set-webhook" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://your-domain.com/bot/webhook"}'
```

### 2. Verify Bot Token

Never commit bot token to public repositories. Use environment variables:

```env
BOT_TOKEN=your-telegram-bot-token
```

### 3. Validate Webhook Requests

Add webhook secret token (optional but recommended):

```bash
curl -X POST "https://api.telegram.org/bot<token>/setWebhook" \
  -d "url=https://your-domain.com/bot/webhook" \
  -d "secret_token=your_secret_here"
```

---

## 🛠️ Development & Testing

### Local Development (Without Webhook)

For local testing, you can use polling instead of webhook:

```bash
# Delete webhook
curl -X POST http://your-server-ip:8000/bot/delete-webhook

# Use telegram bot library with polling (not implemented yet)
# Example: python-telegram-bot library
```

### Testing Commands

```bash
# Test /start command via API (for debugging)
curl -X POST "https://api.telegram.org/botyour-telegram-bot-token/sendMessage" \
  -H "Content-Type: application/json" \
  -d '{
    "chat_id": YOUR_CHAT_ID,
    "text": "Test message"
  }'
```

---

## 🔄 Webhook Updates Flow

```
User sends /start
    ↓
Telegram API
    ↓
POST http://your-server-ip:8000/bot/webhook
    ↓
FastAPI processes command
    ↓
Sends response via sendMessage API
    ↓
User receives message
```

---

## ⚠️ Troubleshooting

### Webhook not receiving updates

**Check webhook status:**
```bash
curl http://your-server-ip:8000/bot/webhook-info
```

**Common issues:**
- ✅ Make sure bot endpoint is accessible from internet
- ✅ Check firewall allows port 8000
- ✅ Verify BOT_TOKEN environment variable is set
- ✅ Check Docker container is running: `docker compose ps`

### Bot not responding

**Check logs:**
```bash
docker compose logs -f backend
```

**Test bot endpoint:**
```bash
curl http://your-server-ip:8000/bot/me
```

### Invalid webhook URL

Webhook URL must:
- Use HTTP or HTTPS (not localhost)
- Be accessible from internet
- Use port 80, 88, 443, or 8443
- Have valid SSL certificate (for HTTPS)

---

## 📦 Mini App Integration

To enable `/wardrobe` command to open Mini App:

### 1. Update Mini App URL

Edit `backend/app/routers/bot.py`:

```python
{
    "text": "🚀 Открыть гардероб",
    "web_app": {"url": "https://your-mini-app-url.com"}  # Replace with actual URL
}
```

### 2. Register Mini App with BotFather

1. Open @BotFather in Telegram
2. Send `/mybots`
3. Select your bot
4. Click "Bot Settings" → "Menu Button"
5. Send Mini App URL

---

## 📊 Webhook Statistics

Check webhook performance:

```bash
# Get webhook info with stats
curl "https://api.telegram.org/botyour-telegram-bot-token/getWebhookInfo"
```

**Response includes:**
- `pending_update_count` - Queued updates
- `last_error_date` - Last error timestamp
- `last_error_message` - Error details

---

## 🎯 Acceptance Criteria Checklist

- ✅ Bot is registered and has valid API token
- ✅ Bot responds to `/start` command with welcome message
- ✅ Bot responds to `/help` command with list of commands
- ✅ Bot responds to `/settings` command with user info
- ✅ Bot responds to `/wardrobe` command
- ✅ Webhook is configured and receives updates
- ✅ Webhook URL points to correct production endpoint
- ✅ Bot token is securely stored (environment variable)

---

## 📞 Support

- **API Documentation:** http://your-server-ip:8000/docs
- **Telegram Bot API:** https://core.telegram.org/bots/api
- **Mini App Guide:** https://core.telegram.org/bots/webapps

---

**Last Updated:** 2026-06-19  
**Bot Status:** Ready for deployment ✅
