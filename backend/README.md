# Digital Wardrobe Backend

![Backend CI](https://github.com/YOUR_USERNAME/digital-wardrobe/workflows/Backend%20CI/badge.svg)
![Code Quality](https://github.com/YOUR_USERNAME/digital-wardrobe/workflows/Code%20Quality%20Check/badge.svg)

Telegram Mini App backend for personal wardrobe management with outfit creation, wear tracking, and AI-powered image processing.

## Features

- 👕 Clothing item management with categories, colors, seasons
- 👔 Outfit creation and organization
- 📸 Image upload with automatic background removal
- 📊 Wear tracking and history
- 🎒 Capsule wardrobe collections
- 🔐 Telegram-based authentication with JWT
- 🗑️ Soft delete with trash and restore functionality

## Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: JWT (python-jose)
- **Image Processing**: Pillow, rembg (background removal)
- **Server**: Uvicorn

## Quick Start

### Prerequisites
- Python 3.12+
- PostgreSQL 12+
- pip

### Installation

1. Clone the repository:
```bash
git clone https://github.com/YOUR_USERNAME/digital-wardrobe.git
cd digital-wardrobe/backend
```

2. Create virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Run the server:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## Environment Variables

Create a `.env` file in the backend directory:

```env
DATABASE_URL=postgresql://username:password@localhost:5432/digital_wardrobe
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
BOT_TOKEN=your-telegram-bot-token
```

## API Documentation

Once running, access interactive API docs at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Project Structure

```
backend/
├── app/
│   ├── dependencies/     # Dependency injection (auth)
│   ├── models/          # SQLAlchemy models
│   ├── routers/         # API endpoints
│   ├── schemas/         # Pydantic schemas
│   ├── services/        # Business logic
│   ├── utils/           # Utilities
│   ├── database.py      # Database configuration
│   └── main.py          # FastAPI application
├── uploads/             # Uploaded images
├── .env.example         # Environment template
├── requirements.txt     # Production dependencies
└── requirements-dev.txt # Development dependencies
```

## Development

### Install dev dependencies:
```bash
pip install -r requirements-dev.txt
```

### Code formatting:
```bash
black app
isort app
```

### Linting:
```bash
flake8 app --max-line-length=127
```

### Security scan:
```bash
bandit -r app
```

## CI/CD

The project uses GitHub Actions for:
- ✅ Automated testing on push/PR
- ✅ Code quality checks
- ✅ Security vulnerability scanning
- ✅ Automated deployment to production

See `.github/workflows/README.md` for details.

## API Endpoints

### Authentication
- `POST /auth/telegram` - Telegram login
- `GET /auth/me` - Get current user

### Clothing Items
- `GET /clothes` - List items (with filters)
- `POST /clothes` - Create item
- `GET /clothes/{id}` - Get item
- `PATCH /clothes/{id}` - Update item
- `DELETE /clothes/{id}` - Soft delete item
- `GET /clothes/trash` - List deleted items
- `POST /clothes/{id}/restore` - Restore from trash
- `DELETE /clothes/{id}/permanent` - Permanently delete

### Outfits
- `GET /outfits` - List outfits
- `POST /outfits` - Create outfit
- `GET /outfits/{id}` - Get outfit
- `PATCH /outfits/{id}` - Update outfit
- `DELETE /outfits/{id}` - Delete outfit
- `GET /outfits/{id}/items` - List outfit items
- `POST /outfits/{id}/items` - Add item to outfit
- `DELETE /outfits/{id}/items/{item_id}` - Remove item from outfit

### Capsules
- `GET /capsules` - List capsules
- `POST /capsules` - Create capsule
- `GET /capsules/{id}` - Get capsule
- `PATCH /capsules/{id}` - Update capsule
- `DELETE /capsules/{id}` - Delete capsule
- `GET /capsules/{id}/items` - List capsule items
- `POST /capsules/{id}/items` - Add item to capsule (max 8)
- `DELETE /capsules/{id}/items/{item_id}` - Remove item from capsule

### Wear Records
- `GET /wear-records` - List wear records
- `POST /wear-records` - Create wear record
- `GET /wear-records/{id}` - Get wear record
- `DELETE /wear-records/{id}` - Delete wear record

### Upload
- `POST /upload` - Upload image (auto background removal)

## Database Schema

- **users** - User accounts (Telegram auth)
- **clothing_items** - Wardrobe items
- **outfits** - Outfit collections
- **outfit_items** - Items in outfits (junction table)
- **capsules** - Capsule wardrobes
- **capsule_items** - Items in capsules (junction table)
- **wear_records** - Outfit wear history

## Security Features

- JWT-based authentication
- User ownership validation on all endpoints
- File upload validation (size, type, content)
- SQL injection protection (parameterized queries)
- Environment secrets properly loaded
- Soft delete prevents accidental data loss
- CASCADE deletes for data integrity

## License

MIT License

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Support

For issues and questions, please open an issue on GitHub.
