from rest_framework import serializers
from .models import Provider, Availability, Appointment
from datetime import datetime, timedelta
from django.utils.timezone import now

class ProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Provider
        fields = '__all__'

class AvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Availability
        fields = '__all__'

    def validate(self, data):
        if data['end_time'] <= data['start_time']:
            raise serializers.ValidationError("End time must be after start time.")
        return data

class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = '__all__'

    def validate(self, data):
        # Check for 24-hour advance booking
        if data['date'] <= (now().date() + timedelta(days=1)):
            raise serializers.ValidationError("Appointments must be reserved at least 24 hours in advance.")
        
        # Check if the time slot is within provider's availability
        availability = Availability.objects.filter(
            provider=data['provider'],
            date=data['date']
        ).first()
        if not availability:
            raise serializers.ValidationError("No availability exists for the selected date.")
        
        slot_time = datetime.combine(data['date'], data['time'])
        start_time = datetime.combine(data['date'], availability.start_time)
        end_time = datetime.combine(data['date'], availability.end_time)
        if slot_time < start_time or slot_time >= end_time:
            raise serializers.ValidationError("Invalid time slot.")

        return data