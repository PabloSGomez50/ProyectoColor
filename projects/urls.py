# Django imports
from django.urls import path

# Project imports
from . import views

app_name = 'projects'
urlpatterns = [
    # API Web Panel
    path("", views.index, name="index"),

    # API utilities
    path("api", views.api, name="new_photo")
]
