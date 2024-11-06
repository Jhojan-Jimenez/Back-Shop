from django.urls import path, include
from .views import GetItemsTotalView, AddItemsView, GetItemsView, GetTotalView, UpdateItemView, EmptyCartView, RemoveItemView, SyncCartView

urlpatterns = [
    path('cart-items', GetItemsView.as_view()),
    path('add-item', AddItemsView.as_view()),
    path('total', GetTotalView.as_view()),
    path('total-items', GetItemsTotalView.as_view()),
    path('update-item', UpdateItemView.as_view()),
    path('remove-item/<productId>', RemoveItemView.as_view()),
    path('empty-cart', EmptyCartView.as_view()),
    path('SyncCart', SyncCartView.as_view()),
]
