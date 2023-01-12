from rest_framework.response import Response
from rest_framework.views import APIView

# Create your views here.


class RootView(APIView):
    def get(self, request, *args, **kwargs):
        data = {"message": "Moneyboxx Auth APIs"}
        return Response(data)
