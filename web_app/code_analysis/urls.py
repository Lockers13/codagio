from django.urls import path
from django.contrib.auth import views as auth_views
from . import views as code_views

urlpatterns = [
    path('solution/<int:prob_id>', code_views.solution_upload, name="solution"),
    path('problem_upload/<str:problem_cat>/<int:course_id>', code_views.problem_upload, name="problem_upload"),
    path("problem_view/<str:category>", code_views.problem_view, name="problem_view"),
]

