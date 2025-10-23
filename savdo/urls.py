from django.urls import path
from .views import UsersView,CreateUserView, UserGetView,GetUpdateUserView

urlpatterns = [
    path('users/', UsersView.as_view(), name='users'),
    path('create_user/', CreateUserView.as_view(), name='create'),
    path('users/<str:telegram_id>/', UserGetView.as_view(), name='user'),
    path('user_update/<str:telegram_id>/', GetUpdateUserView.as_view(), name='user'),
]
