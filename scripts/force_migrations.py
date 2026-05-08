
import os
import sys
import django
from django.core.management import call_command

def force():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jkr.settings')
    django.setup()
    
    print("Apps registered:", [app.label for app in django.apps.apps.get_app_configs()])
    
    try:
        print("Making migrations for accounts...")
        call_command('makemigrations', 'accounts')
    except Exception as e:
        print(f"Failed accounts: {e}")

    try:
        print("Making migrations for pages...")
        call_command('makemigrations', 'pages')
    except Exception as e:
        print(f"Failed pages: {e}")

if __name__ == "__main__":
    force()
