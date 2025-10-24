from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import User, Product, Order, OrderItem, Category
from .serializers import UsersSerializer, ProductSerializer, OrderSerializer, OrderItemSerializer, CategorySerializer, \
    OrderDetailSerializer
from rest_framework import generics, permissions


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

class OrderView(generics.ListAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.AllowAny]


class OrderCreatView(generics.CreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.AllowAny]


class UserOrdersRetrieveView(generics.RetrieveAPIView):
    serializer_class = OrderDetailSerializer

    def get(self, request, user_id, *args, **kwargs):
        orders = (
            Order.objects
            .filter(user_id=user_id)
            .order_by('-created_at')
        )

        if not orders.exists():
            return Response(
                {"detail": "Bu foydalanuvchiga tegishli buyurtma topilmadi."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = self.get_serializer(orders, many=True)
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
