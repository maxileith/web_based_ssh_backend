from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('all/', views.all, name="all"),
    path('details/<int:id>', views.details, name="details"),
]
