import os
import sys
import django

# Add root to path
sys.path.append(os.getcwd())

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "jkr.settings")
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from django.conf import settings

settings.ALLOWED_HOSTS.append('testserver')

def fetch_admin():
    client = Client()
    # Create superuser if not exists
    username = 'debug_admin'
    password = 'password123'
    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(username, 'admin@example.com', password)
    
    # Login
    client.login(username=username, password=password)
    
    # Fetch admin index
    print("Fetching admin index...")
    response = client.get('/admin/')
    print(f"Status Code: {response.status_code}")
    
    os.makedirs('scratch', exist_ok=True)
    with open('scratch/admin_index_debug.html', 'wb') as f:
        f.write(response.content)
    
    print("Saved admin index to scratch/admin_index_debug.html")
    
    # Check if content is empty or truncated
    if len(response.content) < 500:
        print(f"WARNING: Content seems too short ({len(response.content)} bytes)")
        try:
            print(response.content.decode('utf-8'))
        except:
            print(response.content)

if __name__ == "__main__":
    fetch_admin()
