from catalog.models import Category
from orders.models import Cart


def shop_context(request):
    cart_count = 0
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
        if cart:
            cart_count = sum(item.quantity for item in cart.items.all())
    return {
        'nav_categories': Category.objects.all(),
        'cart_count': cart_count,
    }