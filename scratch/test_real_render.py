import os
import sys
import environ
# Bypasses reading .env and .env.local to force fallback to SQLite and Local Memory cache
environ.Env.read_env = lambda *args, **kwargs: None

sys.path.insert(0, os.getcwd())
os.environ['DATABASE_URL'] = ''
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jkr.settings')

import django
django.setup()

from django.test import RequestFactory
from core.views import home

def main():
    factory = RequestFactory()
    request = factory.get('/')
    
    print("Attempting to render homepage on local SQLite...")
    try:
        response = home(request)
        print("Success! Status code:", response.status_code)
    except Exception as e:
        print("\n--- Error rendering homepage ---")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
