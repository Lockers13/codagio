from django.urls import path
from django.contrib.auth import views as auth_views
from . import views  as user_views

urlpatterns = [
    path('profile/', user_views.profile, name="profile"),
    path('profile_stats/', user_views.ProfileStatsView.as_view(), name="profile_stats"),
    path('profile/delete/<int:pk>/', user_views.delete_solution, name="delete_solution"),
    path('profile/delete_response/', user_views.delete_response, name="delete_response"),
    path('profile/solution/view/', user_views.solution_view, name="solution_view"),
    path('profile/problem/view/', user_views.problem_view, name="problem_view"),
]
