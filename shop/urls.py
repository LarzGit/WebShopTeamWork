from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("catalog/", views.catalog, name="catalog"),
    path("register/", views.register, name="shop_register"),
    path("login/", views.login_view, name="shop_login"),
]