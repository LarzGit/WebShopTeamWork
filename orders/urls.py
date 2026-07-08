from django.urls import path
from .views import (
    CartView, CartItemAddView, CartItemRemoveView,
    OrderCreateView, OrderHistoryView, OrderDetailView,
)

urlpatterns = [
    path('cart/', CartView.as_view(), name='cart'),
    path('cart/add/', CartItemAddView.as_view(), name='cart-add'),
    path('cart/remove/<int:item_id>/', CartItemRemoveView.as_view(), name='cart-remove'),
    path('checkout/', OrderCreateView.as_view(), name='order-create'),
    path('', OrderHistoryView.as_view(), name='order-history'),
    path('<int:pk>/', OrderDetailView.as_view(), name='order-detail'),
]