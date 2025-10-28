from django.contrib import admin
from django.utils.html import format_html
from .models import User, Category, Product, Order, OrderItem, ProductNameCategory
from modeltranslation.admin import TranslationAdmin


# translate u-n jazzmin admin paneli uchun UI
class TaskAdmin(admin.ModelAdmin):
    class Media:
        js = (
            'http://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js',
            'http://ajax.googleapis.com/ajax/libs/jqueryui/1.10.2/jquery-ui.min.js',
            'modeltranslation/js/tabbed_translation_fields.js',
            'admin/js/jquery.init.js',
        )
        css = {
            'screen': ('modeltranslation/css/tabbed_translation_fields.css',),
        }


# -------------------------------
# USER ADMIN
# -------------------------------
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'telegram_id', 'first_name', 'user_name',
        'age', 'phone_number', 'language', 'is_registered', 'created_at'
    )
    list_display_links = ('id', 'telegram_id', 'first_name', 'user_name')
    search_fields = ('telegram_id', 'first_name', 'user_name', 'phone_number')
    list_filter = ('language', 'is_registered', 'created_at')
    ordering = ('-created_at',)
    list_per_page = 25
    readonly_fields = ('created_at',)


# -------------------------------
# CATEGORY ADMIN
# -------------------------------
@admin.register(Category)
class CategoryAdmin(TranslationAdmin, TaskAdmin):
    list_display = ('id', 'name')
    list_display_links = ('id', 'name')
    search_fields = ('name',)
    ordering = ('name',)
    list_per_page = 25


# -------------------------------
# PRODUCT NAME CATEGORY ADMIN
# -------------------------------
@admin.register(ProductNameCategory)
class ProductNameCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category',)
    list_display_links = ('id', 'name', 'category',)
    search_fields = ('name',)
    list_filter = ('category',)
    ordering = ('name',)
    autocomplete_fields = ('category',)
    list_per_page = 25


# -------------------------------
# PRODUCT ADMIN
# -------------------------------
@admin.register(Product)
class ProductAdmin(TranslationAdmin, TaskAdmin):
    list_display = (
        'id', 'name', 'name_category', 'price', 'unit',
        'quantity', 'available', 'image_preview'
    )
    list_display_links = ('id', 'name')
    list_filter = ('available', 'name_category')
    search_fields = ('name', 'name_category__name')
    ordering = ('-id',)
    autocomplete_fields = ('name_category',)
    list_editable = ('price', 'available', 'quantity',)
    readonly_fields = ('image_preview',)
    list_per_page = 25

    def image_preview(self, obj):
        if obj.image:
            return format_html(f'<img src="{obj.image.url}" width="50" height="50" style="border-radius:6px;" />')
        return "—"

    image_preview.short_description = "Rasm"


# -------------------------------
# ORDER ITEM INLINE (Order ichida)
# -------------------------------
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('total_price',)
    autocomplete_fields = ('product',)
    fields = ('product', 'quantity', 'total_price')
    show_change_link = True


# -------------------------------
# ORDER ADMIN
# -------------------------------
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'status', 'is_confirmed', 'total_price',
        'created_at',)
    list_display_links = ('id', 'user')
    list_filter = ('status', 'is_confirmed', 'created_at')
    search_fields = (
        'user__first_name', 'user__user_name', 'user__telegram_id'
    )
    ordering = ('-created_at',)
    readonly_fields = ('total_price', 'created_at')
    list_editable = ('status',)
    inlines = [OrderItemInline]
    list_per_page = 20
    autocomplete_fields = ('user',)
