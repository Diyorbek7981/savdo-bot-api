from django.urls import path
from .views import UsersView, CreateUserView, UserGetView, GetUpdateUserView, OrderView, CategoryView, OrderCreatView, \
    UserOrdersRetrieveView, ProductsByCategoryView, ProductRetrieveAPIView

urlpatterns = [
    path('users/', UsersView.as_view(), name='users'),
    path('create_user/', CreateUserView.as_view(), name='create'),
    path('users/<str:telegram_id>/', UserGetView.as_view(), name='user'),
    path('user_update/<str:telegram_id>/', GetUpdateUserView.as_view(), name='user'),
    path('order/', OrderView.as_view(), name='order'),
    path('order_creat/', OrderCreatView.as_view(), name='order_creat'),
    path('user_orders/<int:user_id>/', UserOrdersRetrieveView.as_view(), name='user-orders'),
    path('cat_list/', CategoryView.as_view(), name='cat_list'),
    path('prod_categ/<int:category_id>/', ProductsByCategoryView.as_view(), name='products-by-category'),
    path('products/<int:id>/', ProductRetrieveAPIView.as_view(), name='product-detail'),
]
