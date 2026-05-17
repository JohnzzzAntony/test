import os
import django
from django.conf import settings
from django.template import Context, RequestContext, Template
from django.test import RequestFactory

# Configure minimal Django
if not settings.configured:
    settings.configure(
        DEBUG=True,
        DATABASES={'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': ':memory:'}},
        INSTALLED_APPS=['django.contrib.contenttypes', 'django.contrib.auth'],
        TEMPLATES=[{
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'APP_DIRS': True,
            'OPTIONS': {
                'context_processors': [
                    'django.template.context_processors.debug',
                    'django.template.context_processors.request',
                    'django.contrib.auth.context_processors.auth',
                    'django.contrib.messages.context_processors.messages',
                ],
            },
        }],
    )
    django.setup()

# Apply monkeypatch
import sys
sys.path.append(os.getcwd())
import core.monkeypatch_django

def test_render():
    factory = RequestFactory()
    request = factory.get('/admin/')
    
    # Simulate what Django does in templates
    t = Template("Hello {{ name }}")
    c = RequestContext(request, {'name': 'World'})
    
    print("Initial context created")
    
    # Django often copies context in include tags or other places
    try:
        import copy
        c2 = copy.copy(c)
        print(f"Context copied successfully: {type(c2)}")
        
        # Test if it still works
        res = t.render(c2)
        print(f"Render result: {res}")
        
    except Exception as e:
        print(f"Error during context copy/render: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_render()
