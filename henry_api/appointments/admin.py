from django.contrib import admin
from .models import Provider, Availability, Appointment

@admin.register(Provider)
class ProviderAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

@admin.register(Availability)
class AvailabilityAdmin(admin.ModelAdmin):
    list_display = ('id', 'provider', 'date', 'start_time', 'end_time')
    list_filter = ('date',)

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'provider', 'date', 'time', 'client_name', 'is_confirmed')
    list_filter = ('date', 'is_confirmed')
    search_fields = ('client_name',)