from django.db import models
from doctors.models import Doctor
from accounts.models import User


class Appointment(models.Model):
    STATUS_CHOICES = (
        ('booked', 'Booked'),
        ('cancelled', 'Cancelled'),
    )

    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='appointments')
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='booked')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('doctor', 'date', 'start_time')

    def __str__(self):
        return f"{self.customer.full_name} with Dr. {self.doctor.user.full_name} on {self.date} at {self.start_time}"