from django.urls import path
from django.contrib.auth import views as auth_views
from . import views as code_views

urlpatterns = [
    path('submission/<sub_type>', code_views.submission, name="submission"),
    path("analysis/", code_views.AnalysisView.as_view(), name="analysis"),
]

