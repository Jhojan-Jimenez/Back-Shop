from rest_framework import serializers
from apps.product.serializers import ProductSerializer


class ProductItemSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    count = serializers.IntegerField()
    product = ProductSerializer()


class CartItemsResponseSerializer(serializers.Serializer):
    products = serializers.ListSerializer(child=ProductItemSerializer())
