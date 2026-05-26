import os
import sys
import django

sys.path.insert(0, os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jkr.settings')

django.setup()

from django.test import RequestFactory, override_settings
from django.contrib.messages.storage.fallback import FallbackStorage
from core.views import home
from django.template.base import Template

# Open trace file
log_file = open('scratch/trace.log', 'w', encoding='utf-8')

# Monkeypatch Template.render to print template info
original_render = Template.render

render_depth = 0
def patched_render(self, context, *args, **kwargs):
    global render_depth
    name = getattr(self, 'name', None) or getattr(self, 'origin', None)
    indent = "  " * render_depth
    log_file.write(f"{indent}-> Rendering template: {name}\n")
    log_file.flush()
    render_depth += 1
    try:
        res = original_render(self, context, *args, **kwargs)
        return res
    finally:
        render_depth -= 1

Template.render = patched_render

class DummySession(dict):
    def save(self):
        pass

@override_settings(CACHES={
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "jkr-test-override",
    }
})
def main():
    factory = RequestFactory()
    request = factory.get('/')
    request.session = DummySession()
    request._messages = FallbackStorage(request)
    
    print("Starting homepage render tracing...")
    try:
        response = home(request)
        print("Done! Status:", response.status_code)
    except RecursionError:
        print("\nHIT RECURSION ERROR!")
        import traceback
        traceback.print_exc(file=log_file)
    except Exception as e:
        print("\nError:", e)
    finally:
        log_file.close()

if __name__ == "__main__":
    main()
