from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('user_submission/<sub_type>', views.user_sub, name="user_sub"),
]
