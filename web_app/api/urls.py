from django.urls import path
from django.contrib.auth import views as auth_views
from . import views as api_views

urlpatterns = [
    path('profile/delete/solution/<int:pk>/', api_views.delete_solution, name="delete_solution"),
    path('profile/delete/problem/<int:pk>/', api_views.delete_problem, name="delete_problem"),
    path('profile/stats/', api_views.ProfileStatsView.as_view(), name="profile_stats"),
    path("code/analysis/", api_views.AnalysisView.as_view(), name="analysis"),
    path('code/save_problem/', api_views.SaveProblemView.as_view(), name="save_problem"),
    path('courses/create_course/', api_views.create_course, name="create_course"),
    path('courses/enrol_course/<str:course_code>/', api_views.enrol_course, name="enrol_course"),
    path('courses/get_course/', api_views.get_course, name="get_course"),
    path('courses/delete/<str:del_type>/<int:del_id>/', api_views.delete_entity, name="delete_entity"),
    path('courses/get_global_problem_stats/<int:problem_id>/<int:course_id>/<str:role>/', api_views.get_global_problem_stats, name="get_global_problem_stats"),
    # path('save_problem/', code_views.SaveProblemView.as_view(), name="save_problem"),
]

