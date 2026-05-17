import os
import django
from django.conf import settings
from django.apps import apps

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jkr.settings')
django.setup()

print("INSTALLED_APPS:", settings.INSTALLED_APPS)
print("App Labels:", [app.label for app in apps.get_app_configs()])
