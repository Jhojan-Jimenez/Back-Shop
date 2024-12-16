from django.urls import path
from .views import RemoveItemView, AddItemView, GetItemsView, ExistItemView

urlpatterns = [
    path("", GetItemsView.as_view()),
    path("exist-item/<int:productId>", ExistItemView.as_view()),
    path("add-item", AddItemView.as_view()),
    path("remove-item/<int:productId>", RemoveItemView.as_view()),
]
