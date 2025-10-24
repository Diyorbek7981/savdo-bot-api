from django.contrib import admin
from .models import User, Category, Product, Order, OrderItem


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'telegram_id', 'first_name', 'user_name',
        'age', 'phone_number', 'language', 'created_at'
    )
    list_display_links = ('id', 'telegram_id', 'first_name', 'user_name')
    search_fields = ('telegram_id', 'first_name', 'user_name', 'phone_number')
    list_filter = ('language', 'is_registered')
    ordering = ('-created_at',)
    list_per_page = 25
    readonly_fields = ('created_at',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    list_display_links = ('id', 'name')
    search_fields = ('name',)
    ordering = ('name',)
    list_per_page = 25


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'category', 'price', 'unit', 'available'
    )
    list_display_links = ('id', 'name')
    list_filter = ('available', 'category')
    search_fields = ('name', 'category__name')
    ordering = ('-id',)
    autocomplete_fields = ('category',)
    list_editable = ('price', 'available')
    list_per_page = 25


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('total_price',)
    autocomplete_fields = ('product',)
    fields = ('product', 'quantity', 'total_price')
    show_change_link = True


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at', 'payment_type', 'address', 'total_price')
    list_display_links = ('id', 'user')
    list_filter = ('created_at', 'payment_type')
    search_fields = ('user__first_name', 'user__user_name', 'user__telegram_id', 'address')
    ordering = ('-created_at',)
    readonly_fields = ('total_price', 'created_at')
    inlines = [OrderItemInline]
    list_per_page = 20

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user').prefetch_related('items')

    def total_sum(self, obj):
        return f"{obj.total_price} so'm"


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'product', 'quantity', 'total_price')
    list_display_links = ('id', 'product')
    search_fields = ('product__name', 'order__user__first_name', 'order__user__user_name')
    autocomplete_fields = ('order', 'product')
    readonly_fields = ('total_price',)
    ordering = ('-id',)
    list_per_page = 25

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('order', 'product')
