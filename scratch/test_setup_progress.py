import os
import sys
import time

print("1. Setting up sys.path...")
sys.path.insert(0, os.getcwd())

print("2. Setting DJANGO_SETTINGS_MODULE...")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jkr.settings')

print("3. Loading settings...")
from django.conf import settings
print("   DEBUG:", getattr(settings, 'DEBUG', None))
print("   DATABASES Engine:", settings.DATABASES['default']['ENGINE'] if 'default' in settings.DATABASES else 'None')

print("4. Importing django...")
import django

print("5. Calling django.setup()...")
start_time = time.time()
django.setup()
print(f"   django.setup() completed in {time.time() - start_time:.2f} seconds!")

print("6. Connecting to database...")
from django.db import connection
try:
    start_time = time.time()
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
    print(f"   Database query SELECT 1 completed in {time.time() - start_time:.2f} seconds!")
except Exception as e:
    print(f"   Database connection failed: {e}")
