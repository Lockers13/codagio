from django.urls import path
from django.contrib.auth import views as auth_views
from . import views as code_views

urlpatterns = [
    path('solution/<int:prob_id>', code_views.solution_upload, name="solution"),
    path('save_problem/', code_views.SaveProblemView.as_view(), name="save_problem"),
    path('problem_upload/<str:problem_cat>', code_views.problem_upload, name="problem_upload"),
    path("analysis/", code_views.AnalysisView.as_view(), name="analysis"),
    path("analysis/<int:soln_id>", code_views.AnalysisView.as_view(), name="analysis_view_stats"),
    path("problem_view/<str:category>", code_views.problem_view, name="problem_view"),
]

