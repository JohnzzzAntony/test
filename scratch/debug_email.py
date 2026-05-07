
import os
import django
from django.conf import settings
from django.core.mail import send_mail

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jkr.settings')
django.setup()

from core.models import SiteSettings

def debug_email():
    print("--- Email Debugging ---")
    print(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
    print(f"EMAIL_HOST: {settings.EMAIL_HOST}")
    print(f"EMAIL_PORT: {settings.EMAIL_PORT}")
    print(f"EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
    print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
    print(f"DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
    
    cfg = SiteSettings.objects.first()
    if cfg:
        print(f"SiteSettings Found: {cfg}")
        print(f"enable_email_notifications: {cfg.enable_email_notifications}")
    else:
        print("No SiteSettings record found.")

    print("\nAttempting to send a test email...")
    try:
        # Use a real email address for testing if possible, but for now we just want to see if it errors
        send_mail(
            'Test Email Notification',
            'This is a test email to verify SMTP settings.',
            settings.DEFAULT_FROM_EMAIL,
            ['johnsantonyjo@gmail.com'], # Sending to the user's email from .env
            fail_silently=False,
        )
        print("Success! Email sent without errors.")
    except Exception as e:
        print(f"Failed! Error: {e}")

if __name__ == "__main__":
    debug_email()
