# Django imports
from django.urls import path

# Project imports
from . import views

app_name = 'projects'
urlpatterns = [
    # API Web Panel
    path("", views.test, name="test"),

    # API utilities
    path("project_list", views.project_list, name="project_list")
]
