ALX Travel App

A comprehensive travel booking application built with Django REST Framework that enables users to discover accommodations, make bookings, and process payments securely.

🌟 Features
Core Functionality
Property Listings: Hosts can create and manage property listings with detailed descriptions, amenities, and pricing

Booking System: Users can book accommodations with flexible check-in/check-out dates

Review System: Guests can leave ratings and reviews for properties they've stayed in

Payment Processing: Secure payment integration with Chapa payment gateway

Email Notifications: Automated booking confirmation emails using Celery background tasks

User Experience
User authentication and authorization

Property search and filtering (by location, price, availability)

Booking management with status tracking (pending, confirmed, cancelled, completed)

Payment status tracking (pending, completed, failed)

Responsive REST API design

🛠 Technology Stack
Backend
Framework: Django 5.2 + Django REST Framework

Database: MySQL

Task Queue: Celery with RabbitMQ

Caching: Django Celery Results

API Documentation: DRF Yasg (Swagger)

Payment Integration
Payment Gateway: Chapa (Ethiopian payment processor)

Currency: ETB (Ethiopian Birr)

Features: Secure transaction handling, webhook verification

Development Tools
Environment configuration with django-environ

CORS headers for frontend integration

Comprehensive testing framework

📋 Prerequisites
Before running this project, ensure you have the following installed:

Python 3.8+

MySQL 5.7+

RabbitMQ (for Celery)

Git

🚀 Installation & Setup
1. Clone the Repository
bash
git clone <repository-url>
cd alx_travel_app
2. Create Virtual Environment
bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
3. Install Dependencies
bash
pip install -r requirements.txt
4. Environment Configuration
Create a .env file in the project root with the following variables:

env
# Django Settings
SECRET_KEY=your-django-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration
DB_NAME=alx_travel_app
DB_USER=your-mysql-username
DB_PASSWORD=your-mysql-password
DB_HOST=localhost
DB_PORT=3306

# Payment Configuration
CHAPA_SECRET_KEY=your-chapa-secret-key

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com

# Celery Configuration
CELERY_BROKER_URL=amqp://guest:guest@localhost:5672//
5. Database Setup
bash
# Create database in MySQL
mysql -u root -p
CREATE DATABASE alx_travel_app;

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
6. Start Services
Start Django Development Server
bash
python manage.py runserver
Start Celery Worker (in separate terminal)
bash
celery -A alx_travel_app worker --loglevel=info
Start RabbitMQ (if not running)
bash
# On macOS with Homebrew
brew services start rabbitmq

# On Ubuntu
sudo systemctl start rabbitmq-server
📚 API Documentation
Once the server is running, access the API documentation at:

Swagger UI: http://localhost:8000/swagger/

ReDoc: http://localhost:8000/redoc/

Key API Endpoints
Listings
GET /api/listings/ - Get all listings

POST /api/listings/ - Create new listing (authenticated)

GET /api/listings/{id}/ - Get specific listing

PUT /api/listings/{id}/ - Update listing (owner only)

DELETE /api/listings/{id}/ - Delete listing (owner only)

Bookings
GET /api/bookings/ - Get user's bookings

POST /api/bookings/ - Create new booking

GET /api/bookings/{id}/ - Get specific booking

PATCH /api/bookings/{id}/ - Update booking status

Payments
POST /api/payments/initiate/ - Initiate payment

GET /api/payments/verify/ - Verify payment status

GET /api/payments/ - Get payment history

💳 Payment Integration
The app integrates with Chapa payment gateway for processing payments in Ethiopian Birr (ETB).

Payment Flow
User creates a booking

System generates payment record with unique reference

User is redirected to Chapa checkout page

Chapa processes payment and redirects back to app

System verifies payment status via webhook

Booking status is updated accordingly

Testing Payments
Use Chapa test credentials for development:

Test card: 4111 1111 1111 1111

Expiry: Any future date

CVV: Any 3 digits

🎯 Key Models
Listing
Property details (title, description, location, amenities)

Pricing and availability

Host information

Reviews and ratings

Booking
Guest information

Stay dates and duration

Total price calculation

Status tracking

Payment
Transaction details

Payment status

Chapa integration data

Booking relationship

Review
Rating system (1-5 stars)

User comments

One review per user per listing

🔧 Development
Running Tests
bash
python manage.py test
Code Structure
text
alx_travel_app/
├── listings/          # Main app containing core functionality
│   ├── models.py     # Database models
│   ├── serializers.py # API serializers
│   ├── views.py      # API viewsets
│   ├── tasks.py      # Celery background tasks
│   └── admin.py      # Django admin configuration
├── alx_travel_app/   # Project settings
└── requirements.txt  # Python dependencies
Adding New Features
Create model in models.py

Add serializer in serializers.py

Implement views in views.py

Register in admin if needed

Create and run migrations

📧 Email System
The app uses Celery for asynchronous email processing:

Booking confirmation emails

Payment status notifications

Host notifications

Email Templates
Customize email templates in templates/email/ directory.

🔒 Security Features
User authentication and authorization

Secure payment processing

Input validation and sanitization

CORS configuration

CSRF protection

Environment variable management

🚨 Troubleshooting
Common Issues
MySQL Connection Error

Verify database credentials in .env

Ensure MySQL service is running

Celery Worker Not Starting

Check RabbitMQ is running

Verify broker URL in settings

Payment Integration Failing

Confirm Chapa secret key is set

Check network connectivity to Chapa API

Email Not Sending

Verify email configuration in .env

Check email service credentials

🤝 Contributing
Fork the repository

Create a feature branch (git checkout -b feature/amazing-feature)

Commit changes (git commit -m 'Add amazing feature')

Push to branch (git push origin feature/amazing-feature)

Open a Pull Request

📄 License
This project is licensed under the MIT License - see the LICENSE file for details.

👥 Team
This project was developed as part of the ALX Software Engineering program.

📞 Support
For support, email [your-email] or create an issue in the repository.

