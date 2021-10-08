from django.urls import path
from . import views as course_views

urlpatterns = [
    path('create_course/', course_views.create_course_view, name="create_course"),
]
