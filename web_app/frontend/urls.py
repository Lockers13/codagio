from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.index),
    path('user_submission/<sub_type>', views.user_sub, name="user_sub"),
    path('register/', views.register, name="register"),
    path('login/', auth_views.LoginView.as_view(), name="login"),
    path('logout/', auth_views.LogoutView.as_view(), name="logout"),
]
