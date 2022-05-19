# Django imports
from django.urls import path

# Project imports
from . import views

app_name = 'projects'
urlpatterns = [
    # API Web Panel
    path("", views.test, name="test"),
    path("apitest", views.api_test, name='apitest'),

    # API utilities
    path("project_list", views.project_list, name="project_list"),
    path("create_project", views.create_project, name="create_project"),
    path("project/<int:pk>", views.project_detail, name="project"),
    
]
