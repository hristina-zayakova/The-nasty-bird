from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

# Register your models here.

user = get_user_model()

@admin.register(user)
class CustomUserAdmin(BaseUserAdmin):
    list_display = ['email', 'is_active', 'is_staff', 'onboarding_step']
    ordering = ['email']

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Onboarding', {'fields': ('onboarding_step',)}),
        ('Important dates', {'fields': ('last_login', 'created_at')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )

    readonly_fields = ('created_at', 'updated_at')