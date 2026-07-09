from django.db.models import Avg, Q
from rest_framework import generics, permissions, parsers
from .models import Product, Category
from .serializers import ProductSerializer, CategorySerializer


class ProductListCreateView(generics.ListCreateAPIView):
    serializer_class = ProductSerializer
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = Product.objects.annotate(avg_rating=Avg('reviews__rating'))
        params = self.request.query_params

        # Пошук за назвою та описом
        search = params.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(description__icontains=search)
            )

        # Фільтр за категорією
        category = params.get('category')
        if category:
            queryset = queryset.filter(category_id=category)

        # Фільтр за ціною (діапазон)
        min_price = params.get('min_price')
        max_price = params.get('max_price')
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)

        # Фільтр за рейтингом (мінімальний середній рейтинг)
        min_rating = params.get('min_rating')
        if min_rating:
            queryset = queryset.filter(avg_rating__gte=min_rating)

        # Фільтр за наявністю
        in_stock = params.get('in_stock')
        if in_stock == 'true':
            queryset = queryset.filter(stock__gt=0)
        elif in_stock == 'false':
            queryset = queryset.filter(stock=0)

        # Сортування
        ordering = params.get('ordering')
        allowed_ordering = {
            'price', '-price',
            'avg_rating', '-avg_rating',
            'created_at', '-created_at',
            'name', '-name',
        }
        if ordering in allowed_ordering:
            queryset = queryset.order_by(ordering)

        return queryset


class ProductDetailUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.annotate(avg_rating=Avg('reviews__rating'))
    serializer_class = ProductSerializer
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class CategoryDetailUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]