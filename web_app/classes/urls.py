from django.urls import path
from . import views as course_views

urlpatterns = [
    # path('create_course_view/', course_views.create_course_view, name="create_course_view"),
    path('search_course_view/<str:user_role>/', course_views.search_course_view, name="search_course_view"),
    path('course_landing/<int:course_id>/', course_views.course_landing, name="course_landing"),
    path('delete_response/<str:del_type>/<int:course_id>/', course_views.delete_response, name="delete_response"),
    path('problem_view/<int:course_id>/<int:prob_id>/<str:user_role>/', course_views.problem_view, name="problem_view"),
]
