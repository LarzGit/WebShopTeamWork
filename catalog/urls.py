from django.urls import path
from .views import (
    ProductListCreateView, ProductDetailUpdateDeleteView,
    CategoryListCreateView, CategoryDetailUpdateDeleteView,
    ReviewListCreateView, ReviewDetailUpdateDeleteView,
)

urlpatterns = [
    path('products/', ProductListCreateView.as_view(), name='product-list-create'),
    path('products/<int:pk>/', ProductDetailUpdateDeleteView.as_view(), name='product-detail'),
    path('categories/', CategoryListCreateView.as_view(), name='category-list-create'),
    path('categories/<int:pk>/', CategoryDetailUpdateDeleteView.as_view(), name='category-detail'),
    path('reviews/', ReviewListCreateView.as_view(), name='review-list-create'),
    path('reviews/<int:pk>/', ReviewDetailUpdateDeleteView.as_view(), name='review-detail'),
]