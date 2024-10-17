from rest_framework import serializers
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.user.models import UserAccount
from .serializers import UserCreateSerializer


class UserView(serializers.Serializer):
    serializer_class = UserCreateSerializer
    queryset = UserAccount.objects.all()


@api_view(["POST"])
def existUser(request):
    try:
        user = UserAccount.objects.get(email=request.data['email'])
        if not user.check_password(request.data['password']):
            return Response({"error": "Invalid Password"}, status=400)
        serialiazer = UserCreateSerializer(user, many=False)
        return Response({"message": serialiazer.data}, status=200)
    except:
        return Response({"error": "No existe un usuario con ese correo"}, status=400)
