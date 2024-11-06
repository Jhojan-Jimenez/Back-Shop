from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Cart, CartItem

from apps.product.models import Product
from apps.product.serializers import ProductSerializer
from apps.wishlist.models import WishList, WishListItem


class GetItemsView(APIView):
    def get(self, request, format=None):
        user = request.user
        try:
            cart = Cart.objects.get(user=user)
            cart_items = CartItem.objects.filter(cart=cart)
            result = []
            if cart_items.exists():
                for cart_item in cart_items:
                    item = {}
                    item['id'] = cart_item.pk
                    item['count'] = cart_item.count
                    product = Product.objects.get(id=cart_item.product.id)
                    product = ProductSerializer(product)

                    item['product'] = product.data

                    result.append(item)

            return Response(
                {'products': result},
                status=status.HTTP_200_OK)

        except:
            return Response(
                {'error': 'Something went wrong when retrieving cart items'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AddItemsView(APIView):
    def post(self, request, format=None):
        user = request.user
        data = request.data
        try:
            product_id = int(data['product_id'])

        except:
            return Response(
                {'error': 'Product ID must be an integer'},
                status=status.HTTP_404_NOT_FOUND)

        try:
            if not Product.objects.filter(id=product_id).exists():
                return Response(
                    {'error': 'Product with this ID does not exist'},
                    status=status.HTTP_404_NOT_FOUND)
            product = Product.objects.get(id=product_id)
            user_cart = Cart.objects.get(user=user)

            if CartItem.objects.filter(product=product, cart=user_cart).exists():
                return Response(
                    {'error': 'Item is already in cart'},
                    status=status.HTTP_409_CONFLICT)
            if int(product.quantity) > 0:
                CartItem.objects.create(
                    product=product, cart=user_cart, count=1
                )
                total_items = int(user_cart.total_items)+1
                Cart.objects.filter(user=user).update(
                    total_items=total_items
                )
                wishlist = WishList.objects.get(user=user)
                if WishListItem.objects.filter(wishlist=wishlist, product=product).exists():
                    WishListItem.objects.filter(
                        wishlist=wishlist, product=product).delete()
                    total_items = int(wishlist.total_items)-1
                    WishList.objects.filter(user=user).update(
                        total_items=total_items
                    )

                return Response(
                    {'message': 'Product successfully added to your cart'},
                    status=status.HTTP_200_OK)

            else:
                return Response(
                    {'error': 'Not enough of this item in stock'},
                    status=status.HTTP_409_CONFLICT)

        except:

            return Response(
                {'error': 'Something went wrong when retrieving cart items'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GetTotalView(APIView):
    def get(self, request, format=None):
        user = request.user

        try:

            user_cart = Cart.objects.get(user=user)
            cart_items = CartItem.objects.filter(cart=user_cart)
            total = 0

            if cart_items.exists():
                for cart_item in cart_items:
                    n = cart_item.count
                    price = cart_item.product.price
                    total += price*n
            return Response(
                {'total_cost': total},
                status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': e},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GetItemsTotalView(APIView):
    def get(self, request, format=None):
        user = request.user
        try:
            user_cart = Cart.objects.get(user=user)

            return Response(
                {'total_items': user_cart.total_items},
                status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': 'Something went wrong when retrieving cart items'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UpdateItemView(APIView):
    def put(self, request, format=None):
        user = request.user
        data = request.data

        try:
            product_id = int(data['product_id'])

        except:
            return Response(
                {'error': 'Product ID must be an integer'},
                status=status.HTTP_404_NOT_FOUND)

        try:
            count = int(data['count'])

        except:
            return Response(
                {'error': 'Count value must be an integer'},
                status=status.HTTP_404_NOT_FOUND)

        try:
            if not Product.objects.filter(id=product_id).exists():
                return Response(
                    {'error': 'Product with this ID does not exist'},
                    status=status.HTTP_404_NOT_FOUND)

            user_cart = Cart.objects.get(user=user)
            product = Product.objects.get(id=product_id)

            if not CartItem.objects.filter(cart=user_cart, product=product).exists():
                return Response(
                    {'error': 'This product is not in your cart'},
                    status=status.HTTP_404_NOT_FOUND)

            stock = product.quantity

            if stock >= count:
                CartItem.objects.filter(
                    product=product, cart=user_cart
                ).update(count=count)

                cart_items = CartItem.objects.order_by(
                    'product').filter(cart=user_cart)
                result = []

                for cart_item in cart_items:
                    item = {}
                    item['id'] = cart_item.id
                    item['count'] = cart_item.count

                    product = Product.objects.get(id=cart_item.product.id)
                    product = ProductSerializer(product)
                    item['product'] = product.data

                    result.append(item)

                return Response({'cart': result}, status=status.HTTP_200_OK)

            else:
                return Response(
                    {'error': 'Not enough of this item in stock'},
                    status=status.HTTP_403_FORBIDDEN)

        except:

            return Response(
                {'error': 'Something went wrong when retrieving cart items'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RemoveItemView(APIView):
    def delete(self, request, productId, format=None):
        user = request.user

        try:
            product_id = int(productId)

        except:
            return Response(
                {'error': 'Product ID must be an integer'},
                status=status.HTTP_404_NOT_FOUND)

        try:
            if not Product.objects.filter(id=product_id).exists():
                return Response(
                    {'error': 'Product with this ID does not exist'},
                    status=status.HTTP_404_NOT_FOUND)

            user_cart = Cart.objects.get(user=user)
            product = Product.objects.get(id=product_id)

            if not CartItem.objects.filter(cart=user_cart, product=product).exists():
                return Response(
                    {'error': 'This product is not in your cart'},
                    status=status.HTTP_404_NOT_FOUND)

            CartItem.objects.filter(cart=user_cart, product=product).delete()

            if not CartItem.objects.filter(cart=user_cart, product=product).exists():
                total_items = int(user_cart.total_items) - 1
                Cart.objects.filter(user=user).update(total_items=total_items)

            cart_items = CartItem.objects.order_by(
                'product').filter(cart=user_cart)
            result = []

            if CartItem.objects.filter(cart=user_cart).exists():
                for cart_item in cart_items:
                    item = {}
                    item['id'] = cart_item.id
                    item['count'] = cart_item.count

                    product = Product.objects.get(id=cart_item.product.id)
                    product = ProductSerializer(product)
                    item['product'] = product.data

                    result.append(item)

            return Response({'cart': result}, status=status.HTTP_200_OK)

        except:
            return Response(
                {'error': 'Something went wrong when retrieving cart items'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class EmptyCartView(APIView):
    def delete(self, request, format=None):
        user = request.user

        try:
            if Cart.objects.get(user=user).total_items == 0:
                return Response(
                    {'error': 'Your cart is already empty'},
                    status=status.HTTP_409_CONFLICT)
            user_cart = Cart.objects.get(user=user)

            CartItem.objects.filter(cart=user_cart).delete()
            Cart.objects.filter(user=user).update(total_items=0)

            return Response(
                {'success': 'Cart emptied successfully'},
                status=status.HTTP_200_OK)

        except:
            return Response(
                {'error': 'Something went wrong when retrieving cart items'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SyncCartView(APIView):
    def put(self, request, format=None):
        user = request.user
        data = request.data

        try:
            user_cart = Cart.objects.get(user=user)
            cart_items = data['cart_items']

            for item in cart_items:
                try:
                    product_id = int(item["product"]["id"])

                except:
                    return Response(
                        {'error': 'Product ID must be an integer'},
                        status=status.HTTP_404_NOT_FOUND)

                if not Product.objects.filter(id=product_id).exists():
                    return Response(
                        {'error': 'Product with this ID does not exist'},
                        status=status.HTTP_404_NOT_FOUND)

                product = Product.objects.get(id=product_id)

                if CartItem.objects.filter(cart=user_cart, product=product):
                    try:
                        count = int(item["count"])
                    except:
                        return Response(
                            {'error': 'Count must be an integer'},
                            status=status.HTTP_404_NOT_FOUND)

                    CartItem.objects.filter(
                        cart=user_cart, product=product).update(count=count)

            return Response(
                {'success': 'Cart Synchronized'},
                status=status.HTTP_201_CREATED)

        except:
            return Response(
                {'error': 'Something went wrong when retrieving cart items'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
