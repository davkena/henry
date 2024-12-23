from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Provider, Availability, Appointment
from .serializers import ProviderSerializer, AvailabilitySerializer, AppointmentSerializer
from django.utils.timezone import now
from datetime import timedelta, datetime
from rest_framework.permissions import IsAuthenticated

class AvailabilityView(APIView):
    permission_classes = [IsAuthenticated]

class AvailabilityView(APIView):
    def post(self, request):
        serializer = AvailabilitySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AppointmentSlotsView(APIView):
    def get(self, request, provider_id):
        date = request.query_params.get('date')
        try:
            availability = Availability.objects.get(provider_id=provider_id, date=date)
        except Availability.DoesNotExist:
            return Response({"error": "No availability found"}, status=status.HTTP_404_NOT_FOUND)
        
        # Generate slots
        slots = []
        start_time = datetime.combine(availability.date, availability.start_time)
        end_time = datetime.combine(availability.date, availability.end_time)
        while start_time < end_time:
            slots.append(start_time.time())
            start_time += timedelta(minutes=15)
        
        # Remove reserved or expired slots
        reserved_slots = Appointment.objects.filter(
            provider_id=provider_id,
            date=date,
            is_confirmed=True
        ).values_list('time', flat=True)
        available_slots = [slot for slot in slots if slot not in reserved_slots]
        
        return Response({"slots": available_slots}, status=status.HTTP_200_OK)

class AppointmentView(APIView):
    def post(self, request):
        serializer = AppointmentSerializer(data=request.data)
        if serializer.is_valid():
            if serializer.validated_data['date'] <= (now() + timedelta(days=1)).date():
                return Response({"error": "Appointments must be reserved at least 24 hours in advance."},
                                status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, appointment_id):
        try:
            appointment = Appointment.objects.get(id=appointment_id)
        except Appointment.DoesNotExist:
            return Response({"error": "Appointment not found"}, status=status.HTTP_404_NOT_FOUND)
        
        if appointment.is_expired:
            return Response({"error": "Cannot confirm expired reservation"}, status=status.HTTP_400_BAD_REQUEST)

        appointment.is_confirmed = True
        appointment.save()
        return Response(AppointmentSerializer(appointment).data, status=status.HTTP_200_OK)