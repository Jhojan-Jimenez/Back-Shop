from django.urls import path
from .views import ListProductsView, ProductDetailView, ListSearchView, ListRelatedView, ListBySearchView

urlpatterns = [
    # path('products', ListProductsView.as_view()),
    # path('search', ListSearchView.as_view()),
    # path('related/<productId>', ListRelatedView.as_view()),
    # path('by/search', ListBySearchView.as_view()),
    path('products', ListBySearchView.as_view()),
    path('related/<int:productId>', ListRelatedView.as_view()),
    path('<int:productId>', ProductDetailView.as_view()),
]
