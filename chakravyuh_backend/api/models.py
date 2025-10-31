from django.db import models
from django.contrib.auth.models import User

# Defines the Riddle table
class Riddle(models.Model):
    riddle_text = models.TextField(unique=True)
    lead_name = models.CharField(max_length=100, blank=True, null=True, help_text="Internal note for which lead this is")

    def __str__(self):
        return f"Riddle #{self.id}: {self.riddle_text[:50]}..."

# Defines the table linking a Team (User) to their game data
class TeamData(models.Model):
    team = models.OneToOneField(User, on_delete=models.CASCADE, related_name="team_data")
    assigned_riddle = models.ForeignKey(Riddle, on_delete=models.PROTECT)
    final_answer = models.CharField(max_length=255, help_text="The exact, all-caps, decrypted string")
    is_complete = models.BooleanField(default=False)

    def __str__(self):
        return f"Data for Team: {self.team.username}"
