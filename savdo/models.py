from django.db import models
from decimal import Decimal


class User(models.Model):
    telegram_id = models.CharField(max_length=100, blank=True, null=True)
    first_name = models.CharField(max_length=100, blank=True, null=True)
    user_name = models.CharField(max_length=100, unique=True)
    age = models.PositiveIntegerField(blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    is_registered = models.BooleanField(default=False)
    language = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.user_name} ({self.phone_number})"


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products")
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=50, default="dona")
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.category.name})"

    @property
    def image_path(self):
        return self.image.path


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    categories = models.ManyToManyField('Category', blank=True, related_name='orders')
    created_at = models.DateTimeField(auto_now_add=True)
    is_confirmed = models.BooleanField(default=False)
    total_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return f"Order #{self.id} — {self.user.first_name or self.user.telegram_id}"

    def calculate_total(self):
        total = sum((item.total_price or 0) for item in self.items.all())
        self.total_price = total
        self.save(update_fields=["total_price"])
        return total


class OrderItem(models.Model):
    order = models.ForeignKey('Order', on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('1.00'))
    total_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        self.total_price = Decimal(self.product.price) * self.quantity
        super().save(*args, **kwargs)
        self.order.calculate_total()

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
