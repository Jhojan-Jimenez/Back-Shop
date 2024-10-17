from djoser.serializers import UserCreateSerializer
from rest_framework import serializers
from django.contrib.auth import get_user_model

#Obtiene el modelo que nosotros hicimos, dado que en csetting, extablecimos AUTH_USER_MODEL como nuestro modelo
User = get_user_model()


class UserCreateSerializer (UserCreateSerializer):
    class Meta (UserCreateSerializer.Meta):
        model = User
        fields = (
            'id',
            'email',
            'first_name',
            'last_name',
            'get_full_name',
        )


class UserAccountSerializer (UserCreateSerializer):
    class Meta (UserCreateSerializer.Meta):
        model = User
        fields = (
            'id',
            'email',
            'first_name',
            'last_name',
            'get_full_name',
        )
