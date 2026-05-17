
import os
import django
from django.test import Client
from django.contrib.auth import get_user_model
import sys

# Setup Django
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jkr.settings')
django.setup()

def test_all_endpoints():
    User = get_user_model()
    user, created = User.objects.get_or_create(username='debug_admin', defaults={'is_superuser': True, 'is_staff': True})
    if created:
        user.set_password('admin123')
        user.save()
    
    client = Client()
    client.force_login(user)
    
    endpoints = [
        '/admin/',
        '/admin/products/product/',
        '/admin/products/category/',
        '/admin/products/brand/',
        '/admin/products/collection/',
        '/admin/orders/customerorder/',
        '/admin/orders/quoteenquiry/',
        '/admin/orders/salesorder/',
        '/admin/accounts/customuser/',
        '/admin/blog/post/',
        '/admin/pages/staticpage/',
    ]
    
    for url in endpoints:
        print(f"Fetching {url}...")
        try:
            response = client.get(url)
            print(f"Result for {url}: {response.status_code}")
            if response.status_code != 200:
                print(f"Error Content (first 1000 chars):")
                if hasattr(response, 'content'):
                    print(response.content[:1000].decode('utf-8', errors='ignore'))
        except Exception as e:
            print(f"Exception for {url}: {e}")
            import traceback
            traceback.print_exc()
        print("-" * 50)

if __name__ == "__main__":
    test_all_endpoints()
