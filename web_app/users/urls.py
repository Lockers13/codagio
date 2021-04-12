from django.urls import path
from django.contrib.auth import views as auth_views
from . import views  as user_views

urlpatterns = [
    path('profile/', user_views.profile, name="profile"),
]
