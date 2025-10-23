from django.contrib import admin
from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'telegram_id', 'first_name', 'user_name', 'age', 'phone_number', 'language')
    list_display_links = ('id', 'telegram_id', 'first_name', 'user_name', 'age', 'phone_number', 'language')
    ordering = ('-created_at',)
