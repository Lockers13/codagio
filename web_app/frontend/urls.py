from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('user_submission/', views.user_sub, name="user_sub"),
]
