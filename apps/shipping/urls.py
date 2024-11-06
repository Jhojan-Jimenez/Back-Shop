from django.urls import path
from .views import GetShippingView

urlpatterns = [
    path('shipping-options', GetShippingView.as_view())
]
