from django.urls import path
from django.contrib.auth import views as auth_views
from . import views as api_views

urlpatterns = [
    path('profile/delete/solution/<int:pk>/', api_views.delete_solution, name="delete_solution"),
    path('profile/delete/problem/<int:pk>/', api_views.delete_problem, name="delete_problem"),
    path('profile/stats/', api_views.ProfileStatsView.as_view(), name="profile_stats"),
    path("code/analysis/", api_views.AnalysisView.as_view(), name="analysis"),
    path('code/save_problem/', api_views.SaveProblemView.as_view(), name="save_problem"),
    path('code/save_problem/', api_views.SaveProblemView.as_view(), name="save_problem"),
    path('courses/create_course/', api_views.create_course, name="create_course"),
    path('courses/enrol_course/', api_views.enrol_course, name="enrol_course"),
    # path('save_problem/', code_views.SaveProblemView.as_view(), name="save_problem"),
]

