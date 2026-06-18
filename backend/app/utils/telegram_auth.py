# import os
# import json
# import hmac
# import hashlib
# from urllib.parse import parse_qsl


# BOT_TOKEN = os.getenv("BOT_TOKEN")


# def verify_telegram_init_data(init_data: str):
#     data = dict(parse_qsl(init_data))

#     received_hash = data.pop("hash", None)

#     if not received_hash:
#         return None

#     data_check_string = "\n".join(
#         f"{k}={v}"
#         for k, v in sorted(data.items())
#     )

#     secret_key = hmac.new(
#         b"WebAppData",
#         BOT_TOKEN.encode(),
#         hashlib.sha256
#     ).digest()

#     calculated_hash = hmac.new(
#         secret_key,
#         data_check_string.encode(),
#         hashlib.sha256
#     ).hexdigest()

#     if calculated_hash != received_hash:
#         return None

#     user_data = json.loads(
#         data.get("user", "{}")
#     )

#     return user_data
