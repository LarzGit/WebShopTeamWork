from django.conf import settings
from django.db import models


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