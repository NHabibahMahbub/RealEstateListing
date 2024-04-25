from django.core.mail import send_mail
from django.conf import settings


def send_inquiry_notification(inquiry):
    owner_email = inquiry.property.owner.email  # Get the property owner's email
    subject = f"New Inquiry for {inquiry.property.title}"
    message = f"""
Hello,

You have received a new inquiry for your property "{inquiry.property.title}".

Details:
- Name: {inquiry.name}
- Email: {inquiry.email}
- Message: {inquiry.message}

You can view the inquiry in your account.

Thank you,
Your Real Estate Platform
"""
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,  # Sender's email
        [owner_email],  # Recipient's email (property owner)
        fail_silently=False,
    )
