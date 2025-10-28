from django.db import models
from decimal import Decimal


class User(models.Model):
    telegram_id = models.CharField(max_length=100, blank=True, null=True)
    first_name = models.CharField(max_length=100, blank=True, null=True)
    user_name = models.CharField(max_length=100, default="no username")
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


class ProductNameCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products")
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return f"{self.name} -- {self.category.name}"


class Product(models.Model):
    name = models.CharField(max_length=50)
    name_category = models.ForeignKey(ProductNameCategory, on_delete=models.CASCADE, related_name="product_names")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=50, default="dona")
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    available = models.BooleanField(default=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    description = models.TextField(blank=True, null=True, max_length=100)

    def __str__(self):
        return f"{self.name} ({self.name_category.name})"

    @property
    def image_path(self):
        return self.image.path

    def save(self, *args, **kwargs):
        if self.quantity <= 0:
            self.available = False
        else:
            self.available = True
        super().save(*args, **kwargs)


class Order(models.Model):
    STATUS_CHOICES = [
        ('preparing', "🍳 Buyurtmangiz kutilmoqda"),
        ('delivering', "🚚 Buyurtmangiz qabul qilindi"),
        ('completed', "✅ Yakunlangan"),
        ('cancelled', "❌ Bekor qilingan"),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    created_at = models.DateTimeField(auto_now_add=True)
    is_confirmed = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    total_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return f"Order #{self.id} — {self.user.first_name or self.user.telegram_id}"

    def calculate_total(self):
        total = sum((item.total_price or 0) for item in self.items.all())
        self.total_price = total
        self.save(update_fields=["total_price"])
        return total

    def save(self, *args, **kwargs):
        # Avval eski holatni olish uchun bazadan tekshiramiz
        if self.pk:
            old_status = Order.objects.get(pk=self.pk).status
        else:
            old_status = None

        super().save(*args, **kwargs)

        # ✅ Agar status 'completed' bo'lsa, Product miqdorini kamaytirish
        if self.status == "completed" and old_status != "completed":
            for item in self.items.all():
                product = item.product
                if product.quantity >= item.quantity:
                    product.quantity -= item.quantity
                else:
                    product.quantity = Decimal('0.00')
                    product.available = False  # agar qolmasa, mavjud emas deb belgilanadi
                product.save(update_fields=["quantity", "available"])


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
