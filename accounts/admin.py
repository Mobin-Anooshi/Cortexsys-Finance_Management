from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from .models import User


class UserAdmin(BaseUserAdmin):
    model = User
    list_display = ("id", "username", "email", "is_superuser", "is_active", "created")
    list_filter = ("is_superuser", "is_active")
    ordering = ("-created",)

    fieldsets = (
        (None, {"fields": ("username", "email", "password")}),
        ("permissions", {"fields": ("is_active", "is_superuser")}),
    )

    add_fieldsets = (
        ("Add member", {"fields": ("username", "email", "password", "is_active", "is_superuser"),}),
    )
    filter_horizontal = ()


admin.site.unregister(Group)
admin.site.register(User, UserAdmin)
