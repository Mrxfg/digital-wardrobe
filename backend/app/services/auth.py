import os
import sys
from datetime import datetime, timedelta
from typing import Optional

from jose import jwt

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

if not SECRET_KEY or not ALGORITHM:
    print("ERROR: SECRET_KEY and ALGORITHM environment variables must be set")
    print("Please create a .env file with these configurations")
    sys.exit(1)


def create_access_token(user_id: int):
    expire = datetime.utcnow() + timedelta(days=7)

    payload = {"user_id": user_id, "exp": expire}

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> Optional[dict]:
    """Decode a JWT token without requiring it to be valid (allows expired too)."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_exp": False})
        return payload
    except Exception:
        return None
