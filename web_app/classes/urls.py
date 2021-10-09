from django.urls import path
from . import views as course_views

urlpatterns = [
    path('create_course_view/', course_views.create_course_view, name="create_course_view"),
    path('create_course/', course_views.create_course, name="create_course"),
    path('search_course_view/', course_views.search_course_view, name="search_course_view"),
    path('course_landing/<int:course_id>/', course_views.course_landing, name="course_landing"),
    path('enrol_course/', course_views.enrol_course, name="enrol_course"),
]
