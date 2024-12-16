from calendar import c
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from core.views import CustomAPIView
from .models import FixedPriceCoupon, PercentageCoupon
from .serializers import FixedPriceCouponSerializer, PercentageCouponSerializer
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class CheckCouponView(CustomAPIView):
    @extend_schema(
        description="Check if a coupon code exists and returns its details. Supports both Fixed Price and Percentage coupons.",
        parameters=[
            OpenApiParameter(
                name="coupon_name",
                description="The name of the coupon to check.",
                required=True,
                type=str,
            )
        ],
        responses={
            200: FixedPriceCouponSerializer,
            404: {
                "type": "object",
                "properties": {
                    "error": {"type": "string"}
                },
                "example": {
                    "error": "Coupon code not found"
                }
            },
            **CustomAPIView.get_500_errors(),
        },
    )
    def get(self, request, format=None):
        try:
            coupon_name = request.query_params.get('coupon_name')

            if FixedPriceCoupon.objects.filter(name=coupon_name).exists():
                coupon = FixedPriceCoupon.objects.get(name=coupon_name)
                coupon = FixedPriceCouponSerializer(coupon)

                return Response(
                    {'coupon': coupon.data},
                    status=status.HTTP_200_OK
                )
            elif PercentageCoupon.objects.filter(name=coupon_name).exists():
                coupon = PercentageCoupon.objects.get(name=coupon_name)
                coupon = PercentageCouponSerializer(coupon)

                return Response(
                    {'coupon': coupon.data},
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {'error': 'Coupon code not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
        except:
            return Response(
                {'error': 'Something went wrong when checking coupon'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
