from rest_framework import serializers
from .models import WishList, WishListItem
from apps.product.serializers import ProductSerializer


class WishListSerializer(serializers.ModelSerializer):

    class Meta:
        model = WishList
        fields = '__all__'


class WishListItemSerializer(serializers.ModelSerializer):

    product = ProductSerializer(read_only=True)

    class Meta:
        model = WishListItem
        fields = ["product", "id"]
