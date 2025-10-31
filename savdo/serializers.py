from rest_framework import serializers
from .models import User, Category, Product, Order, OrderItem, ProductNameCategory


class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


class ProdNameCategorySerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = ProductNameCategory
        fields = ['id', 'name', 'category_name', 'category']


class ProductSerializer(serializers.ModelSerializer):
    name_category_name = serializers.CharField(source='name_category.name', read_only=True)
    category = serializers.CharField(source='name_category.category.name', read_only=True)
    category_id = serializers.CharField(source='name_category.category.id', read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'unit', 'available', 'category', 'photo', "quantity",
                  "description", "name_category", "name_category_name", "category_id"]

    photo = serializers.CharField(source='image_path')


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_price = serializers.DecimalField(source='product.price', max_digits=10, decimal_places=2, read_only=True)
    category_name = serializers.CharField(source='product.name_category.category.name', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'category_name', 'product_price', 'quantity', 'total_price']


class OrderItemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'order', 'quantity']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'created_at', 'is_confirmed', 'status', 'total_price', 'items']
