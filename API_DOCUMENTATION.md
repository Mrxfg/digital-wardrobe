# Digital Wardrobe API Documentation
---

## 🔐 Authentication

All endpoints (except `/auth/telegram` and `/health`) require JWT authentication.

**Header Format:**
```http
Authorization: Bearer {your_jwt_token}
```

### 1. Telegram Login

**Endpoint:** `POST /auth/telegram`

**Description:** Authenticate via Telegram Mini App. Creates new user or updates existing one.

**Request Body:**
```json
{
  "telegram_id": 123456789,
  "username": "john_doe",
  "first_name": "John",
  "avatar_url": "https://t.me/i/userpic/320/example.jpg"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Status Codes:**
- `200 OK` - Successful authentication
- `422 Unprocessable Entity` - Invalid request body

---

### 2. Get Current User

**Endpoint:** `GET /auth/me`

**Description:** Get information about the currently authenticated user.

**Headers:**
```http
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "id": 1,
  "telegram_id": 123456789,
  "username": "john_doe",
  "first_name": "John",
  "avatar_url": "https://t.me/i/userpic/320/example.jpg",
  "created_at": "2026-06-19T10:00:00"
}
```

**Status Codes:**
- `200 OK` - Success
- `401 Unauthorized` - Invalid or missing token

---

## 👕 Clothes Endpoints

### 3. Get All Clothes

**Endpoint:** `GET /clothes`

**Description:** Get list of user's clothing items with optional filters.

**Query Parameters (all optional):**
- `name` (string) - Search by name (partial match)
- `category` (string) - Filter by category
- `color` (string) - Filter by color
- `season` (string) - Filter by season
- `material` (string) - Filter by material

**Example Request:**
```http
GET /clothes?name=shirt&category=tops&color=blue&season=summer&material=cotton
```

**Response:**
```json
[
  {
    "id": 1,
    "user_id": 1,
    "name": "Blue T-shirt",
    "category": "tops",
    "color": "blue",
    "season": "summer",
    "material": "cotton",
    "image_url": "/uploads/image_abc123.png",
    "original_image_url": "/uploads/original_abc123.jpg",
    "is_deleted": false,
    "created_at": "2026-06-19T10:00:00"
  }
]
```

**Status Codes:**
- `200 OK` - Success
- `401 Unauthorized` - Not authenticated

---

### 4. Get Clothing by ID

**Endpoint:** `GET /clothes/{item_id}`

**Description:** Get specific clothing item by ID.

**Path Parameters:**
- `item_id` (integer) - Clothing item ID

**Response:** Same as single item in Get All Clothes

**Status Codes:**
- `200 OK` - Success
- `404 Not Found` - Clothing item not found
- `401 Unauthorized` - Not authenticated

---

### 5. Create Clothing

**Endpoint:** `POST /clothes`

**Description:** Add new clothing item to wardrobe.

**Request Body:**
```json
{
  "name": "Blue T-shirt",
  "category": "tops",
  "color": "blue",
  "season": "summer",
  "material": "cotton",
  "image_url": "/uploads/image_abc123.png",
  "original_image_url": "/uploads/original_abc123.jpg"
}
```

**Response:**
```json
{
  "id": 1,
  "user_id": 1,
  "name": "Blue T-shirt",
  "category": "tops",
  "color": "blue",
  "season": "summer",
  "material": "cotton",
  "image_url": "/uploads/image_abc123.png",
  "original_image_url": "/uploads/original_abc123.jpg",
  "is_deleted": false,
  "created_at": "2026-06-19T10:00:00"
}
```

**Status Codes:**
- `200 OK` - Success
- `401 Unauthorized` - Not authenticated
- `422 Unprocessable Entity` - Invalid request body

---

### 6. Update Clothing

**Endpoint:** `PATCH /clothes/{item_id}`

**Description:** Update clothing item information (all fields optional).

**Path Parameters:**
- `item_id` (integer) - Clothing item ID

**Request Body (all fields optional):**
```json
{
  "name": "Updated name",
  "category": "bottoms",
  "color": "red",
  "season": "winter",
  "material": "wool"
}
```

**Response:** Updated clothing item object

**Status Codes:**
- `200 OK` - Success
- `404 Not Found` - Clothing item not found
- `401 Unauthorized` - Not authenticated

---

### 7. Delete Clothing (Soft Delete)

**Endpoint:** `DELETE /clothes/{item_id}`

**Description:** Move clothing item to trash (soft delete, `is_deleted=true`). Item can be restored.

**Path Parameters:**
- `item_id` (integer) - Clothing item ID

**Response:**
```json
{
  "message": "Clothing item deleted successfully"
}
```

**Status Codes:**
- `200 OK` - Success
- `404 Not Found` - Clothing item not found
- `401 Unauthorized` - Not authenticated

---

### 8. Get Trash

**Endpoint:** `GET /clothes/trash`

**Description:** Get all deleted clothing items (trash bin).

**Response:** Array of deleted clothing items

**Status Codes:**
- `200 OK` - Success
- `401 Unauthorized` - Not authenticated

---

### 9. Restore Clothing

**Endpoint:** `POST /clothes/{item_id}/restore`

**Description:** Restore clothing item from trash.

**Path Parameters:**
- `item_id` (integer) - Clothing item ID

**Response:**
```json
{
  "message": "Clothing item restored successfully"
}
```

**Status Codes:**
- `200 OK` - Success
- `404 Not Found` - Clothing item not found in trash
- `401 Unauthorized` - Not authenticated

---

### 10. Permanent Delete

**Endpoint:** `DELETE /clothes/{item_id}/permanent`

**Description:** Permanently delete clothing item from database. Only works for items already in trash. **This action cannot be undone.**

**Path Parameters:**
- `item_id` (integer) - Clothing item ID

**Response:**
```json
{
  "message": "Clothing item permanently deleted"
}
```

**Status Codes:**
- `200 OK` - Success
- `404 Not Found` - Clothing item not found in trash
- `401 Unauthorized` - Not authenticated

---

## 👔 Outfits Endpoints

### 11. Get All Outfits

**Endpoint:** `GET /outfits`

**Description:** Get all user's outfit collections.

**Query Parameters:**
- `name` (string, optional) - Search by name

**Example Request:**
```http
GET /outfits?name=casual
```

**Response:**
```json
[
  {
    "id": 1,
    "user_id": 1,
    "name": "Casual Friday",
    "created_at": "2026-06-19T10:00:00"
  }
]
```

**Status Codes:**
- `200 OK` - Success
- `401 Unauthorized` - Not authenticated

---

### 12. Get Outfit by ID

**Endpoint:** `GET /outfits/{outfit_id}`

**Description:** Get specific outfit by ID.

**Path Parameters:**
- `outfit_id` (integer) - Outfit ID

**Response:** Single outfit object

**Status Codes:**
- `200 OK` - Success
- `404 Not Found` - Outfit not found
- `401 Unauthorized` - Not authenticated

---

### 13. Create Outfit

**Endpoint:** `POST /outfits`

**Description:** Create new outfit collection.

**Request Body:**
```json
{
  "name": "Casual Friday"
}
```

**Response:**
```json
{
  "id": 1,
  "user_id": 1,
  "name": "Casual Friday",
  "created_at": "2026-06-19T10:00:00"
}
```

**Status Codes:**
- `200 OK` - Success
- `401 Unauthorized` - Not authenticated
- `422 Unprocessable Entity` - Invalid request body

---

### 14. Update Outfit

**Endpoint:** `PATCH /outfits/{outfit_id}`

**Description:** Update outfit name.

**Path Parameters:**
- `outfit_id` (integer) - Outfit ID

**Request Body:**
```json
{
  "name": "New Outfit Name"
}
```

**Response:** Updated outfit object

**Status Codes:**
- `200 OK` - Success
- `404 Not Found` - Outfit not found
- `401 Unauthorized` - Not authenticated

---

### 15. Delete Outfit

**Endpoint:** `DELETE /outfits/{outfit_id}`

**Description:** Delete outfit collection. Automatically removes all item associations (CASCADE delete).

**Path Parameters:**
- `outfit_id` (integer) - Outfit ID

**Response:**
```json
{
  "message": "Outfit deleted successfully"
}
```

**Status Codes:**
- `200 OK` - Success
- `404 Not Found` - Outfit not found
- `401 Unauthorized` - Not authenticated

---

### 16. Add Item to Outfit

**Endpoint:** `POST /outfits/{outfit_id}/items`

**Description:** Add clothing item to outfit collection.

**Path Parameters:**
- `outfit_id` (integer) - Outfit ID

**Request Body:**
```json
{
  "clothing_item_id": 5
}
```

**Response:**
```json
{
  "id": 1,
  "outfit_id": 1,
  "clothing_item_id": 5
}
```

**Status Codes:**
- `200 OK` - Success
- `404 Not Found` - Outfit or clothing item not found
- `400 Bad Request` - Item already exists in outfit
- `401 Unauthorized` - Not authenticated

---

### 17. Get Outfit Items

**Endpoint:** `GET /outfits/{outfit_id}/items`

**Description:** Get all clothing items in outfit.

**Path Parameters:**
- `outfit_id` (integer) - Outfit ID

**Response:** Array of clothing item objects

**Status Codes:**
- `200 OK` - Success
- `404 Not Found` - Outfit not found
- `401 Unauthorized` - Not authenticated

---

### 18. Remove Item from Outfit

**Endpoint:** `DELETE /outfits/{outfit_id}/items/{item_id}`

**Description:** Remove clothing item from outfit.

**Path Parameters:**
- `outfit_id` (integer) - Outfit ID
- `item_id` (integer) - Clothing item ID

**Response:**
```json
{
  "message": "Item removed from outfit"
}
```

**Status Codes:**
- `200 OK` - Success
- `404 Not Found` - Outfit or item not found in outfit
- `401 Unauthorized` - Not authenticated

---

## 💼 Capsules Endpoints

### 19. Get All Capsules

**Endpoint:** `GET /capsules`

**Description:** Get all user's capsule wardrobes.

**Query Parameters:**
- `name` (string, optional) - Search by name

**Example Request:**
```http
GET /capsules?name=winter
```

**Response:**
```json
[
  {
    "id": 1,
    "user_id": 1,
    "name": "Winter Essentials",
    "season": "winter",
    "created_at": "2026-06-19T10:00:00"
  }
]
```

**Status Codes:**
- `200 OK` - Success
- `401 Unauthorized` - Not authenticated

---

### 20. Get Capsule by ID

**Endpoint:** `GET /capsules/{capsule_id}`

**Description:** Get specific capsule wardrobe by ID.

**Path Parameters:**
- `capsule_id` (integer) - Capsule ID

**Response:** Single capsule object

**Status Codes:**
- `200 OK` - Success
- `404 Not Found` - Capsule not found
- `401 Unauthorized` - Not authenticated

---

### 21. Create Capsule

**Endpoint:** `POST /capsules`

**Description:** Create new capsule wardrobe (maximum 8 items per capsule).

**Request Body:**
```json
{
  "name": "Winter Essentials",
  "season": "winter"
}
```

**Response:**
```json
{
  "id": 1,
  "user_id": 1,
  "name": "Winter Essentials",
  "season": "winter",
  "created_at": "2026-06-19T10:00:00"
}
```

**Status Codes:**
- `200 OK` - Success
- `401 Unauthorized` - Not authenticated
- `422 Unprocessable Entity` - Invalid request body

---

### 22. Update Capsule

**Endpoint:** `PATCH /capsules/{capsule_id}`

**Description:** Update capsule information.

**Path Parameters:**
- `capsule_id` (integer) - Capsule ID

**Request Body (all fields optional):**
```json
{
  "name": "New Capsule Name",
  "season": "spring"
}
```

**Response:** Updated capsule object

**Status Codes:**
- `200 OK` - Success
- `404 Not Found` - Capsule not found
- `401 Unauthorized` - Not authenticated

---

### 23. Delete Capsule

**Endpoint:** `DELETE /capsules/{capsule_id}`

**Description:** Delete capsule wardrobe. Automatically removes all item associations (CASCADE delete).

**Path Parameters:**
- `capsule_id` (integer) - Capsule ID

**Response:**
```json
{
  "message": "Capsule deleted successfully"
}
```

**Status Codes:**
- `200 OK` - Success
- `404 Not Found` - Capsule not found
- `401 Unauthorized` - Not authenticated

---

### 24. Add Item to Capsule

**Endpoint:** `POST /capsules/{capsule_id}/items`

**Description:** Add clothing item to capsule wardrobe. **Maximum 8 items per capsule.**

**Path Parameters:**
- `capsule_id` (integer) - Capsule ID

**Request Body:**
```json
{
  "clothing_item_id": 3
}
```

**Response:**
```json
{
  "id": 1,
  "capsule_id": 1,
  "clothing_item_id": 3
}
```

**Status Codes:**
- `200 OK` - Success
- `404 Not Found` - Capsule or clothing item not found
- `400 Bad Request` - Capsule already has 8 items or item already exists
- `401 Unauthorized` - Not authenticated

**Error Example:**
```json
{
  "detail": "Capsule can contain maximum 8 items"
}
```

---

### 25. Get Capsule Items

**Endpoint:** `GET /capsules/{capsule_id}/items`

**Description:** Get all clothing items in capsule.

**Path Parameters:**
- `capsule_id` (integer) - Capsule ID

**Response:** Array of clothing item objects

**Status Codes:**
- `200 OK` - Success
- `404 Not Found` - Capsule not found
- `401 Unauthorized` - Not authenticated

---

### 26. Remove Item from Capsule

**Endpoint:** `DELETE /capsules/{capsule_id}/items/{item_id}`

**Description:** Remove clothing item from capsule.

**Path Parameters:**
- `capsule_id` (integer) - Capsule ID
- `item_id` (integer) - Clothing item ID

**Response:**
```json
{
  "message": "Item removed from capsule"
}
```

**Status Codes:**
- `200 OK` - Success
- `404 Not Found` - Capsule or item not found in capsule
- `401 Unauthorized` - Not authenticated

---

## 📅 Wear Records Endpoints

### 27. Create Wear Record

**Endpoint:** `POST /wear-records`

**Description:** Record when an outfit was worn (for statistics and analytics).

**Request Body:**
```json
{
  "outfit_id": 1,
  "worn_date": "2026-06-19"
}
```

**Response:**
```json
{
  "id": 1,
  "user_id": 1,
  "outfit_id": 1,
  "worn_date": "2026-06-19",
  "created_at": "2026-06-19T10:00:00"
}
```

**Status Codes:**
- `200 OK` - Success
- `404 Not Found` - Outfit not found
- `401 Unauthorized` - Not authenticated
- `422 Unprocessable Entity` - Invalid request body

---

### 28. Get All Wear Records

**Endpoint:** `GET /wear-records`

**Description:** Get complete history of outfit wear records.

**Response:**
```json
[
  {
    "id": 1,
    "user_id": 1,
    "outfit_id": 1,
    "worn_date": "2026-06-19",
    "created_at": "2026-06-19T10:00:00"
  }
]
```

**Status Codes:**
- `200 OK` - Success
- `401 Unauthorized` - Not authenticated

---

### 29. Get Wear Record by ID

**Endpoint:** `GET /wear-records/{record_id}`

**Description:** Get specific wear record by ID.

**Path Parameters:**
- `record_id` (integer) - Wear record ID

**Response:** Single wear record object

**Status Codes:**
- `200 OK` - Success
- `404 Not Found` - Wear record not found
- `401 Unauthorized` - Not authenticated

---

### 30. Delete Wear Record

**Endpoint:** `DELETE /wear-records/{record_id}`

**Description:** Delete wear record from history.

**Path Parameters:**
- `record_id` (integer) - Wear record ID

**Response:**
```json
{
  "message": "Wear record deleted successfully"
}
```

**Status Codes:**
- `200 OK` - Success
- `404 Not Found` - Wear record not found
- `401 Unauthorized` - Not authenticated

---

## 📤 Upload Endpoint

### 31. Upload Image

**Endpoint:** `POST /upload/image`

**Description:** Upload clothing image with automatic background removal.

**Request:**
- **Content-Type:** `multipart/form-data`
- **Field name:** `file`
- **Supported formats:** JPG, JPEG, PNG, HEIC, HEIF
- **Max file size:** Recommended under 10MB

**Example using curl:**
```bash
curl -X POST "http://186.246.5.37:8000/upload/image" \
  -H "Authorization: Bearer {token}" \
  -F "file=@/path/to/image.jpg"
```

**Response:**
```json
{
  "image_url": "/uploads/image_abc123.png",
  "original_image_url": "/uploads/original_abc123.jpg"
}
```

**Features:**
- ✅ Automatic background removal (rembg AI)
- ✅ HEIC/HEIF support (iPhone photos)
- ✅ Image compression
- ✅ Saves both original and processed versions

**Status Codes:**
- `200 OK` - Success
- `400 Bad Request` - Invalid file format or no file provided
- `401 Unauthorized` - Not authenticated
- `413 Payload Too Large` - File too large

**Error Example:**
```json
{
  "detail": "Only image files are allowed (jpg, jpeg, png, heic, heif)"
}
```

---

## 🏥 Health Check

### 32. Health Check

**Endpoint:** `GET /health`

**Description:** Check API health status (no authentication required).

**Response:**
```json
{
  "status": "healthy",
  "service": "digital-wardrobe-api",
  "version": "1.0.0"
}
```

**Status Codes:**
- `200 OK` - API is healthy and running

---

## ⚠️ Error Responses

### Common Error Formats

**401 Unauthorized:**
```json
{
  "detail": "Not authenticated"
}
```

**404 Not Found:**
```json
{
  "detail": "Clothing item not found"
}
```

**400 Bad Request:**
```json
{
  "detail": "Item already exists in outfit"
}
```

**422 Unprocessable Entity:**
```json
{
  "detail": [
    {
      "loc": ["body", "name"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

**500 Internal Server Error:**
```json
{
  "detail": "Internal server error"
}
```

---

## 📊 Database Schema

### Tables Overview

**users**
- `id` - Primary key
- `telegram_id` - Unique Telegram user ID
- `username` - Telegram username
- `first_name` - User's first name
- `avatar_url` - Profile picture URL
- `created_at` - Registration timestamp

**clothing_items**
- `id` - Primary key
- `user_id` - Foreign key to users
- `name` - Clothing name
- `category` - Category (tops, bottoms, etc.)
- `color` - Color
- `season` - Season (summer, winter, etc.)
- `material` - Material type
- `image_url` - Processed image URL
- `original_image_url` - Original image URL
- `is_deleted` - Soft delete flag
- `created_at` - Creation timestamp

**outfits**
- `id` - Primary key
- `user_id` - Foreign key to users
- `name` - Outfit name
- `created_at` - Creation timestamp

**outfit_items**
- `id` - Primary key
- `outfit_id` - Foreign key to outfits (CASCADE delete)
- `clothing_item_id` - Foreign key to clothing_items (CASCADE delete)

**capsules**
- `id` - Primary key
- `user_id` - Foreign key to users
- `name` - Capsule name
- `season` - Season
- `created_at` - Creation timestamp

**capsule_items**
- `id` - Primary key
- `capsule_id` - Foreign key to capsules (CASCADE delete)
- `clothing_item_id` - Foreign key to clothing_items (CASCADE delete)
- **Limit:** Maximum 8 items per capsule

**wear_records**
- `id` - Primary key
- `user_id` - Foreign key to users
- `outfit_id` - Foreign key to outfits (CASCADE delete)
- `worn_date` - Date when outfit was worn
- `created_at` - Record creation timestamp

---

## 🔒 Security Features

- ✅ JWT authentication for all protected endpoints
- ✅ CORS middleware (configured for Telegram Mini App)
- ✅ User isolation (users can only access their own data)
- ✅ Cascade deletes for data integrity
- ✅ Soft deletes for clothing items (trash bin functionality)
- ✅ Input validation with Pydantic schemas
- ✅ SQL injection protection via SQLAlchemy ORM

---

## 🚀 Deployment Information

**Production Server:**
- **Location:** `/opt/digital-wardrobe`
- **Branch:** `feature/image-upload`

**Docker Services:**
- `wardrobe_db` - PostgreSQL 15
- `wardrobe_backend` - FastAPI (Python 3.12)

**Deployment Commands:**
```bash
# Start services
docker compose up -d

# View logs
docker compose logs -f backend

# Restart backend
docker compose restart backend

# Stop all services
docker compose down
```

---
## 📦 Dependencies

**Core:**
- FastAPI - Web framework
- Uvicorn - ASGI server
- SQLAlchemy - ORM
- psycopg2-binary - PostgreSQL driver

**Authentication:**
- python-jose - JWT handling
- passlib - Password hashing

**Image Processing:**
- Pillow - Image manipulation
- pillow-heif - HEIC/HEIF support
- rembg[cpu] - Background removal AI

**Other:**
- python-dotenv - Environment variables
- python-multipart - File upload support

---

## 📞 Support & Resources

- **Interactive API Docs:** `http://186.246.5.37:8000/docs`
- **GitHub Repository:** `https://github.com/Mrxfg/digital-wardrobe`
- **Deployment Guide:** See `DEPLOYMENT.md`

---

**Last Updated:** 2026-06-19  
**API Version:** 1.0.0  
**Documentation Version:** 1.0.0
