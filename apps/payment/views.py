from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apps.cart.models import Cart, CartItem
from apps.coupons.models import FixedPriceCoupon, PercentageCoupon
from apps.orders.models import Order, OrderItem
from apps.product.models import Product
from apps.shipping.models import Shipping
from django.core.mail import send_mail
import uuid
import os
import jwt
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse

from core.views import AuthenticatedAPIView

payment_key = os.environ.get("PAYMENT_KEY")


class GenerateTokenView(APIView):
    @extend_schema(exclude=True)
    def get(self, request, format=None):
        user = self.request.user

        try:
            payload = {
                "user_id": user.email,
            }
            token = jwt.encode(payload, payment_key, algorithm="HS256")

            return Response(
                {'PaymentToken': token},
                status=status.HTTP_200_OK
            )
        except:
            return Response(
                {'error': 'Something went wrong when retrieving payment token'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class GetPaymentTotalView(AuthenticatedAPIView):
    @extend_schema(
        description="Get the total amount of the payment including tax, shipping, and coupon discounts.",
        parameters=[
            OpenApiParameter(
                name="shipping_id",
                description="The ID of the shipping option.",
                required=True,
                type=str,
            ),
            OpenApiParameter(
                name="coupon_name",
                description="The name of the coupon to apply.",
                required=False,
                type=str,
            )
        ],
        responses={
            200: {

                "type": "object",
                "properties": {
                    "original_price": {"type": "string"},
                    "total_after_coupon": {"type": "string"},
                    "estimated_tax": {"type": "string"},
                    "shipping_cost": {"type": "string"},
                    "final_total_amount": {"type": "string"},
                    "total_compare_amount": {"type": "string"}
                },
                "example": {
                    "original_price": "100.00",
                    "total_after_coupon": "90.00",
                    "estimated_tax": "0.19",
                    "shipping_cost": "5.00",
                    "final_total_amount": "95.00",
                    "total_compare_amount": "120.00"
                }

            },
            200: {

                "type": "object",
                "properties": {
                    "error": {"type": "string"}
                },

                "example": {"error": "Not enough Adidas blue items in stock"}
            },
            **AuthenticatedAPIView.get_auth_responses(),
            404: {

                "type": "object",
                "properties": {
                    "error": {"type": "string"}
                },

                "example": {"error": "Need to have items in cart"}


            },
            404: {

                "type": "object",
                "properties": {
                    "error": {"type": "string"}
                },

                "example": {"error": "A proudct with ID 1 does not exist"}


            },
            **AuthenticatedAPIView.get_500_errors(),
        }
    )
    def get(self, request, format=None):
        user = self.request.user

        tax = 0.19

        shipping_id = request.query_params.get('shipping_id')
        shipping_id = str(shipping_id)
        coupon_name = request.query_params.get('coupon_name')
        coupon_name = str(coupon_name)

        try:
            cart = Cart.objects.get(user=user)

            # Revisar si existen items
            if not CartItem.objects.filter(cart=cart).exists():
                return Response(
                    {'error': 'Need to have items in cart'},
                    status=status.HTTP_404_NOT_FOUND
                )

            cart_items = CartItem.objects.filter(cart=cart)

            for cart_item in cart_items:
                if not Product.objects.filter(id=cart_item.product.id).exists():
                    return Response(
                        {'error': 'A proudct with ID' +
                            cart_item.product.id + ' does not exist'},
                        status=status.HTTP_404_NOT_FOUND
                    )
                if int(cart_item.count) > int(cart_item.product.quantity):
                    return Response(
                        {'error': f'Not enough {cart_item.product.name} items in stock'},
                        status=status.HTTP_200_OK
                    )

                total_amount = 0.0
                total_compare_amount = 0.0

                for cart_item in cart_items:
                    total_amount += (float(cart_item.product.price)
                                     * float(cart_item.count))
                    total_compare_amount += (float(cart_item.product.compare_price)
                                             * float(cart_item.count))
                original_price = total_amount
                # Cupones
                total_after_coupon = None
                if coupon_name != '':
                    # Revisar si cupon de precio fijo es valido
                    if FixedPriceCoupon.objects.filter(name__iexact=coupon_name).exists():
                        fixed_price_coupon = FixedPriceCoupon.objects.get(
                            name=coupon_name
                        )
                        discount_amount = float(
                            fixed_price_coupon.discount_price)
                        if discount_amount < total_amount:
                            total_amount -= discount_amount
                            total_after_coupon = total_amount

                    elif PercentageCoupon.objects.filter(name__iexact=coupon_name).exists():
                        percentage_coupon = PercentageCoupon.objects.get(
                            name=coupon_name
                        )
                        discount_percentage = float(
                            percentage_coupon.discount_percentage)

                        if discount_percentage > 1 and discount_percentage < 100:
                            total_amount -= (total_amount *

                                             (discount_percentage / 100))
                            total_after_coupon = total_amount

                total_amount += (total_amount * tax)

                shipping_cost = 0.0
                # verificar que el envio sea valido
                if Shipping.objects.filter(id__iexact=shipping_id).exists():
                    # agregar shipping a total amount
                    shipping = Shipping.objects.get(id=shipping_id)
                    shipping_cost = shipping.price
                    total_amount += float(shipping_cost)

                total_amount = round(total_amount, 2)

                return Response({
                    'original_price': f'{original_price}',
                    'total_after_coupon': f'{total_after_coupon}' if total_after_coupon else None,
                    'estimated_tax': f'{0.18}',
                    'shipping_cost': f'{shipping_cost}',
                    'final_total_amount': f'{total_amount:}',
                    'total_compare_amount': f'{total_compare_amount}',
                },
                    status=status.HTTP_200_OK
                )

        except:
            return Response(
                {'error': 'Something went wrong when retrieving payment total information'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ProcessPaymentView(AuthenticatedAPIView):
    @extend_schema(
        description="Process the checkout by validating the shipping, coupon, and cart items, then creating the order.",
        parameters=[
            OpenApiParameter(
                name="shipping_id",
                description="The ID of the selected shipping option.",
                required=True,
                type=str,
            ),
            OpenApiParameter(
                name="coupon_name",
                description="The name of the coupon to apply (optional).",
                required=False,
                type=str,
            ),
        ],
        responses={
            200: {
                "type": "object",
                "properties": {
                    "success": {"type": "string"}
                },
                "example": {"error": "Transaction successful and order was created"}
            },

            400: {

                "type": "object",
                "properties": {
                    "error": {"type": "string"}
                },

                "example": {
                    "insufficient_stock":
                    {"error": "Not enough Adidas blue items in stock"},

                    "transaction_failure":  {"error": "Transaction failed"}

                }
            },
            **AuthenticatedAPIView.get_auth_responses(),
            404: {
                "type": "object",
                "properties": {
                        "error": {"type": "string"}
                },
                "example": [{"error": "Need to have items in cart"}, {"error": "Transaction failed, a product ID 1 does not exist"}, {"error": "Invalid shipping option"}],

            },
            500: {

                "type": "object",
                "properties": {
                        "error": {"type": "string"}
                },
                "example":
                    [{"error": "Something is wrong with the payment"}, {"error": "Transaction succeeded but failed to create the order"}, {"error": "Transaction succeeded and order created, but failed to create an order item"}, {
                        "error": "Transaction succeeded and order created, but failed to send email"}, {"error": "Transaction succeeded and order successful, but failed to clear cart"}]

            }
        }
    )
    def post(self, request, format=None):
        user = self.request.user
        data = self.request.data

        tax = 0.19
        shipping_id = str(data['shipping_id'])
        coupon_name = str(data['coupon_name'])

        full_name = data['full_name']
        address_line_1 = data['address_line_1']
        address_line_2 = data['address_line_2']
        city = data['city']
        state_province_region = data['state_province_region']
        postal_zip_code = data['postal_zip_code']
        country_region = data['country_region']
        telephone_number = data['telephone_number']

        # revisar si datos de shipping son validos
        if not Shipping.objects.filter(id__iexact=shipping_id).exists():
            return Response(
                {'error': 'Invalid shipping option'},
                status=status.HTTP_404_NOT_FOUND
            )

        cart = Cart.objects.get(user=user)

        # revisar si usuario tiene items en carrito
        if not CartItem.objects.filter(cart=cart).exists():
            return Response(
                {'error': 'Need to have items in cart'},
                status=status.HTTP_404_NOT_FOUND
            )

        cart_items = CartItem.objects.filter(cart=cart)

        # revisar si hay stock

        for cart_item in cart_items:
            if not Product.objects.filter(id=cart_item.product.id).exists():
                return Response(
                    {'error': 'Transaction failed, a product ID ' +
                        cart_item.product.id+' does not exist'},
                    status=status.HTTP_404_NOT_FOUND
                )
            if int(cart_item.count) > int(cart_item.product.quantity):
                return Response(
                    {'error': 'Not enough '+cart_item.product.name+' items in stock'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        total_amount = 0.0

        for cart_item in cart_items:
            total_amount += (float(cart_item.product.price)
                             * float(cart_item.count))
        coupon_descount = 0
        # Cupones
        if coupon_name != '':
            if FixedPriceCoupon.objects.filter(name__iexact=coupon_name).exists():
                fixed_price_coupon = FixedPriceCoupon.objects.get(
                    name=coupon_name
                )
                discount_amount = float(fixed_price_coupon.discount_price)
                if discount_amount < total_amount:
                    coupon_descount = discount_amount
                    total_amount -= discount_amount

            elif PercentageCoupon.objects.filter(name__iexact=coupon_name).exists():
                percentage_coupon = PercentageCoupon.objects.get(
                    name=coupon_name
                )
                discount_percentage = float(
                    percentage_coupon.discount_percentage)

                if discount_percentage > 1 and discount_percentage < 100:
                    coupon_descount = (total_amount *
                                       (discount_percentage / 100))
                    total_amount -= coupon_descount

        total_amount += (total_amount * tax)

        shipping = Shipping.objects.get(id=int(shipping_id))

        shipping_name = shipping.name
        shipping_time = shipping.time_to_delivery
        shipping_price = shipping.price

        total_amount += float(shipping_price)
        newTransaction = {"is_success": False}
        try:
            payload = {
                "user_id": user.email,
            }
            jwt.encode(payload, payment_key, algorithm="HS256")
            newTransaction["is_success"] = True
            newTransaction["id"] = uuid.uuid4()
        except:
            return Response(
                {'error': 'Something is wrong with the payment'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        if newTransaction['is_success']:
            for cart_item in cart_items:
                update_product = Product.objects.get(id=cart_item.product.id)

                # encontrar cantidad despues de coompra
                quantity = int(update_product.quantity) - int(cart_item.count)

                # obtener cantidad de producto por vender
                sold = int(update_product.sold) + int(cart_item.count)

                # actualizar el producto
                Product.objects.filter(id=cart_item.product.id).update(
                    quantity=quantity, sold=sold
                )

            # crear orden
            try:
                order = Order.objects.create(
                    user=user,
                    transaction_id=newTransaction["id"],
                    amount=total_amount,
                    full_name=full_name,
                    address_line_1=address_line_1,
                    address_line_2=address_line_2,
                    city=city,
                    state_province_region=state_province_region,
                    postal_zip_code=postal_zip_code,
                    country_region=country_region,
                    telephone_number=telephone_number,
                    shipping_name=shipping_name,
                    shipping_time=shipping_time,
                    shipping_price=float(shipping_price),
                    coupon_descount=coupon_descount
                )
            except:
                return Response(
                    {'error': 'Transaction succeeded but failed to create the order'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            for cart_item in cart_items:
                try:
                    # agarrar el producto
                    product = Product.objects.get(id=cart_item.product.id)

                    OrderItem.objects.create(
                        product=product,
                        order=order,
                        name=product.name,
                        price=cart_item.product.price,
                        count=cart_item.count
                    )
                except Exception as e:
                    print(e)
                    return Response(
                        {'error': 'Transaction succeeded and order created, but failed to create an order item'},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )

            try:
                send_mail(
                    'Your Order Details',
                    'Hey ' + full_name + ','
                    + '\n\nWe received your order!'
                    + '\n\nGive us some time to process your order and ship it out to you.'
                    + '\n\nYou can go on your user dashboard to check the status of your order.'
                    + '\n\nSincerely,'
                    + '\nShop Time',
                    'carlosmortshop@gmail.com',  # Cambia esto a una dirección de correo válida
                    [user.email],
                    fail_silently=False
                )

            except Exception as e:
                print(e)
                return Response(
                    {'error': 'Transaction succeeded and order created, but failed to send email'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            try:
                # Vaciar carrito de compras
                CartItem.objects.filter(cart=cart).delete()

                # Actualizar carrito
                Cart.objects.filter(user=user).update(total_items=0)
            except:
                return Response(
                    {'error': 'Transaction succeeded and order successful, but failed to clear cart'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            return Response(
                {'success': 'Transaction successful and order was created'},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {'error': 'Transaction failed'},
                status=status.HTTP_400_BAD_REQUEST
            )
