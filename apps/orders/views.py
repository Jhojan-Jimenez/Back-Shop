from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from core.views import AuthenticatedAPIView
from .models import Order, OrderItem
from .contries import Countries
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes


class GetCountriesView(APIView):
    @extend_schema(
        description="Get all available countries.",
        responses={
            200: {
                    "type": "object",
                            "properties": {
                                "countries": {
                                    "type": "array",
                                    "items": {
                                        "type": "string"
                                    }
                                }
                            },
                "example": {"countries": ["Argentina", "Brazil", "Colombia"]}
            }
        }
    )
    def get(self, request, format=None):
        return Response(
            {'countries': [country[1]
                           for country in Countries.choices]},
            status=status.HTTP_200_OK
        )


class ListOrdersView(AuthenticatedAPIView):
    @extend_schema(
        description="Get all user's orders",
        responses={
            200: {

                    "type": "object",
                            "properties": {
                                "orders": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "status": {"type": "string"},
                                            "transaction_id": {"type": "string"},
                                            "amount": {"type": "number"},
                                            "shipping_price": {"type": "number"},
                                            "date_issued": {"type": "string", "format": "date-time"},
                                            "address_line_1": {"type": "string"},
                                            "address_line_2": {"type": "string"},
                                        }
                                    }
                                }
                            },
                "example": {
                    "orders": [
                        {
                            "status": "Pending",
                            "transaction_id": "TX12345",
                            "amount": 100.00,
                            "shipping_price": 10.00,
                            "date_issued": "2024-12-13T11:45:00Z",
                            "address_line_1": "123 Main St",
                            "address_line_2": "Apt 2B"
                        }
                    ]
                            }

            },
            **AuthenticatedAPIView.get_500_errors()
        }
    )
    def get(self, request, format=None):
        user = self.request.user
        try:
            orders = Order.objects.order_by('-date_issued').filter(user=user)
            result = []

            for order in orders:
                item = {}
                item['status'] = order.status
                item['transaction_id'] = order.transaction_id
                item['amount'] = order.amount
                item['shipping_price'] = order.shipping_price
                item['date_issued'] = order.date_issued
                item['address_line_1'] = order.address_line_1
                item['address_line_2'] = order.address_line_2

                result.append(item)

            return Response(
                {'orders': result},
                status=status.HTTP_200_OK
            )
        except:
            return Response(
                {'error': 'Something went wrong when retrieving orders'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ListOrderDetailView(AuthenticatedAPIView):
    @extend_schema(
        description="Get details about one order",
        parameters=[
            OpenApiParameter(
                "transactionId",
                type=OpenApiTypes.STR,
                required=True,
                description="Transaction ID of the order to be retrieved.",
                location=OpenApiParameter.PATH
            )
        ],
        responses={
            200: {

                "type": "object",
                "properties": {
                    "order": {
                        "type": "object",
                        "properties": {
                            "status": {"type": "string"},
                            "transaction_id": {"type": "string"},
                            "amount": {"type": "number"},
                            "full_name": {"type": "string"},
                            "address_line_1": {"type": "string"},
                            "address_line_2": {"type": "string"},
                            "city": {"type": "string"},
                            "state_province_region": {"type": "string"},
                            "postal_zip_code": {"type": "string"},
                            "country_region": {"type": "string"},
                            "telephone_number": {"type": "string"},
                            "shipping_name": {"type": "string"},
                            "shipping_time": {"type": "string"},
                            "shipping_price": {"type": "number"},
                            "date_issued": {"type": "string", "format": "date-time"},
                            "coupon_discount": {"type": "number"},
                            "order_items": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "name": {"type": "string"},
                                        "price": {"type": "number"},
                                        "count": {"type": "integer"},
                                    }
                                }
                            }
                        }
                    }
                },
                "example": {
                    "order": {
                        "status": "Pending",
                        "transaction_id": "TX12345",
                        "amount": 100.00,
                        "full_name": "John Doe",
                        "order_items": [
                            {
                                "name": "T-Shirt",
                                        "price": 20.00,
                                        "count": 2
                            },
                        ]
                    }
                }

            },
            404: {

                "type": "object",
                "properties": {
                    "error": {"type": "string"}
                },
                "example": {"error": "Order with this transaction ID does not exist"}

            },
            500: {

                "type": "object",
                "properties": {
                    "error": {"type": "string"}
                },
                "example": {"error": "Something went wrong when retrieving order detail"}
            }

        }
    )
    def get(self, request, transactionId, format=None):
        user = self.request.user

        try:
            if Order.objects.filter(user=user, transaction_id=transactionId).exists():
                order = Order.objects.get(
                    user=user, transaction_id=transactionId)
                result = {}
                result['status'] = order.status
                result['transaction_id'] = order.transaction_id
                result['amount'] = order.amount
                result['full_name'] = order.full_name
                result['address_line_1'] = order.address_line_1
                result['address_line_2'] = order.address_line_2
                result['city'] = order.city
                result['state_province_region'] = order.state_province_region
                result['postal_zip_code'] = order.postal_zip_code
                result['country_region'] = order.country_region
                result['telephone_number'] = order.telephone_number
                result['shipping_name'] = order.shipping_name
                result['shipping_time'] = order.shipping_time
                result['shipping_price'] = order.shipping_price
                result['date_issued'] = order.date_issued
                result['coupon_discount'] = order.coupon_descount

                order_items = OrderItem.objects.order_by(
                    '-date_added').filter(order=order)
                result['order_items'] = []

                for order_item in order_items:
                    sub_item = {}

                    sub_item['name'] = order_item.name
                    sub_item['price'] = order_item.price
                    sub_item['count'] = order_item.count

                    result['order_items'].append(sub_item)
                return Response(
                    {'order': result},
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {'error': 'Order with this transaction ID does not exist'},
                    status=status.HTTP_404_NOT_FOUND
                )
        except:
            return Response(
                {'error': 'Something went wrong when retrieving order detail'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
