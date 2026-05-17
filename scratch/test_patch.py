import os
import django
from django.conf import settings

# Configure minimal settings
if not settings.configured:
    settings.configure(
        DEBUG=True,
        DATABASES={'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': ':memory:'}},
        INSTALLED_APPS=['django.contrib.contenttypes', 'django.contrib.auth'],
        TEMPLATES=[{
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [],
            'APP_DIRS': True,
        }]
    )
    django.setup()

from django.template import Context, RequestContext
from copy import copy
import core.monkeypatch_django

print("Testing Context copy...")
c = Context({'a': 1})
try:
    c2 = copy(c)
    print("Context copy successful.")
    print(f"c2.dicts: {c2.dicts}")
except Exception as e:
    print(f"Context copy failed: {e}")
    import traceback
    traceback.print_exc()

print("\nTesting RequestContext copy...")
from django.test import RequestFactory
rf = RequestFactory()
request = rf.get('/')
rc = RequestContext(request, {'b': 2})
try:
    rc2 = copy(rc)
    print("RequestContext copy successful.")
    print(f"rc2.dicts: {rc2.dicts}")
except Exception as e:
    print(f"RequestContext copy failed: {e}")
    import traceback
    traceback.print_exc()
