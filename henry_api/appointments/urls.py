from django.urls import path
from .views import AvailabilityView, AppointmentSlotsView, AppointmentView
from rest_framework.generics import ListCreateAPIView
from .models import Provider
from .serializers import ProviderSerializer

class ProviderView(ListCreateAPIView):
    queryset = Provider.objects.all()
    serializer_class = ProviderSerializer

urlpatterns = [
    path('providers/', ProviderView.as_view(), name='providers'),
    path('availability/', AvailabilityView.as_view(), name='availability'),
    path('slots/<int:provider_id>/', AppointmentSlotsView.as_view(), name='appointment_slots'),
    path('appointments/', AppointmentView.as_view(), name='appointments'),
    path('appointments/<int:appointment_id>/', AppointmentView.as_view(), name='appointment_detail'),
]