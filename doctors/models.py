from django.db import models
from accounts.models import User


class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='doctor_profile')
    specialization = models.CharField(max_length=255)
    working_days = models.JSONField(default=list)  # eg: ["monday", "wednesday", "friday"]
    start_time = models.TimeField()
    end_time = models.TimeField()
    slot_duration = models.PositiveIntegerField(help_text="Slot duration in minutes")
    consultations_per_day = models.PositiveIntegerField()

    def __str__(self):
        return f"Dr. {self.user.full_name} - {self.specialization}"