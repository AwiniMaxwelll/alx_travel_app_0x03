from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def send_booking_confirmation_email(booking_id, user_email):
    """
    Send booking confirmation email as a Celery task
    """
    try:
        subject = 'Booking Confirmation - ALX Travel App'
        message = f'Your booking #{booking_id} has been confirmed. Thank you!'
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [user_email]
        
        send_mail(subject, message, from_email, recipient_list)
        return f"Email sent to {user_email}"
    except Exception as e:
        return f"Error sending email: {str(e)}"
