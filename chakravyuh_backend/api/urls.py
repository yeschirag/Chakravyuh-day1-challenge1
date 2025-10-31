from django.urls import path
from . import views  # Imports views from the same (api) folder
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

# In your project's main urls.py, this file is included under '/api/'
urlpatterns = [
    # POST to /api/login/ with username/password to get a token
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    
    # POST to /api/token/refresh/ with refresh token to get a new access token
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # GET /api/riddle/ (with auth token)
    path('riddle/', views.get_riddle, name='get-riddle'),
    
    # POST /api/submit/ (with auth token)
    path('submit/', views.submit_answer, name='submit-answer'),
]

