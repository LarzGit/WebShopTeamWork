from django.db import transaction
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Order, OrderItem, Cart, CartItem
from .serializers import OrderSerializer, CartSerializer


class CartView(APIView):
    """Показати кошик поточного користувача"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        return Response(CartSerializer(cart).data)


class CartItemAddView(APIView):
    """Додати товар у кошик (або збільшити кількість, якщо вже є)"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        product_id = request.data.get('product')
        quantity = int(request.data.get('quantity', 1))

        cart, _ = Cart.objects.get_or_create(user=request.user)
        item, created = CartItem.objects.get_or_create(
            cart=cart, product_id=product_id,
            defaults={'quantity': quantity}
        )
        if not created:
            item.quantity += quantity
            item.save()

        return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)


class CartItemRemoveView(APIView):
    """Видалити позицію з кошика"""
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, item_id):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        CartItem.objects.filter(cart=cart, id=item_id).delete()
        return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)


class OrderCreateView(APIView):
    """Оформити замовлення на основі поточного кошика"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart_items = cart.items.select_related('product').all()

        if not cart_items:
            return Response({"detail": "Кошик порожній"}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            order = Order.objects.create(
                user=request.user,
                delivery_method=request.data.get('delivery_method'),
                address=request.data.get('address', ''),
                recipient_phone=request.data.get('recipient_phone'),
                payment_method=request.data.get('payment_method'),
                total_amount=0,
            )

            total = 0
            for cart_item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    price_at_purchase=cart_item.product.price,
                )
                total += cart_item.product.price * cart_item.quantity

            order.total_amount = total
            order.save()

            cart_items.delete()  # очищаємо кошик після оформлення

        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


class OrderHistoryView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Order.objects.filter(user=self.request.user)
        ordering = self.request.query_params.get('ordering', '-created_at')
        allowed = {'created_at', '-created_at', 'status', '-status'}
        if ordering not in allowed:
            ordering = '-created_at'
        return queryset.order_by(ordering)


class OrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)