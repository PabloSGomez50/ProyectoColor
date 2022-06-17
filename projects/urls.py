# Django imports
from django.urls import path

# Project imports
from . import views

app_name = 'projects'
urlpatterns = [
    # API Web Panel
    path("", views.test, name="test"),
    path("apitest", views.api_test, name='apitest'),
    # path("csrf", views.get_csrf, name="get_csrf"),
    path("refresh", views.session_view, name="session_view"),

    # API Projects
    path("project_list", views.project_list, name="project_list"),
    path("create_project", views.create_project, name="create_project"),
    path("project/<int:pk>", views.project_detail, name="project"),

    # API User
    path("register", views.register, name="register"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("profile/<int:pk>", views.get_user, name="get_user"),
    path("edit_user", views.edit_user, name="edit_user")
]
