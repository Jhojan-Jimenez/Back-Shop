from django.urls import path
from .views import ListOrderDetailView, ListOrdersView, GetCountriesView

urlpatterns = [
    path("", ListOrdersView.as_view()),
    path("countries", GetCountriesView.as_view()),
    path("<transactionId>", ListOrderDetailView.as_view())

]
