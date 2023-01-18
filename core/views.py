from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import OtpSerializer

# Create your views here.


class SendOtp(APIView):
    def post(self, request):
        serializer = OtpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.save()
        return Response(data)
