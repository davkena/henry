import pytest
from django.utils.timezone import now
from datetime import timedelta, date, time
from appointments.models import Provider, Availability, Appointment
from django.contrib.auth.models import User
from rest_framework.test import APIClient

# Create a test user and authenticate the client
def get_authenticated_client():
    # Create a user if it doesn't exist
    user, created = User.objects.get_or_create(username="testuser")
    if created:
        user.set_password("testpassword")
        user.save()
    
    # Obtain a token
    client = APIClient()
    response = client.post('/api/token/', {"username": "testuser", "password": "testpassword"})
    token = response.data['access']
    
    # Set the Authorization header
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    return client

# Helper function to create a provider
def create_provider(name="Dr. Jekyll"):
    return Provider.objects.create(name=name)

# Helper function to create availability
def create_availability(provider, availability_date, start="08:00", end="15:00"):
    return Availability.objects.create(
        provider=provider,
        date=availability_date,
        start_time=start,
        end_time=end
    )

@pytest.mark.django_db
def test_create_provider(client):
    client = get_authenticated_client()  
    response = client.post('/api/providers/', {'name': 'Dr. Jekyll'})
    assert response.status_code == 201
    assert response.data['name'] == 'Dr. Jekyll'

@pytest.mark.django_db
def test_create_availability(client):
    client = get_authenticated_client()  
    provider = create_provider()
    response = client.post('/api/availability/', {
        'provider': provider.id,
        'date': str(date.today() + timedelta(days=2)),
        'start_time': '08:00',
        'end_time': '15:00'
    })
    assert response.status_code == 201
    assert response.data['date'] == str(date.today() + timedelta(days=2))

@pytest.mark.django_db
def test_availability_edge_cases(client):
    client = get_authenticated_client()  
    provider = create_provider()
    # Missing fields
    response = client.post('/api/availability/', {
        'provider': provider.id,
        'date': str(date.today() + timedelta(days=2)),
    })
    assert response.status_code == 400  # Missing start_time and end_time

    # End time before start time
    response = client.post('/api/availability/', {
        'provider': provider.id,
        'date': str(date.today() + timedelta(days=2)),
        'start_time': '15:00',
        'end_time': '08:00'
    })
    assert response.status_code == 400  # Invalid time range

@pytest.mark.django_db
def test_fetch_slots(client):
    client = get_authenticated_client()  
    provider = create_provider()
    create_availability(provider, date.today() + timedelta(days=2))

    response = client.get(f'/api/slots/{provider.id}/?date={date.today() + timedelta(days=2)}')
    assert response.status_code == 200
    assert len(response.data['slots']) > 0  # Slots should be returned

@pytest.mark.django_db
def test_no_slots_available(client):
    client = get_authenticated_client()  
    provider = create_provider()
    response = client.get(f'/api/slots/{provider.id}/?date={date.today() + timedelta(days=2)}')
    assert response.status_code == 404  # No availability exists

@pytest.mark.django_db
def test_create_appointment(client):
    client = get_authenticated_client()  
    provider = create_provider()
    create_availability(provider, date.today() + timedelta(days=2))
    slot_time = time(8, 0)

    response = client.post('/api/appointments/', {
        'provider': provider.id,
        'date': str(date.today() + timedelta(days=2)),
        'time': slot_time.strftime('%H:%M:%S'),
        'client_name': 'John Doe'
    })
    assert response.status_code == 201
    assert response.data['client_name'] == 'John Doe'

@pytest.mark.django_db
def test_create_appointment_edge_cases(client):
    client = get_authenticated_client()  
    provider = create_provider()
    create_availability(provider, date.today() + timedelta(days=2))
    slot_time = time(8, 0)

    # Booking less than 24 hours in advance
    response = client.post('/api/appointments/', {
        'provider': provider.id,
        'date': str(date.today()),
        'time': slot_time.strftime('%H:%M:%S'),
        'client_name': 'John Doe'
    })
    assert response.status_code == 400  # Should not allow same-day booking

    # Booking invalid time slot
    response = client.post('/api/appointments/', {
        'provider': provider.id,
        'date': str(date.today() + timedelta(days=2)),
        'time': '07:00:00',  # Outside available time
        'client_name': 'John Doe'
    })
    assert response.status_code == 400  # Invalid slot

@pytest.mark.django_db
def test_confirm_appointment(client):
    client = get_authenticated_client()  
    provider = create_provider()
    appointment = Appointment.objects.create(
        provider=provider,
        date=date.today() + timedelta(days=2),
        time=time(8, 0),
        client_name='John Doe'
    )

    response = client.put(f'/api/appointments/{appointment.id}/')
    assert response.status_code == 200
    assert response.data['is_confirmed'] is True

@pytest.mark.django_db
def test_confirm_expired_appointment(client):
    client = get_authenticated_client()  
    provider = create_provider()
    appointment = Appointment.objects.create(
        provider=provider,
        date=date.today() + timedelta(days=2),
        time=time(8, 0),
        client_name='John Doe',
        reserved_at=now() - timedelta(minutes=31)  # Reservation expired
    )

    response = client.put(f'/api/appointments/{appointment.id}/')
    assert response.status_code == 400  # Cannot confirm expired reservation