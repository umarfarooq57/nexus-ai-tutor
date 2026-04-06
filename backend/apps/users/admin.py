from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'username', 'role', 'is_staff', 'email_verified', 'created_at')
    list_filter = ('role', 'is_staff', 'is_superuser', 'email_verified')
    ordering = ('email',)
    fieldsets = UserAdmin.fieldsets + (
        ('Profile', {'fields': ('role', 'bio', 'avatar')}),
        ('Verification', {'fields': ('email_verified', 'phone', 'phone_verified')}),
        ('Blockchain', {'fields': ('wallet_address', 'did')}),
        ('Preferences', {'fields': ('language', 'timezone', 'dark_mode')}),
    )
