from django.db.models import Avg, Q
from rest_framework import generics, permissions, parsers
from .models import Product, Category
from .serializers import ProductSerializer, CategorySerializer
from rest_framework import generics, permissions
from .models import Review
from .serializers import ReviewSerializer



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





class IsReviewOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user_id == request.user.id


class ReviewListCreateView(generics.ListCreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = Review.objects.all()
        product_id = self.request.query_params.get('product')
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ReviewDetailUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsReviewOwnerOrReadOnly]