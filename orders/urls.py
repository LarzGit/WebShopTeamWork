from django.urls import path
from .views import (
    CartView, CartItemAddView, CartItemRemoveView, CartItemUpdateView,
    OrderCreateView, OrderHistoryView, OrderDetailView, OrderStatusUpdateView,
)

urlpatterns = [
    path('cart/', CartView.as_view(), name='cart'),
    path('cart/add/', CartItemAddView.as_view(), name='cart-add'),
    path('cart/update/<int:item_id>/', CartItemUpdateView.as_view(), name='cart-update'),
    path('cart/remove/<int:item_id>/', CartItemRemoveView.as_view(), name='cart-remove'),
    path('checkout/', OrderCreateView.as_view(), name='order-create'),
    path('<int:pk>/status/', OrderStatusUpdateView.as_view(), name='order-status-update'),
    path('', OrderHistoryView.as_view(), name='order-history'),
    path('<int:pk>/', OrderDetailView.as_view(), name='order-detail'),
]