import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jkr.settings')
django.setup()

from pages.models import Service

services = Service.objects.all()
print(f"Total services: {services.count()}")
for s in services:
    print(f"ID: {s.id}, Title: {s.title}, Active: {s.is_active}, Order: {s.order}")
