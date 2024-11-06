from django.urls import path, include
from .views import GenerateTokenView, GetPaymentTotalView, ProcessPaymentView

urlpatterns = [
    path('token', GenerateTokenView.as_view()),
    path('payment-total', GetPaymentTotalView.as_view()),
    path('make-payment', ProcessPaymentView.as_view()),
]
