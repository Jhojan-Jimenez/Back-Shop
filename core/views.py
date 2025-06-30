from datetime import datetime
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from drf_spectacular.openapi import AutoSchema


class CustomAutoSchema(AutoSchema):
    def get_operation_security(self, path, method):
        if self.view.__class__.__name__ == 'SyncCartView':
            return [{'BearerAuth': {"type": "http",
                                    "scheme": "bearer",
                                    "bearerFormat": "JWT"}}]
        return super().get_operation_security(path, method)


class CustomAPIView(APIView):
    permission_classes = [AllowAny]

    @staticmethod
    def get_500_errors():
        return {
            500: {

                "type": "object",
                "properties": {
                    "error": {"type": "string"}
                },
                "example": {"error": "Something went wrong when retrieving cart items"}
            }
        }


class AuthenticatedAPIView(CustomAPIView):
    permission_classes = [IsAuthenticated]

    @staticmethod
    def get_auth_responses():
        return {
            401: {
                "description": "Unauthorized",


                "type": "object",
                "properties": {
                    "detail": {"type": "string"},
                },

                "example": {"error": "Authentication credentials were not provided."}
            }
        }


def ping_view(request):
    hora_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"✅ Ping recibido a {hora_actual}")
    return JsonResponse({"message": "ok"}, status=200)
