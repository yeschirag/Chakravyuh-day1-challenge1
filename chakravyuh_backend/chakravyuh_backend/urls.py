"""
This is the main URL configuration for your project.
It just tells Django where your 'admin' and 'api' apps live.
"""
from django.contrib import admin
from django.urls import path, include  # Make sure 'include' is imported

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # This line "plugs in" your api/urls.py file
    path('api/', include('api.urls')), 
]

