# Django imports
from django.urls import path

# Project imports
from . import views

app_name = 'projects'
urlpatterns = [
    # API Web Panel
    path("", views.test, name="test"),
    path("apitest", views.api_test),

    # API utilities
    path("project_list", views.project_list, name="project_list"),
    path("projectunsafe", views.project_test),
    path("project/<int:pk>", views.project_detail, name="project"),
    
]
