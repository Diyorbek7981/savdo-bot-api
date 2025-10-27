from django.urls import path
from .views import UsersView, CreateUserView, UserGetView, GetUpdateUserView, CategoryView, OrderCreatView, \
    UserOrdersRetrieveView, ProductsByCategoryView, ProductRetrieveAPIView, OrderItemCreatView, OrderItemUpdateView, \
    OrderDeleteView, UserOrderUpdateView, UserActiveOrdersView, MonthlyTopCustomersAPIView

urlpatterns = [
    path('users/', UsersView.as_view(), name='users'),
    path('create_user/', CreateUserView.as_view(), name='create'),
    path('users/<str:telegram_id>/', UserGetView.as_view(), name='user'),
    path('user_update/<str:telegram_id>/', GetUpdateUserView.as_view(), name='user'),
    path('order_del/<int:id>/', OrderDeleteView.as_view(), name='order_del'),
    path('order_creat/', OrderCreatView.as_view(), name='order_creat'),
    path('user_orders/<int:user_id>/', UserOrdersRetrieveView.as_view(), name='user_orders'),
    path('cat_list/', CategoryView.as_view(), name='cat_list'),
    path('prod_categ/<int:category_id>/', ProductsByCategoryView.as_view(), name='products_by_category'),
    path('products/<int:id>/', ProductRetrieveAPIView.as_view(), name='product-detail'),
    path('order_item_creat/', OrderItemCreatView.as_view(), name='order_item_creat'),
    path('orderit_update/<int:id>/', OrderItemUpdateView.as_view(), name='orderitem_update'),
    path('user_order_update/<int:user_id>/', UserOrderUpdateView.as_view(), name='user_order_update'),
    path("orders_list/<int:user_id>/", UserActiveOrdersView.as_view(), name="user_active_orders"),
    path('top_monthly_customers/', MonthlyTopCustomersAPIView.as_view(), name='top-monthly-customers'),
]
