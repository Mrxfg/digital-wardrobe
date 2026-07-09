"""Unit and integration tests for AI Stylist Chat (PBI-301).

Covers the chat endpoint, history persistence, fallback responses,
validation, and error handling.
"""

from unittest.mock import patch

from app.models.ai_chat import AiChatHistory
from app.models.clothing_item import ClothingItem


def _seed_wardrobe(db_session):
    """Add a few clothing items for user 1 so the AI has context."""
    items = [
        ClothingItem(id=1, user_id=1, name="Blue Shirt", category="top", color="blue", season="summer", material="cotton"),
        ClothingItem(id=2, user_id=1, name="Black Jeans", category="bottom", color="black", season="all", material="denim"),
        ClothingItem(
            id=3, user_id=1, name="White Sneakers", category="shoes", color="white", season="all", material="leather"
        ),
    ]
    for item in items:
        db_session.add(item)
    db_session.commit()


# ===================================================================
# POST /ai-stylist/chat
# ===================================================================


class TestAiChat:
    """Scenario 1 & 2 — chat with AI stylist."""

    def test_chat_returns_reply(self, client, db_session):
        """Valid message with wardrobe context → 200 with reply."""
        _seed_wardrobe(db_session)

        with patch("app.routers.ai_stylist.chat_with_ai") as mock_chat:
            mock_chat.return_value = ("I recommend your Blue Shirt with Black Jeans!", False)

            resp = client.post("/ai-stylist/chat", json={"message": "What should I wear?"})

        assert resp.status_code == 200
        data = resp.json()
        assert "reply" in data
        assert "Blue Shirt" in data["reply"]

    def test_chat_saves_history(self, client, db_session):
        """Messages are saved to ai_chat_history table."""
        _seed_wardrobe(db_session)

        with patch("app.routers.ai_stylist.chat_with_ai") as mock_chat:
            mock_chat.return_value = ("Wear your Blue Shirt!", False)

            resp = client.post("/ai-stylist/chat", json={"message": "Style advice please"})

        assert resp.status_code == 200

        # Check history was saved
        records = db_session.query(AiChatHistory).filter(AiChatHistory.user_id == 1).all()
        assert len(records) == 2
        assert records[0].role == "user"
        assert records[0].message == "Style advice please"
        assert records[1].role == "assistant"
        assert records[1].message == "Wear your Blue Shirt!"

    def test_chat_follow_up_uses_history(self, client, db_session):
        """Follow-up question keeps context from previous messages (Scenario 3)."""
        _seed_wardrobe(db_session)

        # Pre-seed some history
        db_session.add(AiChatHistory(user_id=1, role="user", message="What should I wear for casual?"))
        db_session.add(AiChatHistory(user_id=1, role="assistant", message="Try Blue Shirt with Black Jeans."))
        db_session.commit()

        with patch("app.routers.ai_stylist.chat_with_ai") as mock_chat:
            mock_chat.return_value = (
                "Yes! Your Blue Shirt goes great with White Sneakers.",
                False,
            )

            resp = client.post(
                "/ai-stylist/chat",
                json={"message": "Can I wear this with white sneakers?"},
            )

        assert resp.status_code == 200
        data = resp.json()
        assert "White Sneakers" in data["reply"]

        # Verify follow-up was also saved
        records = db_session.query(AiChatHistory).filter(AiChatHistory.user_id == 1).all()
        assert len(records) == 4

    def test_chat_empty_message(self, client):
        """Empty message → 400."""
        resp = client.post("/ai-stylist/chat", json={"message": "   "})
        assert resp.status_code == 400

    def test_chat_fallback_when_ai_unavailable(self, client, db_session):
        """AI service down → 200 with fallback text."""
        _seed_wardrobe(db_session)

        with patch("app.routers.ai_stylist.chat_with_ai") as mock_chat:
            mock_chat.return_value = (
                "I'd suggest checking your wardrobe for a top and bottom combination...",
                True,
            )

            resp = client.post("/ai-stylist/chat", json={"message": "What to wear today?"})

        assert resp.status_code == 200
        data = resp.json()
        assert "reply" in data

    def test_chat_no_wardrobe_items(self, client, db_session):
        """User with empty wardrobe → still replies."""
        with patch("app.routers.ai_stylist.chat_with_ai") as mock_chat:
            mock_chat.return_value = (
                "You don't have items yet. Add some to your wardrobe first!",
                False,
            )

            resp = client.post("/ai-stylist/chat", json={"message": "What should I wear?"})

        assert resp.status_code == 200
        assert "reply" in resp.json()


# ===================================================================
# AI Service — unit tests
# ===================================================================


class TestAiServiceUnit:
    """Direct tests of the chat_with_ai service function."""

    def test_fallback_on_empty_wardrobe(self):
        """chat_with_ai with no API key returns fallback."""
        from app.services.ai_stylist import chat_with_ai

        with patch("app.services.ai_stylist._get_api_key", return_value=None):
            reply, was_fallback = chat_with_ai(
                wardrobe_text="The user has no items.",
                message="What should I wear?",
                history=[],
            )

        assert was_fallback is True
        assert isinstance(reply, str)
        assert len(reply) > 0

    def test_fallback_responds_to_weather_question(self):
        """Fallback response is relevant to weather-related questions."""
        from app.services.ai_stylist import chat_with_ai

        with patch("app.services.ai_stylist._get_api_key", return_value=None):
            reply, _ = chat_with_ai(
                wardrobe_text="",
                message="Is it cold outside?",
                history=[],
            )

        assert "weather" in reply.lower() or "cold" in reply.lower() or "layer" in reply.lower()

    def test_fallback_responds_to_color_question(self):
        """Fallback response mentions color matching."""
        from app.services.ai_stylist import chat_with_ai

        with patch("app.services.ai_stylist._get_api_key", return_value=None):
            reply, _ = chat_with_ai(
                wardrobe_text="",
                message="What colors match with blue?",
                history=[],
            )

        assert "color" in reply.lower() or "neutral" in reply.lower()


# ===================================================================
# Database model tests
# ===================================================================


class TestAiChatModel:
    """Verify the AiChatHistory model works correctly."""

    def test_create_chat_record(self, db_session):
        """Create and read a chat history record."""
        record = AiChatHistory(
            user_id=1,
            role="user",
            message="Hello, stylist!",
        )
        db_session.add(record)
        db_session.commit()

        saved = db_session.query(AiChatHistory).first()
        assert saved is not None
        assert saved.user_id == 1
        assert saved.role == "user"
        assert saved.message == "Hello, stylist!"
        assert saved.created_at is not None

    def test_multiple_records_ordered(self, db_session):
        """Records are ordered by created_at."""
        for msg in ["first", "second", "third"]:
            db_session.add(AiChatHistory(user_id=1, role="user", message=msg))
        db_session.commit()

        records = (
            db_session.query(AiChatHistory).filter(AiChatHistory.user_id == 1).order_by(AiChatHistory.created_at.asc()).all()
        )
        assert [r.message for r in records] == ["first", "second", "third"]

    def test_delete_chat_record(self, db_session):
        """Can delete a chat record directly."""
        record = AiChatHistory(
            user_id=1,
            role="user",
            message="test",
        )
        db_session.add(record)
        db_session.commit()

        assert db_session.query(AiChatHistory).count() == 1

        db_session.delete(record)
        db_session.commit()

        assert db_session.query(AiChatHistory).count() == 0
