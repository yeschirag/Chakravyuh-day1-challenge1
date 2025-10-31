"""
This file contains the consolidated code for a basic Django backend
to run your Chakravyuh event.

Follow these steps to use it:
1.  Install Django:
    pip install django djangorestframework django-cors-headers

2.  Start a new Django project:
    django-admin startproject chakravyuh_backend
    cd chakravyuh_backend

3.  Create a new app to handle the game logic:
    python manage.py startapp api

4.  Configure your project's settings.py:
    - Add 'api', 'rest_framework', and 'corsheaders' to INSTALLED_APPS.
    - Add 'corsheaders.middleware.CorsMiddleware' to MIDDLEWARE.
    - Set `CORS_ALLOWED_ORIGINS = [ ...your_frontend_url... ]` or
      `CORS_ALLOW_ALL_ORIGINS = True` (for development).

5.  Split the code from this file into the correct files in your 'api' app:
    - Code under "# --- api/models.py ---" goes into `api/models.py`
    - Code under "# --- api/admin.py ---" goes into `api/admin.py`
    - Code under "# --- api/serializers.py ---" goes into a new file `api/serializers.py`
    - Code under "# --- api/views.py ---" goes into `api/views.py`
    - Code under "# --- api/urls.py ---" goes into a new file `api/urls.py`

6.  Configure your main project's `chakravyuh_backend/urls.py`:
    - Add: `from django.urls import path, include`
    - Add: `path('api/', include('api.urls')),` to your `urlpatterns` list.

7.  Run the database migrations:
    python manage.py makemigrations
    python manage.py migrate

8.  Create your admin superuser:
    python manage.py createsuperuser

9.  Run the server:
    python manage.py runserver
"""

# ==============================================================================
# --- api/models.py ---
# (Defines your database structure)
# ==============================================================================
from django.db import models
from django.contrib.auth.models import User

class Riddle(models.Model):
    """Stores a single riddle."""
    riddle_text = models.TextField(unique=True)
    # Just for your reference, not shown to user
    lead_name = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"Riddle #{self.id}: {self.riddle_text[:50]}..."

class TeamData(models.Model):
    """
    This is the most important model.
    It links a Team (User) to their assigned Riddle and their Final Answer.
    """
    # Use a OneToOneField to link to Django's built-in User model.
    # The User model already has 'username' (for Team ID) and 'password'.
    team = models.OneToOneField(User, on_delete=models.CASCADE)
    
    # The specific riddle assigned to this team
    assigned_riddle = models.ForeignKey(Riddle, on_delete=models.PROTECT)
    
    # The correct final decrypted answer for this team
    final_answer = models.CharField(max_length=255, help_text="The exact, all-caps, decrypted string")
    
    # Track if they have successfully completed the challenge
    is_complete = models.BooleanField(default=False)

    def __str__(self):
        return f"Data for Team: {self.team.username}"


# ==============================================================================
# --- api/admin.py ---
# (Makes your models show up in the Django Admin Panel)
# ==============================================================================
from django.contrib import admin
# from .models import Riddle, TeamData # (Uncomment in actual file)

# Simple registration
admin.site.register(Riddle)

# A more advanced registration to show TeamData inline with the User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

class TeamDataInline(admin.StackedInline):
    model = TeamData
    can_delete = False
    verbose_name_plural = 'Team Game Data'

class UserAdmin(BaseUserAdmin):
    inlines = (TeamDataInline,)

# Unregister the base User model
admin.site.unregister(User)
# Register the User model with your new inline
admin.site.register(User, UserAdmin)


# ==============================================================================
# --- api/serializers.py ---
# (Tells Django REST Framework how to convert your models to JSON)
# ==============================================================================
from rest_framework import serializers
# from .models import Riddle # (Uncomment in actual file)

class RiddleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Riddle
        fields = ['riddle_text'] # Only send the riddle text


# ==============================================================================
# --- api/views.py ---
# (Defines your API endpoints - the actual logic)
# ==============================================================================
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import status
# from .models import TeamData
# from .serializers import RiddleSerializer

# We don't need a custom login view, we can use one from a library.
# We'll use "simple-jwt" for token-based authentication.
# The user will POST {'username': 'TEAM-001', 'password': '...'}
# and get back an access token.

@api_view(['GET'])
@permission_classes([IsAuthenticated]) # Ensures only logged-in users can access
def get_riddle(request):
    """
    API endpoint for a logged-in team to fetch their assigned riddle.
    """
    user = request.user
    try:
        # Find the game data associated with the logged-in user
        team_data = TeamData.objects.get(team=user)
        # Get their assigned riddle
        riddle = team_data.assigned_riddle
        # Convert the riddle object to JSON
        serializer = RiddleSerializer(riddle)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except TeamData.DoesNotExist:
        return Response(
            {"error": "No game data found for this team. Contact an admin."},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated]) # Ensures only logged-in users can access
def submit_answer(request):
    """
    API endpoint for a team to submit their final decrypted answer.
    """
    user = request.user
    submitted_answer = request.data.get('answer', '').strip().upper()

    if not submitted_answer:
        return Response(
            {"error": "No answer provided."}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        team_data = TeamData.objects.get(team=user)
        
        # Compare the submitted answer to the correct answer in the database
        # (Make sure to store the correct answer in all caps)
        correct_answer = team_data.final_answer.strip().upper()
        
        if submitted_answer == correct_answer:
            # CORRECT!
            team_data.is_complete = True
            team_data.save()
            return Response(
                {"correct": True, "message": "Mission Complete! Timeline saved!"},
                status=status.HTTP_200_OK
            )
        else:
            # INCORRECT!
            return Response(
                {"correct": False, "message": "Access Denied. That is not the correct code."},
                status=status.HTTP_200_OK # 200 OK because the *request* was valid, even if answer was wrong
            )
            
    except TeamData.DoesNotExist:
        return Response(
            {"error": "No game data found for this team. Contact an admin."},
            status=status.HTTP_404_NOT_FOUND
        )


# ==============================================================================
# --- api/urls.py ---
# (Connects your views to URL paths)
# ==============================================================================
from django.urls import path
# from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

# In your project's main urls.py, this file will be included under '/api/'
urlpatterns = [
    # POST to /api/login/ with username/password to get a token
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # POST to /api/token/refresh/ with refresh token to get a new access token
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # GET /api/riddle/ (with auth token)
    path('riddle/', get_riddle, name='get-riddle'),
    
    # POST /api/submit/ (with auth token)
    path('submit/', submit_answer, name='submit-answer'),
]
