from django.contrib import admin
from .models import Riddle, TeamData
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

# --- Register your models here ---

# This creates an "inline" view for TeamData inside the User admin page
class TeamDataInline(admin.StackedInline):
    model = TeamData
    can_delete = False
    verbose_name_plural = 'Team Game Data'
    # This prevents you from adding more than one game data object to a user
    max_num = 1 
    min_num = 1

# Define a new User admin
class UserAdmin(BaseUserAdmin):
    inlines = (TeamDataInline,)

# Re-register User admin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# Also register Riddle so you can add/edit riddles
admin.site.register(Riddle)
