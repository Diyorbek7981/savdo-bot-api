from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import User, Product, Order, OrderItem, Category
from .serializers import UsersSerializer, ProductSerializer, OrderSerializer, OrderItemSerializer, CategorySerializer, \
    OrderItemCreateSerializer
from rest_framework import generics, permissions
from decimal import Decimal


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
