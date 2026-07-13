import json
import logging
import os
import random
from typing import Optional

import httpx

QWEN_API_URL = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1/chat/completions"
QWEN_MODEL = "qwen3.7-plus"
REQUEST_TIMEOUT = 10.0
FALLBACK_COMBINATIONS = 3

logger = logging.getLogger(__name__)

# Predefined fallback outfit templates keyed by category pair
_FALLBACK_TEMPLATES: dict[tuple[str, str], str] = {
    ("top", "bottom"): "Classic Top & Bottom",
    ("top", "shoes"): "Casual Day Out",
    ("top", "outerwear"): "Layered Comfort",
    ("top", "bags"): "Everyday Essentials",
    ("bottom", "shoes"): "Street Style",
    ("bottom", "outerwear"): "Urban Layer",
    ("bottom", "bags"): "Practical Everyday",
    ("outerwear", "shoes"): "Outdoor Ready",
    ("outerwear", "bags"): "Go-To Outer Look",
    ("shoes", "bags"): "Minimalist Choice",
    ("top", "accessories"): "Simple Accents",
    ("bottom", "accessories"): "Subtle Details",
    ("dress", "shoes"): "Effortless Elegance",
    ("dress", "outerwear"): "Chic Layering",
    ("dress", "bags"): "Polished Finish",
}


def _get_api_key() -> Optional[str]:
    return os.getenv("QWEN_API_KEY")


def _build_prompt(items_by_category: dict[str, list[dict]]) -> str:
    """Build a prompt for Qwen to generate outfit combinations."""
    categories_desc = []
    for cat, items in items_by_category.items():
        items_desc = ", ".join(f'id: {item["id"]}, name: {item["name"]}, color: {item["color"]}' for item in items)
        categories_desc.append(f"{cat}: [{items_desc}]")

    return f"""You are an AI stylist. Generate {FALLBACK_COMBINATIONS} different outfit combinations from the user's wardrobe.

Available items by category:
{chr(10).join(categories_desc)}

Rules:
- Each outfit must have 1 item from at least 2 different categories (e.g. top + bottom, top + shoes)
- Prefer items with complementary colors
- Return ONLY a valid JSON array, no markdown, no explanation

Format:
[
  {{
    "name": "short creative name for this outfit",
    "items": [item_id_1, item_id_2]
  }}
]"""


def _pick_fallback_name(categories: list[str]) -> str:
    """Pick a meaningful fallback name based on the category combination."""
    cat_pair = (categories[0], categories[1]) if len(categories) >= 2 else (categories[0], categories[0])
    # Try exact match
    name = _FALLBACK_TEMPLATES.get(cat_pair)
    if name:
        return name
    # Try reverse
    name = _FALLBACK_TEMPLATES.get((cat_pair[1], cat_pair[0]))
    if name:
        return name
    # Fallback: combine category names
    return f"{cat_pair[0].title()} + {cat_pair[1].title()}"


def _generate_fallback(items_by_category: dict[str, list[dict]]) -> list[dict]:
    """Generate meaningful outfit combinations when AI is unavailable.

    Uses predefined templates for category pairs and picks random items.
    Picks at least 2 items from at least 2 categories when possible.
    If only 1 category exists, picks 2+ items from that single category.
    """
    categories = list(items_by_category.keys())
    outfits = []

    for i in range(FALLBACK_COMBINATIONS):
        chosen_items = []
        used_ids = set()

        if len(categories) >= 2:
            selected_categories = random.sample(categories, min(2, len(categories)))  # nosec
        else:
            selected_categories = categories * 2

        for cat in selected_categories:
            available = [item for item in items_by_category[cat] if item["id"] not in used_ids]
            if available:
                picked = random.choice(available)  # nosec
                chosen_items.append(picked["id"])
                used_ids.add(picked["id"])

        if len(chosen_items) >= 2:
            name = _pick_fallback_name(selected_categories)
            # Add a number suffix if we generate multiple outfits with the same template
            outfits.append(
                {
                    "name": name if i == 0 else f"{name} {i + 1}",
                    "items": chosen_items,
                }
            )

    return outfits


def _build_chat_prompt(wardrobe_text: str, message: str, history: list[dict], weather_text: str = "") -> str:
    """Build a prompt for Qwen chat with history context."""
    weather_section = ""
    if weather_text:
        weather_section = f"\nCurrent weather: {weather_text}\nUse this weather info when suggesting outfits."

    system_prompt = f"""You are a professional AI stylist. Keep answers SHORT — 2-3 sentences max.

The user's wardrobe consists of:
{wardrobe_text}
{weather_section}

Rules:
- Recommend ONLY items that exist in the user's wardrobe above
- If the user asks about something not in their wardrobe, suggest the closest alternative from what they have
- Keep answers CONCISE — 2-3 sentences, no long explanations
- Use emojis sparingly
- When suggesting an outfit, name the specific items from their wardrobe
- Consider seasons, weather, and occasions"""

    messages = [{"role": "system", "content": system_prompt}]

    for h in history:
        messages.append({"role": h["role"], "content": h["message"]})

    messages.append({"role": "user", "content": message})
    return messages


def chat_with_ai(
    wardrobe_text: str,
    message: str,
    history: list[dict],
    weather_text: str = "",
) -> tuple[str, bool]:
    """Send a chat message to Qwen AI and get a stylist response.

    Returns a tuple of (reply_text, was_fallback).
    history is a list of dicts with 'role' and 'message' keys.
    """
    api_key = _get_api_key()

    if not api_key:
        logger.warning("QWEN_API_KEY not set, using fallback response")
        return _fallback_chat_response(message), True

    messages = _build_chat_prompt(wardrobe_text, message, history, weather_text)

    payload = {
        "model": QWEN_MODEL,
        "messages": messages,
        "temperature": 0.8,
        "max_tokens": 1024,
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.post(QWEN_API_URL, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()

            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            if content:
                return content.strip(), False

    except httpx.TimeoutException:
        logger.warning("Qwen API timed out on chat request")
    except httpx.HTTPStatusError as e:
        logger.error(f"Qwen API error: {e.response.status_code} - {e.response.text}")
    except (httpx.RequestError, KeyError, TypeError) as e:
        logger.error(f"Qwen API failed: {e}")

    return _fallback_chat_response(message), True


def _fallback_chat_response(message: str) -> str:
    """Generate a fallback response when AI is unavailable."""
    message_lower = message.lower()

    if "wear" in message_lower or "outfit" in message_lower:
        return (
            "👔 I'd suggest checking your wardrobe for a top and bottom combination "
            "that matches the weather today! You can use the outfit generator to get "
            "AI-powered suggestions."
        )
    if "color" in message_lower or "match" in message_lower:
        return (
            "🎨 Great question! As a rule of thumb: neutral colors (black, white, gray, navy) "
            "go with almost anything. Try pairing one bold item with neutrals for a balanced look."
        )
    if "weather" in message_lower or "cold" in message_lower or "hot" in message_lower:
        return (
            "🌤️ Check the weather section in the app! Layer your outfit accordingly — "
            "a light jacket for cool mornings that can come off when it warms up."
        )

    return (
        "💡 I'm your AI stylist! Ask me about outfit combinations, color matching, "
        "what to wear for specific occasions, or how to style items from your wardrobe."
    )


def generate_outfits(items_by_category: dict[str, list[dict]]) -> tuple[list[dict], bool]:
    """Generate outfit combinations using Qwen AI with fallback.

    Returns a tuple of (list of dicts with 'name' and 'items', was_fallback).
    Each item dict has at least 'id' — caller enriches with full details.
    """
    api_key = _get_api_key()

    if not api_key:
        logger.warning("QWEN_API_KEY not set, using fallback generator")
        return _generate_fallback(items_by_category), True

    prompt = _build_prompt(items_by_category)

    payload = {
        "model": QWEN_MODEL,
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful AI stylist. Output valid JSON only.",
            },
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.8,
        "max_tokens": 1024,
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    try:
        with httpx.Client(timeout=REQUEST_TIMEOUT) as client:
            response = client.post(QWEN_API_URL, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()

            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")

            # Strip markdown code fences if present
            if content.startswith("```"):
                content = content.strip("`").strip()
                if content.startswith("json"):
                    content = content[4:].strip()

            outfits = json.loads(content)

            if isinstance(outfits, list) and len(outfits) > 0:
                return outfits, False  # AI generated, not a fallback

    except httpx.TimeoutException:
        logger.warning("Qwen API timed out, using fallback")
    except httpx.HTTPStatusError as e:
        logger.error(f"Qwen API error: {e.response.status_code} - {e.response.text}")
    except (httpx.RequestError, json.JSONDecodeError, KeyError, TypeError) as e:
        logger.error(f"Qwen API failed: {e}")

    return _generate_fallback(items_by_category), True
