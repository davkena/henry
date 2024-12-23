from django.db import models
from django.utils.timezone import now
from datetime import timedelta

class Provider(models.Model):
    name = models.CharField(max_length=255)

class Availability(models.Model):
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, related_name='availabilities')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()

class Appointment(models.Model):
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, related_name='appointments')
    date = models.DateField()
    time = models.TimeField()
    client_name = models.CharField(max_length=255, null=True, blank=True)
    reserved_at = models.DateTimeField(default=now)
    is_confirmed = models.BooleanField(default=False)

    @property
    def is_expired(self):
        return not self.is_confirmed and now() > self.reserved_at + timedelta(minutes=30)