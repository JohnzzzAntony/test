
import os
import django
from django.test import Client
from django.contrib.auth import get_user_model
import sys

# Setup Django
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jkr.settings')
django.setup()

def fetch_admin_category():
    User = get_user_model()
    # Create or get the superuser from the previous debug session
    user, created = User.objects.get_or_create(username='debug_admin', defaults={'is_superuser': True, 'is_staff': True})
    if created:
        user.set_password('admin123')
        user.save()
    
    client = Client()
    client.force_login(user)
    
    # Try fetching the category list
    response = client.get('/admin/products/category/')
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        content = response.content.decode('utf-8')
        with open('scratch/category_debug.html', 'w', encoding='utf-8') as f:
            f.write(content)
        print("Successfully saved category page to scratch/category_debug.html")
    else:
        print("Failed to fetch category page")
        if hasattr(response, 'content'):
            print(f"Content: {response.content[:500]}")

if __name__ == "__main__":
    fetch_admin_category()
