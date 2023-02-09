from django.contrib.auth.hashers import check_password
from rest_framework.authentication import get_authorization_header
from rest_framework.exceptions import APIException, AuthenticationFailed
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import UpdateModelMixin
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import MbxUser, Tokens
from .serializers import (
    MbxUserProfessionUpdateSerializer,
    MpinSerializer,
    OtpSerializer,
    OtpVerifySerializer,
    ReferralVerifySerializer,
)
from .token import (
    create_access_token,
    create_refresh_token,
    decode_access_token,
    decode_refresh_token,
    decode_temp_token,
)

# Create your views here.


class RootView(APIView):
    def get(self, request, *args, **kwargs):
        data = {"message": "Moneyboxx Auth APIs"}
        return Response(data)


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
            raise AuthenticationFailed("unauthenticated token not found")

        (user_id, is_mpin_set) = decode_temp_token(token)

        if user_id is None:
            raise AuthenticationFailed("unauthenticated invalid token")

        serializer = MpinSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        try:
            user = MbxUser.objects.get(pk=user_id)
        except MbxUser.DoesNotExist:
            raise APIException("User does not exist!")

        if user.is_mpin_set or user.mpin:
            raise APIException("Mpin already set.")

        user.set_mpin_hash(validated_data["mpin"])
        user.is_mpin_set = True
        user.save()

        access_token = create_access_token(user_id, user.phone_number)
        refresh_token = create_refresh_token(user=user, method="create_new")

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

        if not request.COOKIES.get("refresh_token") and not token:
            raise AuthenticationFailed("unauthenticated, no token/cookie found")

        if request.COOKIES.get("refresh_token") and not token:
            raise AuthenticationFailed("unauthenticated, token not found!")

        if request.COOKIES.get("refresh_token") and token:
            user_id = decode_access_token(token)

        if not request.COOKIES.get("refresh_token") and token:
            (user_id, is_mpin_set) = decode_temp_token(token)
            if token and user_id and not is_mpin_set:
                raise AuthenticationFailed("unauthenticated, invalid temp token!")

        serializer = MpinSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        try:
            user_obj = MbxUser.objects.get(pk=user_id)
        except MbxUser.DoesNotExist:
            raise APIException("User does not exist!")

        if not check_password(validated_data["mpin"], user_obj.mpin):
            raise AuthenticationFailed("Invalid Mpin")

        access_token = create_access_token(user_id, user_obj.phone_number)
        refresh_token = create_refresh_token(user=user_id, method="update_existing")

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
            raise AuthenticationFailed("unauthenticated, cookie not found!")

        refresh_token = request.COOKIES.get("refresh_token")
        (user_id, expiry_time) = decode_refresh_token(
            request.COOKIES.get("refresh_token")
        )

        try:
            token_obj = Tokens.objects.get(user_id=user_id, token=refresh_token)
        except Tokens.DoesNotExist:
            raise APIException(
                "no matching token_obj found, please try with valid cookie!"
            )

        access_token = create_access_token(user_id, token_obj.user_id.phone_number)

        refresh_token = create_refresh_token(user=user_id, method="update_existing")

        response = Response()
        response.set_cookie(key="refresh_token", value=refresh_token, httponly=True)

        response.data = {
            "message": "success",
            "access_token": access_token,
            "refresh_token": refresh_token,
        }
        return response


class VerifyReferralCode(APIView):
    def post(self, request):

        if not request.COOKIES.get("refresh_token"):
            raise AuthenticationFailed("unauthenticated, refresh token not found!")

        token = get_authorization_header(request).decode("utf-8")

        if not token:
            raise AuthenticationFailed("unauthenticated access token not found")

        user_id = decode_access_token(token)

        try:
            current_user = MbxUser.objects.get(pk=user_id)
        except MbxUser.DoesNotExist:
            raise APIException("No matching user found!")

        serializer = ReferralVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_referral = serializer.validated_data["referral_code"]

        try:
            user_with_matching_referral = MbxUser.objects.get(
                referral_code=validated_referral
            )
        except MbxUser.DoesNotExist:
            raise APIException("Invalid referral code!")

        current_user.refered_by_user_id = user_with_matching_referral.id
        current_user.save()

        response = Response()
        response.data = {
            "message": "success",
            "current_user": current_user.id,
            "referred_by": user_with_matching_referral.id,
            "referral_code": validated_referral,
        }
        return response


class MbxUserUpdateView(GenericAPIView, UpdateModelMixin):
    """
    Can support multiple fields update.
    Define multiple serializers class and choose based on field applied in future.
    Currently updates profession field.
    """

    serializer_class = MbxUserProfessionUpdateSerializer

    def get_object(self):

        if not self.request.COOKIES.get("refresh_token"):
            raise AuthenticationFailed("unauthenticated, refresh token not found!")

        token = get_authorization_header(self.request).decode("utf-8")
        if not token:
            raise AuthenticationFailed("unauthenticated access token not found")

        user_id = decode_access_token(token)

        serializer = self.serializer_class(data=self.request.data)
        serializer.is_valid(raise_exception=True)

        return MbxUser.objects.get(pk=user_id)

    def patch(self, request, *args, **kwargs):
        patch_response_data = self.partial_update(request, *args, **kwargs).data
        return Response(
            {"message": "successfully patched profession", "data": patch_response_data}
        )
