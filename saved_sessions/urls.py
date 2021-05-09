from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.sessions, name="sessions"),
    path('details/<int:id>', views.details, name="details"),
    path('details/<int:session_id>/key', views.ssh_key, name="ssh-key"),
]
