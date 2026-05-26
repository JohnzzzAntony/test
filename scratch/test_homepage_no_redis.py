import os
import sys
import django

sys.path.insert(0, os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jkr.settings')

django.setup()

from django.test import RequestFactory, override_settings
from django.contrib.messages.storage.fallback import FallbackStorage
from core.views import home

class DummySession(dict):
    def save(self):
        pass

# Override cache setting to run locally without Redis connection
@override_settings(CACHES={
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "jkr-test-override",
    }
})
def main():
    factory = RequestFactory()
    request = factory.get('/')
    
    # Mock session
    request.session = DummySession()
    
    # Mock messages storage
    request._messages = FallbackStorage(request)
    
    print("Attempting to render homepage on database with mocked session (LocMemCache)...")
    try:
        response = home(request)
        print("Success! Status code:", response.status_code)
        if response.status_code == 500:
            print("Response content:", response.content[:1000])
    except Exception as e:
        print("\n--- Error rendering homepage ---")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
