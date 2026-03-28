from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
    # Remove 'username' from the list display
    list_display = ["email", "role", "institute", "academic_class", "is_staff"]
    list_filter = ["role", "institute", "academic_class"]
    search_fields = ["email"]
    ordering = ["email"]
    filter_horizontal = ()

    # override fieldsets to remove 'username'
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name")}),
        ("Academic & Role Info", {
            "fields": ("role", "institute", "academic_class", "stream", "guardian", "mentor")
        }),
        ("Permissions", {
            "fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")
        }),
        ("Gamification", {"fields": ("is_verified", "login_count")}),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )

    # Required when creating a user via the admin panel
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "password", "role", "institute", "is_active"),
        }),
    )

admin.site.register(User, CustomUserAdmin)