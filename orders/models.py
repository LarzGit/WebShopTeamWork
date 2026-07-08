from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from catalog.models import Product


class Order(models.Model):
    class Status(models.TextChoices):
        NEW = 'new', 'Нове'
        PROCESSING = 'processing', 'В обробці'
        SHIPPED = 'shipped', 'Відправлено'
        DELIVERED = 'delivered', 'Доставлено'
        CANCELLED = 'cancelled', 'Скасовано'

    class DeliveryMethod(models.TextChoices):
        COURIER = 'courier', 'Кур\'єр'
        PICKUP = 'pickup', 'Самовивіз'
        POST = 'post', 'Поштове відділення'

    class PaymentMethod(models.TextChoices):
        CARD_ONLINE = 'card_online', 'Картка онлайн'
        CASH_ON_DELIVERY = 'cash_on_delivery', 'Готівкою при отриманні'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NEW)
    delivery_method = models.CharField(max_length=20, choices=DeliveryMethod.choices)
    address = models.CharField(max_length=255, blank=True)
    recipient_phone = models.CharField(max_length=20)
    payment_method = models.CharField(max_length=20, choices=PaymentMethod.choices)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Order #{self.id} ({self.user})'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name="замовлення")
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, verbose_name="товар")
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)], verbose_name="кількість")
    price_at_purchase = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="ціна на момент купівлі"
    )

    @property
    def subtotal(self):
        return self.price_at_purchase * self.quantity

    def __str__(self):
        return f'{self.product} x{self.quantity} ({self.order})'


class Cart(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cart',
        verbose_name="користувач"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Кошик {self.user}'

    @property
    def total_amount(self):
        return sum(item.subtotal for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items', verbose_name="кошик")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="товар")
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)], verbose_name="кількість")

    class Meta:
        unique_together = ('cart', 'product')

    @property
    def subtotal(self):
        return self.product.price * self.quantity

    def __str__(self):
        return f'{self.product.name} x{self.quantity}'