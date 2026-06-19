# Telegram Mini App Authentication Guide

## 🔐 Overview

This guide explains how to authenticate users in the Digital Wardrobe Telegram Mini App using the secure `initData` verification method.

## 🚀 Quick Start

### Frontend Integration (JavaScript)

```javascript
// Get Telegram WebApp object
const tg = window.Telegram.WebApp;

// Get initData (automatically signed by Telegram)
const initData = tg.initData;

// Send to backend for authentication
async function authenticateUser() {
    try {
        const response = await fetch('http://186.246.5.37:8000/auth/telegram-webapp', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                init_data: initData
            })
        });

        if (!response.ok) {
            throw new Error('Authentication failed');
        }

        const data = await response.json();
        
        // Store JWT token
        localStorage.setItem('access_token', data.access_token);
        
        // Now you can make authenticated requests
        console.log('Authenticated successfully!');
        
        return data.access_token;
    } catch (error) {
        console.error('Auth error:', error);
        throw error;
    }
}

// Call on app load
authenticateUser();
```

---

## 📡 API Endpoints

### 1. **POST /auth/telegram-webapp** (RECOMMENDED - Secure)

**Description:** Authenticate user via Telegram Mini App with signature verification.

**Request:**
```json
{
  "init_data": "query_id=AAHdF6IQAAAAAN0XohDhrOrc&user=%7B%22id%22%3A279058397%2C%22first_name%22%3A%22John%22%2C%22last_name%22%3A%22Doe%22%2C%22username%22%3A%22johndoe%22%2C%22language_code%22%3A%22en%22%7D&auth_date=1682343643&hash=89d6079ad6762351f38c6dbbc41bb53048019256a9443988af7a48bcad16ba31"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**How it works:**
1. Frontend gets `initData` from `Telegram.WebApp.initData`
2. Backend verifies signature using BOT_TOKEN
3. If valid, creates or updates user
4. Returns JWT token

**Status Codes:**
- `200 OK` - Success
- `401 Unauthorized` - Invalid initData or signature
- `500 Internal Server Error` - Bot token not configured

---

### 2. **POST /auth/telegram** (DEPRECATED - Insecure)

**⚠️ WARNING:** This endpoint does NOT verify Telegram signature. Use only for testing!

**Request:**
```json
{
  "telegram_id": "123456789",
  "username": "johndoe",
  "first_name": "John",
  "avatar_url": "https://t.me/i/userpic/320/example.jpg"
}
```

**Response:** Same as `/auth/telegram-webapp`

---

## 🔒 How Signature Verification Works

### Backend Process

1. **Parse initData**
   ```
   query_id=AAH...&user={...}&auth_date=1682343643&hash=89d607...
   ```

2. **Extract hash**
   ```
   received_hash = "89d6079ad6762351f38c6dbbc41bb53048019256a9443988af7a48bcad16ba31"
   ```

3. **Create data check string**
   ```
   auth_date=1682343643
   query_id=AAH...
   user={"id":279058397,...}
   ```

4. **Calculate secret key**
   ```python
   secret_key = HMAC_SHA256("WebAppData", BOT_TOKEN)
   ```

5. **Calculate hash**
   ```python
   calculated_hash = HMAC_SHA256(secret_key, data_check_string)
   ```

6. **Verify**
   ```python
   if calculated_hash == received_hash:
       # Valid! User is authenticated by Telegram
   ```

This ensures the data comes from Telegram and hasn't been tampered with.

---

## 🎯 User Story Implementation

### Scenario 1: First-time login

```javascript
// On Mini App load
window.addEventListener('DOMContentLoaded', async () => {
    const tg = window.Telegram.WebApp;
    
    // Expand to full screen
    tg.expand();
    
    try {
        // Authenticate automatically
        const token = await authenticateUser();
        
        // Check if new user
        const user = await fetchCurrentUser(token);
        
        if (user.is_new) {
            // Show welcome/onboarding
            showWelcomePage();
        } else {
            // Go to home
            showHomePage();
        }
    } catch (error) {
        // Show error
        showAuthError();
    }
});
```

### Scenario 2: Denied access

```javascript
async function authenticateUser() {
    const tg = window.Telegram.WebApp;
    
    // Check if initData is available
    if (!tg.initData) {
        // User denied access or app not opened in Telegram
        showError('Please open this app through Telegram');
        return;
    }
    
    // Continue with authentication...
}
```

### Scenario 3: Making authenticated requests

```javascript
async function getMyClothes() {
    const token = localStorage.getItem('access_token');
    
    const response = await fetch('http://186.246.5.37:8000/clothes', {
        headers: {
            'Authorization': `Bearer ${token}`
        }
    });
    
    return await response.json();
}
```

---

## 🧪 Testing

### Test with real Telegram

1. Create Mini App via @BotFather:
   ```
   /newapp
   Select your bot
   Enter app title: Digital Wardrobe
   Enter description
   Upload app icon (512x512 PNG)
   Send app URL: https://your-domain.com
   ```

2. Open Mini App in Telegram

3. Check browser console for `initData`

### Test locally (without Telegram)

**⚠️ For development only!** Use deprecated endpoint:

```javascript
async function devAuth() {
    const response = await fetch('http://localhost:8000/auth/telegram', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            telegram_id: "123456789",
            username: "testuser",
            first_name: "Test",
            avatar_url: null
        })
    });
    
    const data = await response.json();
    localStorage.setItem('access_token', data.access_token);
}
```

---

## 📱 Complete Example

```html
<!DOCTYPE html>
<html>
<head>
    <title>Digital Wardrobe</title>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
</head>
<body>
    <div id="app">
        <div id="loading">Loading...</div>
        <div id="error" style="display:none;">Authentication failed</div>
        <div id="content" style="display:none;">
            <h1>Welcome to Digital Wardrobe!</h1>
            <button id="addItem">Add First Item</button>
        </div>
    </div>

    <script>
        const API_URL = 'http://186.246.5.37:8000';
        const tg = window.Telegram.WebApp;

        // Authenticate on load
        async function init() {
            try {
                // Check if opened in Telegram
                if (!tg.initData) {
                    throw new Error('Please open in Telegram');
                }

                // Authenticate
                const response = await fetch(`${API_URL}/auth/telegram-webapp`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ init_data: tg.initData })
                });

                if (!response.ok) throw new Error('Auth failed');

                const { access_token } = await response.json();
                localStorage.setItem('token', access_token);

                // Show app content
                document.getElementById('loading').style.display = 'none';
                document.getElementById('content').style.display = 'block';

                // Notify Telegram that app is ready
                tg.ready();
                tg.expand();

            } catch (error) {
                console.error(error);
                document.getElementById('loading').style.display = 'none';
                document.getElementById('error').style.display = 'block';
            }
        }

        // Run on load
        init();
    </script>
</body>
</html>
```

---

## 🔧 Environment Setup

### Backend (.env)

```env
BOT_TOKEN=8930175741:AAFn20YgCQWSDh-avVP10H2gQrJml8-9m-I
SECRET_KEY=8f2c9a1e7d4b6f3a9c8e5d2b7f1a4c6e
ALGORITHM=HS256
DATABASE_URL=postgresql://postgres:postgres123@localhost:5432/digital_wardrobe
```

### CORS Configuration

Make sure your backend allows Telegram origins:

```python
# backend/app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*",  # For development
        "https://web.telegram.org",  # Telegram Web
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 🐛 Troubleshooting

### "Invalid Telegram authentication data"

**Causes:**
- initData is expired (valid for 24 hours)
- BOT_TOKEN is incorrect
- initData was modified

**Solution:**
- Refresh the Mini App
- Check BOT_TOKEN in .env
- Make sure initData is passed exactly as received

### "initData is empty"

**Causes:**
- App not opened through Telegram
- Running in regular browser

**Solution:**
- Open app through Telegram bot
- Use `/auth/telegram` endpoint for local testing

### CORS errors

**Solution:**
```python
allow_origins=["*"]  # For development
```

---

## 📚 Resources

- [Telegram Mini Apps Documentation](https://core.telegram.org/bots/webapps)
- [Telegram WebApp SDK](https://core.telegram.org/bots/webapps#initializing-mini-apps)
- [Validating data received via Mini Apps](https://core.telegram.org/bots/webapps#validating-data-received-via-the-mini-app)

---

## ✅ Acceptance Criteria Checklist

- ✅ Backend verifies Telegram initData signature
- ✅ New users are created automatically
- ✅ Existing users are updated on login
- ✅ JWT token is returned for authenticated requests
- ✅ Error handling for denied access
- ✅ No separate registration forms needed
- ✅ Data linked to Telegram ID

---

**Last Updated:** 2026-06-19  
**Task:** #103 Backend Telegram Auth Endpoint  
**Status:** Ready for frontend integration ✅
