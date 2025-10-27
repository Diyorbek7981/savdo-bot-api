from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import User, Product, Order, OrderItem, Category
from .serializers import UsersSerializer, ProductSerializer, OrderSerializer, OrderItemSerializer, CategorySerializer, \
    OrderItemCreateSerializer
from rest_framework import generics, permissions
from decimal import Decimal
from django.utils import timezone
from django.db.models import Sum, Count, Max


class UsersView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UsersSerializer
    permission_classes = [permissions.AllowAny]


class CreateUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UsersSerializer
    permission_classes = [permissions.AllowAny]


class GetUpdateUserView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UsersSerializer
    lookup_field = "telegram_id"
    lookup_url_kwarg = "telegram_id"

    def patch(self, request, *args, **kwargs):
        telegram_id = kwargs.get("telegram_id")

        try:
            user = User.objects.get(telegram_id=telegram_id)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)


class UserGetView(APIView):
    def get(self, request, telegram_id, format=None):
        try:
            user = User.objects.get(telegram_id=telegram_id)
        except User.DoesNotExist:
            return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        # Serialize the user data and return it in the response
        serializer = UsersSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


# //////////////////////////////////////////////////////////////////////////////////////////////////
class OrderCreatView(generics.CreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.AllowAny]


class UserOrdersRetrieveView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer

    def get(self, request, user_id, *args, **kwargs):
        order = (
            Order.objects
            .filter(user_id=user_id)
            .order_by('-created_at')
            .first()
        )

        if not order:
            return Response(
                {"detail": "Bu foydalanuvchiga tegishli buyurtma topilmadi."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = self.get_serializer(order)
        return Response(serializer.data)


class UserActiveOrdersView(generics.ListAPIView):
    serializer_class = OrderSerializer

    def get_queryset(self):
        user_id = self.kwargs.get("user_id")
        return (
            Order.objects
            .filter(user_id=user_id, is_confirmed=True)
            .exclude(status="completed")
            .order_by("-created_at")
        )

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset.exists():
            return Response(
                {"detail": "Foydalanuvchining faol buyurtmalari topilmadi."},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserOrderUpdateView(generics.UpdateAPIView):
    serializer_class = OrderSerializer
    queryset = Order.objects.all()

    def patch(self, request, user_id, *args, **kwargs):
        order = (
            Order.objects
            .filter(user_id=user_id)
            .order_by('-created_at')
            .first()
        )

        if not order:
            return Response(
                {"detail": "Bu foydalanuvchiga tegishli buyurtma topilmadi."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = self.get_serializer(order, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)


class CategoryView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]


class ProductsByCategoryView(generics.ListAPIView):
    serializer_class = ProductSerializer

    def get(self, request, category_id, *args, **kwargs):
        products = Product.objects.filter(category_id=category_id, available=True)

        if not products.exists():
            return Response(
                {"detail": "Bu kategoriyaga tegishli mahsulot topilmadi."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)


class ProductRetrieveAPIView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = 'id'


class OrderItemCreatView(generics.CreateAPIView):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemCreateSerializer
    permission_classes = [permissions.AllowAny]


class OrderItemUpdateView(generics.UpdateAPIView):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemCreateSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'id'


class OrderDeleteView(generics.DestroyAPIView):
    queryset = Order.objects.all()
    permission_classes = [permissions.AllowAny]
    lookup_field = "id"

    def delete(self, request, *args, **kwargs):
        order_id = kwargs.get("id")
        try:
            order = Order.objects.get(id=order_id)
            order.delete()
            return Response(
                {"detail": f"Order ID {order_id} muvaffaqiyatli o‘chirildi."},
                status=status.HTTP_204_NO_CONTENT
            )
        except Order.DoesNotExist:
            return Response(
                {"detail": f"Order ID {order_id} topilmadi."},
                status=status.HTTP_404_NOT_FOUND
            )


# /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


class MonthlyTopCustomersAPIView(APIView):
    def get(self, request):
        now = timezone.now()
        start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        orders = Order.objects.filter(created_at__gte=start_of_month, is_confirmed=True, status="completed")

        if not orders.exists():
            return Response(
                {"message": "Bu oyda hali hech kim buyurtma qilmagan."},
                status=status.HTTP_200_OK
            )

        # 🔹 Har bir foydalanuvchi bo‘yicha umumiy summa, buyurtmalar soni, oxirgi buyurtma sanasi
        stats = (
            orders.values(
                "user__id",
                "user__first_name",
                "user__user_name",
                "user__phone_number",
                "user__language",
            )
            .annotate(
                total_spent=Sum("total_price"),
                order_count=Count("id"),
                last_order=Max("created_at"),
            )
            .order_by("-total_spent")  # Eng ko‘p xarid qilganlar birinchi
        )

        result = []
        for s in stats:
            result.append({
                "user_id": s["user__id"],
                "first_name": s["user__first_name"],
                "username": s["user__user_name"],
                "phone_number": s["user__phone_number"],
                "language": s["user__language"],
                "total_spent_this_month": float(s["total_spent"] or 0),
                "total_orders_this_month": s["order_count"],
                "last_order_date": s["last_order"].strftime("%Y-%m-%d %H:%M:%S"),
            })

        return Response(result, status=status.HTTP_200_OK)
