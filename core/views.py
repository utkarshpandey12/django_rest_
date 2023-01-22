from rest_framework.authentication import get_authorization_header
from rest_framework.exceptions import APIException, AuthenticationFailed
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import MbxUser
from .serializers import MpinSerializer, OtpSerializer, OtpVerifySerializer
from .token import create_access_token, create_refresh_token, decode_temp_token

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
        auth_headers = get_authorization_header(request).split()

        if not auth_headers or len(auth_headers) != 2:
            raise AuthenticationFailed("unauthenticated")

        token = auth_headers[1].decode("utf-8")

        user_id = decode_temp_token(token)

        serializer = MpinSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        user = MbxUser.objects.get(pk=user_id)
        if user.is_mpin_set or user.mpin:
            raise APIException("Mpin already set.")

        user.set_mpin_hash(validated_data["mpin"])
        access_token = create_access_token(user_id, user.phone_number)
        refresh_token = create_refresh_token(user_id)

        response = Response()

        response.data = {
            "message": "success",
            "data": {"access_token": access_token, "refresh_token": refresh_token},
        }

        return response
