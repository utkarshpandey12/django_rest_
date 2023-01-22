import datetime

import jwt
from rest_framework import exceptions


def create_temp_token(user_id, is_mpin_set):

    return jwt.encode(
        {
            "user_id": user_id,
            "mpin_set": is_mpin_set,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(seconds=900),
        },
        "temp_secret",
        algorithm="HS256",
    )


def decode_temp_token(token):
    try:
        payload = jwt.decode(token, "temp_secret", algorithms="HS256")
        return payload["user_id"]
    except Exception:
        raise exceptions.AuthenticationFailed("unauthenticated")


def create_access_token(user_id, phone_number):

    return jwt.encode(
        {
            "user_id": user_id,
            "phone_number": phone_number,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=10),
        },
        "access_token_secret",
        algorithm="HS256",
    )


def create_refresh_token(user_id):

    return jwt.encode(
        {
            "user_id": user_id,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(days=3),
        },
        "refresh_token_secret",
        algorithm="HS256",
    )
