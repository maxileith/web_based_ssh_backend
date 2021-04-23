from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('ssh/', include('ssh.urls')),
    path('auth/', include('app_auth.urls')),
    path('saved_sessions/', include('saved_sessions.urls')),
    path('known_hosts/', include('known_hosts.urls')),
    path('personal_data/', include('personal_data.urls'))
]
