from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login, name="login"),
    path('logout/', views.logout_view, name="logout"),
    path('register/', views.register, name="register"),
    path('verify/', views.verify, name="verify"),
    path('email/verify/<token>', views.verify_email, name="verify-email")
]
