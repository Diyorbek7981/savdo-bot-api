from django.contrib import admin
from .models import User, Category, Product, Order, OrderItem


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'telegram_id', 'first_name', 'user_name', 'age', 'phone_number', 'language')
    list_display_links = ('id', 'telegram_id', 'first_name', 'user_name', 'age', 'phone_number', 'language')
    ordering = ('-created_at',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    list_display_links = ('id', 'name')
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category', 'price', 'unit', 'available')
    list_display_links = ('id', 'name', 'category', 'price', 'unit', 'available')
    list_filter = ('available', 'category')
    search_fields = ('name', 'category__name')
    ordering = ('-id',)
    autocomplete_fields = ('category',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at', 'total_price', 'is_completed')
    list_display_links = ('id', 'user')
    list_filter = ('is_completed', 'created_at')
    search_fields = ('user__username', 'user__telegram_id')
    ordering = ('-created_at',)
    readonly_fields = ('total_price', 'created_at')

    # OrderItem ni inline tarzda ko‘rsatamiz
    class OrderItemInline(admin.TabularInline):
        model = OrderItem
        extra = 0
        readonly_fields = ('total_price',)

    inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'product', 'quantity', 'total_price')
    list_display_links = ('id', 'product')
    search_fields = ('product__name', 'order__user__username')
    autocomplete_fields = ('order', 'product')
    ordering = ('-id',)
