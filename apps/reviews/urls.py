from django.urls import path
from .views import *

urlpatterns = [
    path('get-reviews/<int:productId>', GetProductReviewsView.as_view()),
    path('get-review/<int:productId>', GetProductReviewView.as_view()),
    path('create-review/<int:productId>', CreateProductReviewView.as_view()),
    path('update-review/<int:productId>', UpdateProductReviewView.as_view()),
    path('delete-review/<int:productId>', DeleteProductReviewView.as_view()),
    path('filter-reviews/<int:productId>', FilterProductReviewsView.as_view()),
]
