from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Avg, Q
from django.shortcuts import render, redirect, get_object_or_404

from catalog.models import Product, Category, Review
from orders.models import Cart, CartItem, Order, OrderItem

User = get_user_model()


# Декоративні дані тільки для вітрини головної сторінки (картинок/брендів немає в моделях)
CATEGORIES = [
    {"name": "Mobile", "image": "shop/img/categories/mobile.png", "active": True},
    {"name": "Cosmetics", "image": "shop/img/categories/cosmetics.png", "active": False},
    {"name": "Electronics", "image": "shop/img/categories/electronics.png", "active": False},
    {"name": "Furniture", "image": "shop/img/categories/furniture.png", "active": False},
    {"name": "Watches", "image": "shop/img/categories/watch.png", "active": False},
    {"name": "Decor", "image": "shop/img/categories/decor.png", "active": False},
    {"name": "Accessories", "image": "shop/img/categories/accessories.png", "active": False},
]

SLIDES = [
    {
        "eyebrow": "Найкраща пропозиція на розумні годинники",
        "title": "SMART WEARABLE.",
        "subtitle": "Знижки до 80%",
        "image": "shop/img/hero/watch.png",
    },
    {
        "eyebrow": "Нова колекція смартфонів",
        "title": "MOBILE POWER.",
        "subtitle": "Знижки до 50%",
        "image": "shop/img/hero/watch.png",
    },
    {
        "eyebrow": "Техніка для дому",
        "title": "HOME ESSENTIALS.",
        "subtitle": "Знижки до 30%",
        "image": "shop/img/hero/watch.png",
    },
]

BRANDS = [
    {"image": "shop/img/brands/iphone.png", "name": "iPhone"},
    {"image": "shop/img/brands/realme.png", "name": "Realme"},
    {"image": "shop/img/brands/xiaomi.png", "name": "Xiaomi"},
]

ESSENTIALS = [
    {"name": "Daily Essentials", "image": "shop/img/essentials/daily.png", "active": True},
    {"name": "Vegetables", "image": "shop/img/essentials/vegetables.png", "active": False},
    {"name": "Fruits", "image": "shop/img/essentials/fruits.png", "active": False},
    {"name": "Strawberry", "image": "shop/img/essentials/strawberry.png", "active": False},
    {"name": "Mango", "image": "shop/img/essentials/mango.png", "active": False},
    {"name": "Cherry", "image": "shop/img/essentials/cherry.png", "active": False},
]


def _annotated_products():
    return Product.objects.annotate(avg_rating=Avg('reviews__rating')).select_related('category')


def home(request):
    products = _annotated_products().order_by('-created_at')[:8]
    return render(request, "shop/home.html", {
        "products": products,
        "categories": CATEGORIES,
        "brands": BRANDS,
        "essentials": ESSENTIALS,
        "slides": SLIDES,
    })


def catalog(request):
    products = _annotated_products()
    params = request.GET

    search = params.get('q', '').strip()
    if search:
        products = products.filter(Q(name__icontains=search) | Q(description__icontains=search))

    category_id = params.get('category')
    if category_id and category_id.isdigit():
        products = products.filter(category_id=category_id)
    else:
        category_id = ''

    min_price = params.get('min_price')
    max_price = params.get('max_price')
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)

    min_rating = params.get('min_rating')
    if min_rating:
        products = products.filter(avg_rating__gte=min_rating)

    in_stock = params.get('in_stock')
    if in_stock == 'true':
        products = products.filter(stock__gt=0)
    elif in_stock == 'false':
        products = products.filter(stock=0)

    ordering = params.get('ordering')
    allowed_ordering = {'price', '-price', 'avg_rating', '-avg_rating', 'created_at', '-created_at', 'name', '-name'}
    products = products.order_by(ordering) if ordering in allowed_ordering else products.order_by('-created_at')

    paginator = Paginator(products, 12)
    page_obj = paginator.get_page(params.get('page'))

    return render(request, "shop/catalog.html", {
        "page_obj": page_obj,
        "products": page_obj.object_list,
        "categories": Category.objects.all(),
        "query": search,
        "selected_category": category_id,
        "ordering": ordering or '-created_at',
        "min_price": min_price or '',
        "max_price": max_price or '',
        "min_rating": min_rating or '',
        "in_stock": in_stock or '',
    })


def product_detail(request, pk):
    product = get_object_or_404(_annotated_products(), pk=pk)
    reviews = product.reviews.select_related('user').order_by('-created_at')

    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, "Щоб залишити відгук, увійдіть у систему.")
            return redirect('shop_login')

        rating = request.POST.get('rating')
        comment = request.POST.get('comment', '')
        if Review.objects.filter(product=product, user=request.user).exists():
            messages.error(request, "Ви вже залишали відгук на цей товар.")
        elif not rating or not (1 <= int(rating) <= 5):
            messages.error(request, "Оцінка має бути від 1 до 5.")
        else:
            Review.objects.create(product=product, user=request.user, rating=rating, comment=comment)
            messages.success(request, "Дякуємо за відгук!")
        return redirect('product_detail', pk=pk)

    return render(request, "shop/product_detail.html", {
        "product": product,
        "reviews": reviews,
    })


def register(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')

        errors = []
        if not username or not email or not password1:
            errors.append("Заповніть усі поля.")
        if len(password1) < 8:
            errors.append("Пароль має містити щонайменше 8 символів.")
        if password1 != password2:
            errors.append("Паролі не збігаються.")
        if User.objects.filter(username=username).exists():
            errors.append("Такий логін вже зайнятий.")
        if User.objects.filter(email=email).exists():
            errors.append("Такий email вже зареєстровано.")

        if errors:
            for e in errors:
                messages.error(request, e)
            return render(request, "shop/register.html", {"username": username, "email": email})

        user = User.objects.create_user(username=username, email=email, password=password1)
        login(request, user)
        messages.success(request, "Реєстрація успішна, вітаємо в MegaMart!")
        return redirect('home')

    return render(request, "shop/register.html")


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if not user.is_active:
                messages.error(request, "Ваш акаунт заблоковано.")
                return render(request, "shop/login.html", {"username": username})
            login(request, user)
            messages.success(request, f"Раді бачити знову, {user.username}!")
            next_url = request.GET.get('next') or request.POST.get('next')
            return redirect(next_url or 'home')
        messages.error(request, "Невірний логін або пароль.")
        return render(request, "shop/login.html", {"username": username})

    return render(request, "shop/login.html")


def logout_view(request):
    logout(request)
    messages.info(request, "Ви вийшли з акаунту.")
    return redirect('home')


@login_required(login_url='shop_login')
def profile(request):
    if request.method == 'POST':
        request.user.first_name = request.POST.get('first_name', '')
        request.user.last_name = request.POST.get('last_name', '')
        request.user.phone = request.POST.get('phone', '')
        request.user.save()
        messages.success(request, "Профіль оновлено.")
        return redirect('profile')

    return render(request, "shop/profile.html")


@login_required(login_url='shop_login')
def cart_view(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    items = cart.items.select_related('product').all()
    return render(request, "shop/cart.html", {"cart": cart, "items": items})


@login_required(login_url='shop_login')
def cart_add(request, product_id):
    if request.method != 'POST':
        return redirect('catalog')

    product = get_object_or_404(Product, pk=product_id)
    try:
        quantity = int(request.POST.get('quantity', 1))
    except (TypeError, ValueError):
        quantity = 1
    quantity = max(quantity, 1)

    cart, _ = Cart.objects.get_or_create(user=request.user)
    item, created = CartItem.objects.get_or_create(cart=cart, product=product, defaults={'quantity': 0})
    new_quantity = item.quantity + quantity

    if new_quantity > product.stock:
        messages.error(request, f"Недостатньо товару на складі. Доступно: {product.stock}.")
    else:
        item.quantity = new_quantity
        item.save()
        messages.success(request, f"«{product.name}» додано до кошика.")

    return redirect('cart')


@login_required(login_url='shop_login')
def cart_update(request, item_id):
    if request.method != 'POST':
        return redirect('cart')

    cart, _ = Cart.objects.get_or_create(user=request.user)
    item = get_object_or_404(CartItem, cart=cart, pk=item_id)
    try:
        quantity = int(request.POST.get('quantity', 1))
    except (TypeError, ValueError):
        quantity = item.quantity

    if quantity < 1:
        item.delete()
    elif quantity > item.product.stock:
        messages.error(request, f"Недостатньо товару на складі. Доступно: {item.product.stock}.")
    else:
        item.quantity = quantity
        item.save()

    return redirect('cart')


@login_required(login_url='shop_login')
def cart_remove(request, item_id):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    CartItem.objects.filter(cart=cart, pk=item_id).delete()
    messages.info(request, "Товар видалено з кошика.")
    return redirect('cart')


@login_required(login_url='shop_login')
def checkout(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    items = cart.items.select_related('product').all()

    if not items:
        messages.warning(request, "Ваш кошик порожній.")
        return redirect('cart')

    if request.method == 'POST':
        delivery_method = request.POST.get('delivery_method')
        address = request.POST.get('address', '')
        recipient_phone = request.POST.get('recipient_phone')
        payment_method = request.POST.get('payment_method')

        if not delivery_method or not recipient_phone or not payment_method:
            messages.error(request, "Заповніть усі обов'язкові поля.")
            return render(request, "shop/checkout.html", {"cart": cart, "items": items})

        with transaction.atomic():
            for item in items:
                if item.quantity > item.product.stock:
                    messages.error(request, f"«{item.product.name}»: на складі лишилось {item.product.stock} шт.")
                    return render(request, "shop/checkout.html", {"cart": cart, "items": items})

            order = Order.objects.create(
                user=request.user,
                delivery_method=delivery_method,
                address=address,
                recipient_phone=recipient_phone,
                payment_method=payment_method,
                total_amount=0,
            )
            total = 0
            for item in items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price_at_purchase=item.product.price,
                )
                item.product.stock -= item.quantity
                item.product.save()
                total += item.product.price * item.quantity

            order.total_amount = total
            order.save()
            items.delete()

        return redirect('order_success', pk=order.pk)

    return render(request, "shop/checkout.html", {"cart": cart, "items": items})


@login_required(login_url='shop_login')
def order_success(request, pk):
    order = get_object_or_404(Order, pk=pk, user=request.user)
    return render(request, "shop/order_success.html", {"order": order})


@login_required(login_url='shop_login')
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, "shop/orders_history.html", {"orders": orders})


@login_required(login_url='shop_login')
def order_detail(request, pk):
    order = get_object_or_404(Order.objects.prefetch_related('items__product'), pk=pk, user=request.user)
    return render(request, "shop/order_detail.html", {"order": order})