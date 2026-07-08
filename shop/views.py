from django.shortcuts import render


def home(request):
    products = [
        {
            "name": "Galaxy S22 Ultra",
            "image": "shop/img/phones/s22.png",
            "price": "₹32999",
            "old_price": "₹74999",
            "save": "₹32999",
            "discount": "56%\nOFF",
        },
        {
            "name": "Galaxy M13 (4GB | 64 GB)",
            "image": "shop/img/phones/m13.png",
            "price": "₹10499",
            "old_price": "₹14999",
            "save": "₹4500",
            "discount": "56%\nOFF",
        },
        {
            "name": "Galaxy M33 (4GB | 64 GB)",
            "image": "shop/img/phones/m33.png",
            "price": "₹16999",
            "old_price": "₹24999",
            "save": "₹8000",
            "discount": "56%\nOFF",
        },
        {
            "name": "Galaxy M53 (4GB | 64 GB)",
            "image": "shop/img/phones/m53.png",
            "price": "₹31999",
            "old_price": "₹40999",
            "save": "₹9000",
            "discount": "56%\nOFF",
        },
        {
            "name": "Galaxy S22 Ultra",
            "image": "shop/img/phones/s22_green.png",
            "price": "₹67999",
            "old_price": "₹85999",
            "save": "₹18000",
            "discount": "56%\nOFF",
        },
    ]

    categories = [
        {"name": "Mobile", "image": "shop/img/categories/mobile.png", "active": True},
        {"name": "Cosmetics", "image": "shop/img/categories/cosmetics.png", "active": False},
        {"name": "Electronics", "image": "shop/img/categories/electronics.png", "active": False},
        {"name": "Furniture", "image": "shop/img/categories/furniture.png", "active": False},
        {"name": "Watches", "image": "shop/img/categories/watch.png", "active": False},
        {"name": "Decor", "image": "shop/img/categories/decor.png", "active": False},
        {"name": "Accessories", "image": "shop/img/categories/accessories.png", "active": False},
    ]

    brands = [
        {"image": "shop/img/brands/iphone.png", "name": "iPhone"},
        {"image": "shop/img/brands/realme.png", "name": "Realme"},
        {"image": "shop/img/brands/xiaomi.png", "name": "Xiaomi"},
    ]

    essentials = [
        {"name": "Daily Essentials", "image": "shop/img/essentials/daily.png", "active": True},
        {"name": "Vegetables", "image": "shop/img/essentials/vegetables.png", "active": False},
        {"name": "Fruits", "image": "shop/img/essentials/fruits.png", "active": False},
        {"name": "Strawberry", "image": "shop/img/essentials/strawberry.png", "active": False},
        {"name": "Mango", "image": "shop/img/essentials/mango.png", "active": False},
        {"name": "Cherry", "image": "shop/img/essentials/cherry.png", "active": False},
    ]

    return render(request, "shop/home.html", {
        "products": products,
        "categories": categories,
        "brands": brands,
        "essentials": essentials,
    })
