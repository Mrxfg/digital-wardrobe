import os
import sys
from datetime import datetime, timedelta

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
