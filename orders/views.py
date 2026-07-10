from django.db import transaction
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Order, OrderItem, Cart, CartItem
from .serializers import OrderSerializer, CartSerializer
from django.shortcuts import get_object_or_404
from catalog.models import Product
from accounts.permissions import IsAdminRole


class CartView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        return Response(CartSerializer(cart).data)


class CartItemAddView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        product_id = request.data.get('product')
        quantity = request.data.get('quantity', 1)

        try:
            quantity = int(quantity)
        except (ValueError, TypeError):
            return Response({"detail": "quantity повинно бути числом"}, status=status.HTTP_400_BAD_REQUEST)

        if quantity < 1:
            return Response({"detail": "Кількість повинна бути більше 0"}, status=status.HTTP_400_BAD_REQUEST)

        product = get_object_or_404(Product, id=product_id)

        cart, _ = Cart.objects.get_or_create(user=request.user)
        item, created = CartItem.objects.get_or_create(
            cart=cart, product=product,
            defaults={'quantity': 0}   
        )

        new_quantity = item.quantity + quantity if not created else quantity

        if new_quantity > product.stock:
            return Response(
                {"detail": f"Недостатньо товару на складі. Доступно: {product.stock}, у кошику вже: {item.quantity if not created else 0}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        item.quantity = new_quantity
        item.save()

        return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)


class CartItemRemoveView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, item_id):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        CartItem.objects.filter(cart=cart, id=item_id).delete()
        return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)


class OrderCreateView(APIView):
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

            cart_items.delete()  

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
    

class CartItemUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, item_id):
        quantity = request.data.get('quantity')

        if quantity is None:
            return Response({"detail": "Поле quantity обов'язкове"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            quantity = int(quantity)
        except (ValueError, TypeError):
            return Response({"detail": "quantity повинно бути числом"}, status=status.HTTP_400_BAD_REQUEST)

        if quantity < 1:
            return Response({"detail": "Кількість повинна бути більше 0"}, status=status.HTTP_400_BAD_REQUEST)

        cart, _ = Cart.objects.get_or_create(user=request.user)
        item = get_object_or_404(CartItem, cart=cart, id=item_id)

        if quantity > item.product.stock:
            return Response(
                {"detail": f"Недостатньо товару на складі. Доступно: {item.product.stock}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        item.quantity = quantity
        item.save()

        return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)
    


class OrderStatusUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminRole]

    def patch(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        new_status = request.data.get('status')

        valid_statuses = [choice[0] for choice in Order.Status.choices]
        if new_status not in valid_statuses:
            return Response(
                {"detail": f"Невірний статус. Дозволені: {valid_statuses}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        order.status = new_status
        order.save()

        return Response(OrderSerializer(order).data, status=status.HTTP_200_OK)