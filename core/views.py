from datetime import datetime

import pytz
from django.contrib.auth.hashers import check_password
from rest_framework.authentication import get_authorization_header
from rest_framework.exceptions import APIException, AuthenticationFailed
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import MbxUser, Tokens
from .serializers import MpinSerializer, OtpSerializer, OtpVerifySerializer
from .token import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    decode_temp_token,
)

# Create your views here.


class SendOtp(APIView):
    def post(self, request):
        serializer = OtpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.save()
        return Response(data)


class VerifyOtp(APIView):
    def post(self, request):
        serializer = OtpVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.save()
        return Response(data)


class SetMpin(APIView):
    def post(self, request):
        token = get_authorization_header(request).decode("utf-8")

        if not token:
            raise AuthenticationFailed("unauthenticated")

        user_id = decode_temp_token(token)

        serializer = MpinSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        user = MbxUser.objects.get(pk=user_id)

        if user.is_mpin_set or user.mpin:
            raise APIException("Mpin already set.")

        user.set_mpin_hash(validated_data["mpin"])
        user.is_mpin_set = True
        user.save()

        access_token = create_access_token(user_id, user.phone_number)
        refresh_token = create_refresh_token(user_id)

        refresh_token_expiry = decode_refresh_token(refresh_token)[1]

        token_obj = Tokens(
            user_id=user,
            token_type="REFRESH",
            token=refresh_token,
            expiry=datetime.utcfromtimestamp(refresh_token_expiry).replace(
                tzinfo=pytz.utc
            ),
        )
        token_obj.save()

        response = Response()
        response.set_cookie(key="refresh_token", value=refresh_token, httponly=True)
        response.data = {
            "message": "success",
            "data": {"access_token": access_token, "refresh_token": refresh_token},
        }

        return response


class VerifyMpin(APIView):
    def post(self, request):
        token = get_authorization_header(request).decode("utf-8")

        if token and decode_temp_token(token):
            raise AuthenticationFailed("unauthenticated temp token found.")

        if not request.COOKIES.get("refresh_token"):
            raise AuthenticationFailed("unauthenticated")

        user_id = decode_refresh_token(request.COOKIES.get("refresh_token"))[0]

        serializer = MpinSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        user_obj = MbxUser.objects.get(pk=user_id)

        if not check_password(validated_data["mpin"], user_obj.mpin):
            raise AuthenticationFailed("Invalid Mpin")

        access_token = create_access_token(user_id, user_obj.phone_number)
        refresh_token = create_refresh_token(user_id)

        token_obj = Tokens.objects.get(user_id=user_obj.id)
        token_obj.token = refresh_token
        token_obj.expiry = datetime.utcfromtimestamp(
            decode_refresh_token(refresh_token)[1]
        ).replace(tzinfo=pytz.utc)

        token_obj.save()

        response = Response()
        response.set_cookie(key="refresh_token", value=refresh_token, httponly=True)

        response.data = {
            "message": "success",
            "data": {"access_token": access_token, "refresh_token": refresh_token},
        }
        return response


class RefreshToken(APIView):
    def post(self, request):

        if not request.COOKIES.get("refresh_token"):
            raise AuthenticationFailed("unauthenticated")

        refresh_token = request.COOKIES.get("refresh_token")
        user_id = decode_refresh_token(request.COOKIES.get("refresh_token"))[0]

        token_obj = Tokens.objects.get(user_id=user_id, token=refresh_token)

        if not token_obj:
            raise AuthenticationFailed("unauthenticated")

        access_token = create_access_token(user_id, token_obj.user_id.phone_number)

        refresh_token = create_refresh_token(user_id)
        token_obj.token = refresh_token
        token_obj.save()

        response = Response()
        response.set_cookie(key="refresh_token", value=refresh_token, httponly=True)

        response.data = {
            "message": "success",
            "access_token": access_token,
            "refresh_token": refresh_token,
        }
        return response
