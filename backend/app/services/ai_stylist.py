import json
import logging
import os
import random
from typing import Optional

import httpx

QWEN_API_URL = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1/chat/completions"
QWEN_MODEL = "qwen-plus"
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
- IMPORTANT: Each outfit must use different items — no item should appear in more than one suggestion
- All {FALLBACK_COMBINATIONS} outfits must be distinct from each other in both items and style
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
    Tracks used items globally so each suggestion uses different pieces.
    """
    categories = list(items_by_category.keys())
    outfits = []
    globally_used_ids: set[int] = set()

    # Flatten all available items for retrying
    all_items = [item for items in items_by_category.values() for item in items]
    random.shuffle(all_items)

    for i in range(FALLBACK_COMBINATIONS):
        chosen_ids: list[int] = []
        remaining = [item for item in all_items if item["id"] not in globally_used_ids]
        # If not enough unused items, reset the pool for remaining slots
        if len(remaining) < 2:
            globally_used_ids.clear()
            remaining = all_items

        # Pick from at least 2 different categories when possible
        if len(categories) >= 2:
            selected_categories = random.sample(categories, min(2, len(categories)))  # nosec
        else:
            selected_categories = categories * 2

        for cat in selected_categories:
            available = [item for item in remaining if item["category"] == cat and item["id"] not in globally_used_ids]
            if available:
                picked = random.choice(available)  # nosec
                chosen_ids.append(picked["id"])
                globally_used_ids.add(picked["id"])
            else:
                # Fallback to any unused item from other categories
                for item in remaining:
                    if item["id"] not in globally_used_ids:
                        chosen_ids.append(item["id"])
                        globally_used_ids.add(item["id"])
                        break

        if len(chosen_ids) >= 2:
            name = _pick_fallback_name(selected_categories)
            suffix = "" if i == 0 else f" {i + 1}"
            # Only add suffix if the name would otherwise collide
            if i > 0 and any(o["name"].startswith(name) for o in outfits):
                suffix = f" {i + 1}"
            outfits.append(
                {
                    "name": name + suffix,
                    "items": chosen_ids,
                }
            )

    return outfits


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
        "temperature": 0.9,
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
