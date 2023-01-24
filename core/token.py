import datetime

import jwt
from rest_framework import exceptions

from .models import Tokens


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
        return (payload["user_id"], payload["mpin_set"])
    except Exception:
        return (None, None)


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


def decode_access_token(token):
    try:
        payload = jwt.decode(token, "access_token_secret", algorithms="HS256")
        return payload["user_id"]
    except Exception:
        raise exceptions.AuthenticationFailed("unauthenticated")


def create_refresh_token(**kwargs):
    expiry_time = datetime.datetime.utcnow() + datetime.timedelta(days=3)
    refresh_token = jwt.encode(
        {
            "user_id": [
                kwargs["user"].id
                if kwargs["method"] == "create_new"
                else kwargs["user"]
            ][0],
            "exp": expiry_time,
        },
        "refresh_token_secret",
        algorithm="HS256",
    )

    if kwargs["method"] == "create_new":
        token_obj = Tokens(
            user_id=kwargs["user"],
            token_type="REFRESH",
            token=refresh_token,
            expiry=expiry_time,
        )
        token_obj.save()

    else:
        token_obj = Tokens.objects.get(user_id=kwargs["user"])
        token_obj.token = refresh_token
        token_obj.expiry = expiry_time
        token_obj.save()

    return refresh_token


def decode_refresh_token(token):
    try:
        payload = jwt.decode(token, "refresh_token_secret", algorithms="HS256")
        return (payload["user_id"], payload["exp"])
    except Exception:
        raise exceptions.AuthenticationFailed("unauthenticated")
