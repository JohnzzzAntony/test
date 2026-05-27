import os
import sys
import django
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jkr.settings')
django.setup()

from django.conf import settings
from core.models import SiteSettings
from accounts.email_notifications import test_email_connection

def debug_email():
    print("--- Resend Email Debugging ---")
    print(f"RESEND_API_KEY: {getattr(settings, 'RESEND_API_KEY', '')[:10]}...")
    print(f"DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
    
    cfg = SiteSettings.objects.first()
    if cfg:
        print(f"SiteSettings Found: {cfg}")
        print(f"enable_email_notifications: {cfg.enable_email_notifications}")
    else:
        print("No SiteSettings record found.")

    print("\nAttempting to send a test email...")
    try:
        # Trigger the connection test using Resend
        result = test_email_connection('johnsantonyjo@gmail.com')
        print(result)
    except Exception as e:
        print(f"Failed! Error: {e}")

if __name__ == "__main__":
    debug_email()
