
# Henry API

Henry API is a Django-based application that manages scheduling and appointments for **providers** and **clients**. Providers can define their availability, while clients can book, reserve, and confirm appointments. This project uses Django REST Framework for API functionality and JWT for authentication.

---

## Features

- **Providers** can:
  - Submit their availability for appointments.
- **Clients** can:
  - Retrieve available appointment slots (15-minute intervals).
  - Reserve an available appointment slot.
  - Confirm a reservation within 30 minutes.
- Expired reservations become available for other clients.
- Appointments must be made at least 24 hours in advance.

---

## Requirements

- Python 3.9+
- Django 4.2
- Django REST Framework
- Simple JWT for authentication

---

## Setup Instructions

### 1. Clone the Repository

    git clone https://github.com/davkena/henry.git
    cd henry

### 2. Configure Environment Variables
Create a .env file in the project root and add the following:

   

>     DJANGO_SECRET_KEY=placeholder-key-for-local-use
>     DJANGO_DEBUG=True
>     DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost

### 3. Apply Migrations

>     python manage.py makemigrations
>     python manage.py migrate

### 4. Create a Superuser

    

> python manage.py createsuperuser

### 5. Run the Server

    

> python manage.py runserver

# Endpoints
### Authentication
Obtain Token
•	URL: /api/token/
•	Method: POST
•	Body:

>     {
>       "username": "your-username",
>       "password": "your-password"
>     }

Response: access and refresh tokens.
Use the access token for authentication and it should be valid for 5 minutes.

### Testing
Run tests using pytest: 

    pytest

## Tradeoffs
Due to time constraint I was able to only implement authentication on top of the basic functionality as security is quite important.
What should be added to this API would be:

-**Data Validation and Sanitization**: Ensure all inputs are sanitized using Django’s ORM and validation mechanisms, which are SQL-injection safe. Set a maximum size for requests to prevent denial-of-service attacks using overly large payloads.

-**HTTPS Enforcement**:Enforce HTTPS by using a reverse proxy like Nginx or a web server like Gunicorn with SSL certificates. Configure the SECURE_SSL_REDIRECT setting in Django to force HTTPS.

-**Rate Limiting**: Implement rate limiting using **Django REST Framework’s throttle classes** or a third-party library like django-ratelimit

-**Secure Data Handling**: Ensure sensitive data (e.g., client names) is encrypted at rest using Django’s cryptography or database encryption mechanisms. Not exposing sensitive client or provider information in responses unless necessary

-**Prevent Expired Reservation Misuse**: Use Django’s built-in SECURE_* settings to enforce security headers. Install django-cors-headers to handle Cross-Origin Resource Sharing (CORS) securely if the API will be consumed by web apps from different origins

-**Audit Logging**:Log sensitive operations like availability creation, appointment booking, and confirmations. Use Django’s built-in logging framework with proper log rotation.

-**Prevent Enumeration Attacks**: Limit access to provider details and availability data to authenticated users. Return generic error messages instead of specific ones like “No availability exists for the selected date.”
