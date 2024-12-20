from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions

from core.views import CustomAPIView
from .models import Shipping
from .serializers import ShippingSerializer
from drf_spectacular.utils import extend_schema


class GetShippingView(CustomAPIView):

    @extend_schema(
        description="Get all available shipping options.",
        responses={200: ShippingSerializer(many=True),
                   404: {

            "type": "object",
            "properties": {
                "error": {"type": "string"}
            },
            "example": {"error": "No shipping options available"}

        },
        },

    )
    def get(self, request, format=None):
        if Shipping.objects.all().exists():
            shipping_options = Shipping.objects.all()
            shipping_options = ShippingSerializer(shipping_options, many=True)

            return Response(
                {'shipping_options': shipping_options.data},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {'error': 'No shipping options available'},
                status=status.HTTP_404_NOT_FOUND
            )
