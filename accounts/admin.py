from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('phone', 'role')}),
    )
    list_display = ['username', 'email', 'role', 'is_staff', 'is_active']


admin.site.register(CustomUser, CustomUserAdmin)