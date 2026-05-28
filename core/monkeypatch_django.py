import django.template.context
from copy import copy

def patched_copy(self):
    # Use object.__new__ to create a new instance of the same class without calling __init__
    duplicate = object.__new__(self.__class__)
    # Copy all dictionary attributes
    duplicate.__dict__.update(self.__dict__)
    # Create a shallow copy of the dicts list
    duplicate.dicts = self.dicts[:]
    # Create a copy of the render_context if it exists
    if hasattr(self, 'render_context'):
        duplicate.render_context = copy(self.render_context)
    return duplicate

# Apply the patches to all context classes in django.template.context
django.template.context.BaseContext.__copy__ = patched_copy
django.template.context.Context.__copy__ = patched_copy
django.template.context.RequestContext.__copy__ = patched_copy
django.template.context.RenderContext.__copy__ = patched_copy

print("Improved Django Context monkeypatch applied (Python 3.14 compatible).")

import django.conf
# Disable Django 5/6 check for mutually exclusive STORAGES vs STATICFILES_STORAGE/DEFAULT_FILE_STORAGE
original_settings_init = django.conf.Settings.__init__

def patched_settings_init(self, settings_module):
    original_is_overridden = self.is_overridden
    
    def temp_is_overridden(setting):
        if setting in ("STATICFILES_STORAGE", "DEFAULT_FILE_STORAGE"):
            return False
        return original_is_overridden(setting)
        
    self.is_overridden = temp_is_overridden
    try:
        original_settings_init(self, settings_module)
    finally:
        if hasattr(self, 'is_overridden'):
            del self.is_overridden

    # Ensure these are populated on django.conf.settings
    if hasattr(self, 'STORAGES'):
        if 'staticfiles' in self.STORAGES:
            self.STATICFILES_STORAGE = self.STORAGES['staticfiles']['BACKEND']
        if 'default' in self.STORAGES:
            self.DEFAULT_FILE_STORAGE = self.STORAGES['default']['BACKEND']

django.conf.Settings.__init__ = patched_settings_init
