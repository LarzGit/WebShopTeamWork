from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="назва категорії")

    class Meta:
        verbose_name = "Категорія"
        verbose_name_plural = "Категорії"

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=200, verbose_name="назва товару", db_index=True)
    description = models.TextField(blank=True, verbose_name="опис товару")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="ціна товару", db_index=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', verbose_name="категорія товару")
    stock = models.PositiveIntegerField(default=0, verbose_name="кількість товару")
    image = models.ImageField(upload_to='products/', blank=True, null=True, verbose_name="фото товару")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="дата додавання")

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товари"
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class Review(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name="користувач"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name="товар"
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="оцінка"
    )
    comment = models.TextField(blank=True, verbose_name="коментар")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="дата створення")

    class Meta:
        verbose_name = "Відгук"
        verbose_name_plural = "Відгуки"
        indexes = [
            models.Index(fields=['-created_at']),  
        ]

    def __str__(self):
        return f"{self.user} - {self.product} ({self.rating})"