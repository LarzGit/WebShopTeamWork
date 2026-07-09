from rest_framework import serializers
from .models import Product, Category, Review


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


class ProductSerializer(serializers.ModelSerializer):
    avg_rating = serializers.FloatField(read_only=True, default=None)

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'category', 'stock', 'image', 'avg_rating']