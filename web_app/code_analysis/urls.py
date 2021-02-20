from django.urls import path
from django.contrib.auth import views as auth_views
from . import views as code_views

urlpatterns = [
    path('solution/<int:prob_id>', code_views.solution_upload, name="solution"),
    path("analysis/", code_views.AnalysisView.as_view(), name="analysis"),
]

