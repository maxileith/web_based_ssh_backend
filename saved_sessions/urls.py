from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.sessions, name="sessions"),
    path('details/<int:id>', views.details, name="details"),
    path('details/<int:session_id>/upload_key', views.ssh_key_upload, name="ssh-key-upload"),
]
