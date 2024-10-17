from django.urls import path, include
from .views import existUser

urlpatterns = [
    path('', existUser)
]
